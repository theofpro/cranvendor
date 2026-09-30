import json, subprocess, urllib.request

API = 'https://api.osv.dev/v1/query'


def tag_exists(repo, tag):
    r = subprocess.run(['git', 'ls-remote', '--tags', repo, f'refs/tags/{tag}'],
                       capture_output=True, text=True, timeout=120)
    return bool(r.stdout.strip())


def _query(package, version):
    body = json.dumps({'package': package, 'version': version}).encode()
    req = urllib.request.Request(API, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'curl/8'})
    vulns = json.load(urllib.request.urlopen(req, timeout=60)).get('vulns', [])
    ids = set()
    for v in vulns:
        cves = [a for a in v.get('aliases', []) if a.startswith('CVE-')]
        ids.add(v['id'] if v['id'].startswith('CVE-') or not cves else cves[0])
    return sorted(ids)


def osv_git(repo, tag):
    # None = we couldn't check (missing tag), [] = checked, nothing known
    if not tag_exists(repo, tag):
        return None
    return _query({'name': repo, 'ecosystem': 'GIT'}, tag)


def osv_npm(name, version):
    return _query({'name': name, 'ecosystem': 'npm'}, version)
