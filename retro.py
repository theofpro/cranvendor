# Run the scanner on the last affected version of each RSEC advisory
# caused by bundled code and check if the advisory's CVEs come back.
import io
import json
import re
import zipfile

from osv import osv_git, osv_npm
from scan import CRAN, get, scan_pkg
from signatures import LIBS

OSV_DUMP = 'https://osv-vulnerabilities.storage.googleapis.com/CRAN/all.zip'

# advisory -> bundled library it is about
CASES = {
    'RSEC-2023-0': 'libxls',
    'RSEC-2023-1': 'libxls',
    'RSEC-2023-2': 'libxls',
    'RSEC-2023-3': 'yajl',
    'RSEC-2023-4': 'igraph',
    'RSEC-2023-5': 'ReadStat',
    'RSEC-2023-6': 'cmark-gfm',
    'RSEC-2023-7': 'cmark-gfm',
    'RSEC-2023-8': 'cmark-gfm',
    'RSEC-2025-1': 'plotly.js',
    'RSEC-2026-0': 'pym.js',
}


def vkey(v):
    return [int(x) for x in re.split(r'[.-]', v) if x.isdigit()]


def last_affected(pkg, events):
    html = get(f'{CRAN}/Archive/{pkg}/').decode()
    rx = rf'href="{re.escape(pkg)}_([^"]+)\.tar\.gz"'
    vs = sorted(set(re.findall(rx, html)), key=vkey)
    lo, hi = events.get('introduced', '0'), events.get('fixed')
    vs = [v for v in vs
          if vkey(v) >= vkey(lo) and (not hi or vkey(v) < vkey(hi))]
    return vs[-1]


def check(adv, lib, z):
    d = json.loads(z.read(adv + '.json'))
    aff = d['affected'][0]
    pkg = aff['package']['name']
    events = {k: v for e in aff['ranges'][0]['events'] for k, v in e.items()}
    cves = set(re.findall(r'CVE-\d+-\d+', json.dumps(d)))
    ver = last_affected(pkg, events)
    rows = [r for r in scan_pkg(pkg, ver, archive=True) if r[1] == lib]
    if not rows:
        return pkg, ver, 'not detected', 0, len(cves)
    kind, libver = rows[0][0], rows[0][2]
    if not libver:
        return pkg, ver, 'not found', 0, len(cves)
    if kind == 'js':
        ids = osv_npm(lib, libver)
    else:
        repo, fmt = LIBS[lib][2], LIBS[lib][3]
        ids = osv_git(repo, fmt.format(libver))
        if ids is None:
            return pkg, ver, libver + ' (no such tag)', 0, len(cves)
    return pkg, ver, libver, len(cves & set(ids)), len(cves)


def main():
    z = zipfile.ZipFile(io.BytesIO(get(OSV_DUMP)))
    print('| Advisory | Package | Library | Version found | CVEs matched |')
    print('|---|---|---|---|---|')
    for adv, lib in CASES.items():
        pkg, ver, found, hit, total = check(adv, lib, z)
        print(f'| {adv} | {pkg} {ver} | {lib} | {found} | {hit}/{total} |')


if __name__ == '__main__':
    main()
