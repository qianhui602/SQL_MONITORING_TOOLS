import base64, json, urllib.request, subprocess

REPO = "qianhui602/SQL_MONITORING_TOOLS"
BRANCH = "master"
remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
TOKEN = remote.split("://")[1].split("@")[0].split(":", 1)[1]

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Python",
}

def upload(local_path, github_path, message):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{github_path}?ref={BRANCH}", headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req)
        sha = json.loads(resp.read())["sha"]
    except: sha = None
    payload = {"message": message, "content": content, "branch": BRANCH}
    if sha: payload["sha"] = sha
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/contents/{github_path}",
        data=data, headers={**HEADERS, "Content-Type": "application/json"}, method="PUT")
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"OK: {github_path} -> {result['commit']['sha'][:8]}")

files = [
    ("frontend/src/views/Dashboard.vue", "feat: Dashboard自动刷新频率可配置+统计卡片去AI化"),
]
for local, msg in files:
    upload(local, local, msg)
print("All done!")
