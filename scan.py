import os, re, sys, csv, json, tarfile, tempfile, urllib.request
from signatures import LIBS, JS_BANNER

CRAN = 'https://cran.r-project.org/src/contrib'
KEEP = ('src/', 'inst/', 'tools/', 'configure', 'NEWS')
UA = {'User-Agent': 'curl/8'}  # cranlogs answers 403 to the python default


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def current_versions():
    txt = get(CRAN + '/PACKAGES').decode()
    return dict(re.findall(r'^Package: (\S+)\nVersion: (\S+)', txt, re.M))


def top_packages(n, versions):
    names, counts = list(versions), {}
    for i in range(0, len(names), 150):
        res = json.loads(get('https://cranlogs.r-pkg.org/downloads/total/last-month/' + ','.join(names[i:i+150])))
        for r in res:
            counts[r['package']] = r['downloads']
    return sorted(counts, key=counts.get, reverse=True)[:n]


def fetch(pkg, ver, dest, archive=False):
    url = f'{CRAN}/Archive/{pkg}/{pkg}_{ver}.tar.gz' if archive else f'{CRAN}/{pkg}_{ver}.tar.gz'
    path = os.path.join(dest, 'pkg.tar.gz')
    with open(path, 'wb') as f:
        f.write(get(url))
    with tarfile.open(path) as t:
        # only the folders we look at, keeps disk usage small
        members = [m for m in t.getmembers() if m.isfile() and m.name.split('/', 1)[-1].startswith(KEEP)]
        t.extractall(dest, members=members, filter='data')
    os.remove(path)
    return os.path.join(dest, pkg)


def read(path, n=400000):
    try:
        with open(path, errors='replace') as f:
            return f.read(n)
    except OSError:
        return ''


def news_version(root, lib):
    # e.g. "Update libcmark-gfm to 0.29.0.gfm.13", "ReadStat 1.1.5"
    for name in ('NEWS.md', 'NEWS', 'inst/NEWS'):
        m = re.search(rf'{lib}\S*\s+(?:to\s+|version\s+|v)?(\d+\.\d+(?:\.\d+)?)', read(os.path.join(root, name)), re.I)
        if m:
            return m.group(1), name
    return '', ''


def find_version(root, lib, text):
    rx = LIBS[lib][1]
    if rx:
        m = re.search(rx, text, re.S)
        if m:
            g = [x for x in m.groups() if x]
            return ('.'.join(g) if all(x.isdigit() for x in g) else g[-1]), 'macro'
    if lib == 'libxls':
        for dp, _, fn in os.walk(os.path.join(root, 'src')):
            if 'config.h' in fn:
                m = re.search(r'PACKAGE_STRING\s+"libxls ([^"]+)"', read(os.path.join(dp, 'config.h')))
                if m:
                    return m.group(1), 'config.h'
    v, src = news_version(root, lib)
    return v, src


def scan_c(root):
    found = {}
    for sub in ('src', 'inst/include'):
        for dp, _, fn in os.walk(os.path.join(root, sub)):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), root)
                for lib, (path_rx, *_rest) in LIBS.items():
                    if lib in found and found[lib][0] or not re.search(path_rx, rel):
                        continue
                    ver, how = find_version(root, lib, read(os.path.join(dp, f)))
                    found[lib] = (ver, rel, how)
    return [(lib, v, rel, how) for lib, (v, rel, how) in found.items()]


def scan_js(root):
    out = {}
    for dp, _, fn in os.walk(os.path.join(root, 'inst')):
        for f in fn:
            if f.endswith('.js'):
                m = re.search(JS_BANNER, read(os.path.join(dp, f), 1500))
                if m:
                    name = m.group(1).lower().removesuffix('.js')
                    out.setdefault((name, m.group(2)), os.path.relpath(os.path.join(dp, f), root))
    return [(n, v, rel, 'banner') for (n, v), rel in out.items()]


def scan_pkg(pkg, ver, archive=False):
    with tempfile.TemporaryDirectory() as d:
        root = fetch(pkg, ver, d, archive)
        return [('c', *r) for r in scan_c(root)] + [('js', *r) for r in scan_js(root)]


if __name__ == '__main__':
    versions = current_versions()
    if sys.argv[1] == '--top':
        pkgs = top_packages(int(sys.argv[2]), versions)
    else:
        pkgs = sys.argv[1:]
    w = csv.writer(sys.stdout)
    w.writerow(['package', 'version', 'kind', 'library', 'lib_version', 'path', 'version_from'])
    for p in pkgs:
        try:
            for row in scan_pkg(p, versions[p]):
                w.writerow([p, versions[p], *row])
        except Exception as e:
            print(f'{p}: failed ({e})', file=sys.stderr)
