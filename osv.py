import json
import subprocess
import urllib.request

API = 'https://api.osv.dev/v1/query'


def tag_exists(repo, tag):
    r = subprocess.run(['git', 'ls-remote', '--tags', repo,
                        f'refs/tags/{tag}'],
                       capture_output=True, text=True, timeout=120)
    return bool(r.stdout.strip())


def query(package, version):
    body = json.dumps({'package': package, 'version': version}).encode()
    req = urllib.request.Request(API, data=body, headers={
        'Content-Type': 'application/json', 'User-Agent': 'curl/8'})
    vulns = json.load(urllib.request.urlopen(req, timeout=60))
    ids = set()
    for v in vulns.get('vulns', []):
        cves = [a for a in v.get('aliases', []) if a.startswith('CVE-')]
        if v['id'].startswith('CVE-') or not cves:
            ids.add(v['id'])
        else:
            ids.add(cves[0])
    return sorted(ids)


def osv_git(repo, tag):
    # None means the tag doesn't exist upstream, so we can't say anything
    # TODO: try the nearest lower tag, then NVD
    if not tag_exists(repo, tag):
        return None
    return query({'name': repo, 'ecosystem': 'GIT'}, tag)


def osv_npm(name, version):
    return query({'name': name, 'ecosystem': 'npm'}, version)
