# Would the scanner have caught the RSEC advisories that come from bundled code?
# For each one: take the last affected version from the CRAN archive, scan it,
# ask OSV about what we found and compare with the CVEs listed in the advisory.
import io, re, json, zipfile
from scan import get, scan_pkg, CRAN
from signatures import LIBS
from osv import osv_git, osv_npm

ADVISORIES = ['RSEC-2023-0', 'RSEC-2023-1', 'RSEC-2023-2', 'RSEC-2023-3', 'RSEC-2023-4', 'RSEC-2023-5',
              'RSEC-2023-6', 'RSEC-2023-7', 'RSEC-2023-8', 'RSEC-2025-1', 'RSEC-2026-0']
# which bundled library each advisory is about
LIB = {'RSEC-2023-0': 'libxls', 'RSEC-2023-1': 'libxls', 'RSEC-2023-2': 'libxls', 'RSEC-2023-3': 'yajl',
       'RSEC-2023-4': 'igraph', 'RSEC-2023-5': 'ReadStat', 'RSEC-2023-6': 'cmark-gfm', 'RSEC-2023-7': 'cmark-gfm',
       'RSEC-2023-8': 'cmark-gfm', 'RSEC-2025-1': 'plotly.js', 'RSEC-2026-0': 'pym.js'}


def vkey(v):
    return [int(x) for x in re.split(r'[.-]', v) if x.isdigit()]


def last_affected(pkg, events):
    html = get(f'{CRAN}/Archive/{pkg}/').decode()
    vs = sorted(set(re.findall(rf'href="{re.escape(pkg)}_([^"]+)\.tar\.gz"', html)), key=vkey)
    lo, hi = events.get('introduced', '0'), events.get('fixed')
    vs = [v for v in vs if vkey(v) >= vkey(lo) and (not hi or vkey(v) < vkey(hi))]
    return vs[-1]


def main():
    z = zipfile.ZipFile(io.BytesIO(get('https://osv-vulnerabilities.storage.googleapis.com/CRAN/all.zip')))
    print('| Advisory | Package | Library | Version found | CVEs matched |')
    print('|---|---|---|---|---|')
    for adv in ADVISORIES:
        d = json.loads(z.read(adv + '.json'))
        aff = d['affected'][0]
        pkg = aff['package']['name']
        events = {k: v for e in aff['ranges'][0]['events'] for k, v in e.items()}
        cves = set(re.findall(r'CVE-\d+-\d+', json.dumps(d)))
        ver = last_affected(pkg, events)
        lib = LIB[adv]
        rows = [r for r in scan_pkg(pkg, ver, archive=True) if r[1] == lib]
        if not rows:
            print(f'| {adv} | {pkg} {ver} | {lib} | not detected | 0 of {len(cves)} |')
            continue
        kind, _, libver, _, _ = rows[0]
        ids, note = [], ''
        if not libver:
            note = 'not found'
        elif kind == 'js':
            ids = osv_npm(lib, libver)
        else:
            repo, fmt = LIBS[lib][2], LIBS[lib][3]
            ids = osv_git(repo, fmt.format(libver))
            if ids is None:
                ids, note = [], ' (no such upstream tag)'
        hit = cves & set(ids)
        shown = libver + note if libver else note
        print(f'| {adv} | {pkg} {ver} | {lib} | {shown} | {len(hit)} of {len(cves)} |')


if __name__ == '__main__':
    main()
