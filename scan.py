import csv
import json
import os
import re
import sys
import tarfile
import tempfile
import urllib.request

from signatures import JS_BANNER, LIBS

CRAN = 'https://cran.r-project.org/src/contrib'
KEEP = ('src/', 'inst/', 'tools/', 'configure', 'NEWS')
UA = {'User-Agent': 'curl/8'}  # cranlogs gives 403 to urllib's default


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=120).read()


def current_versions():
    txt = get(CRAN + '/PACKAGES').decode()
    return dict(re.findall(r'^Package: (\S+)\nVersion: (\S+)', txt, re.M))


def top_packages(n, versions):
    names = list(versions)
    counts = {}
    for i in range(0, len(names), 150):
        url = ('https://cranlogs.r-pkg.org/downloads/total/last-month/'
               + ','.join(names[i:i + 150]))
        for r in json.loads(get(url)):
            counts[r['package']] = r['downloads']
    return sorted(counts, key=counts.get, reverse=True)[:n]


def fetch(pkg, ver, dest, archive=False):
    if archive:
        url = f'{CRAN}/Archive/{pkg}/{pkg}_{ver}.tar.gz'
    else:
        url = f'{CRAN}/{pkg}_{ver}.tar.gz'
    path = os.path.join(dest, 'pkg.tar.gz')
    with open(path, 'wb') as f:
        f.write(get(url))
    with tarfile.open(path) as t:
        members = [m for m in t.getmembers()
                   if m.isfile() and m.name.split('/', 1)[-1].startswith(KEEP)]
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
    # "Update libcmark-gfm to 0.29.0.gfm.13", "ReadStat 1.1.5", ...
    rx = rf'{lib}\S*\s+(?:to\s+|version\s+|v)?(\d+\.\d+(?:\.\d+)?)'
    for name in ('NEWS.md', 'NEWS', 'inst/NEWS'):
        m = re.search(rx, read(os.path.join(root, name)), re.I)
        if m:
            return m.group(1), name
    return '', ''


def find_version(root, lib, text):
    rx = LIBS[lib][1]
    if rx:
        m = re.search(rx, text, re.S)
        if m:
            g = [x for x in m.groups() if x]
            if all(x.isdigit() for x in g):
                return '.'.join(g), 'macro'
            return g[-1], 'macro'
    if lib == 'libxls':
        for dp, _, files in os.walk(os.path.join(root, 'src')):
            if 'config.h' in files:
                txt = read(os.path.join(dp, 'config.h'))
                m = re.search(r'PACKAGE_STRING\s+"libxls ([^"]+)"', txt)
                if m:
                    return m.group(1), 'config.h'
    return news_version(root, lib)


def scan_c(root):
    found = {}
    for sub in ('src', 'inst/include'):
        for dp, _, files in os.walk(os.path.join(root, sub)):
            for f in files:
                rel = os.path.relpath(os.path.join(dp, f), root)
                for lib, sig in LIBS.items():
                    if lib in found and found[lib][0]:
                        continue
                    if not re.search(sig[0], rel):
                        continue
                    text = read(os.path.join(dp, f))
                    ver, how = find_version(root, lib, text)
                    found[lib] = (ver, rel, how)
    return [(lib, v, rel, how) for lib, (v, rel, how) in found.items()]


def scan_js(root):
    out = {}
    for dp, _, files in os.walk(os.path.join(root, 'inst')):
        for f in files:
            if not f.endswith('.js'):
                continue
            m = re.search(JS_BANNER, read(os.path.join(dp, f), 1500))
            if m:
                # keep the .js suffix, npm uses it (plotly.js, pym.js)
                key = (m.group(1).lower(), m.group(2))
                out.setdefault(key, os.path.relpath(os.path.join(dp, f), root))
    return [(name, v, rel, 'banner') for (name, v), rel in out.items()]


def scan_pkg(pkg, ver, archive=False):
    with tempfile.TemporaryDirectory() as d:
        root = fetch(pkg, ver, d, archive)
        rows = [('c',) + r for r in scan_c(root)]
        rows += [('js',) + r for r in scan_js(root)]
        return rows


def main(args):
    versions = current_versions()
    if args[0] == '--top':
        pkgs = top_packages(int(args[1]), versions)
    else:
        pkgs = args
    w = csv.writer(sys.stdout)
    w.writerow(['package', 'version', 'kind', 'library', 'lib_version',
                'path', 'version_from'])
    for p in pkgs:
        try:
            for row in scan_pkg(p, versions[p]):
                w.writerow([p, versions[p]] + list(row))
        except Exception as e:
            print(f'{p}: failed ({e})', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
