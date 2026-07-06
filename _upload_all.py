import base64, json, urllib.request, subprocess

REPO = "qianhui602/SQL_MONITORING_TOOLS"
BRANCH = "master"
remote = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
TOKEN = remote.split("://")[1].split("@")[0].split(":", 1)[1]
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "Python"}

def upload(local_path, github_path, message):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{github_path}?ref={BRANCH}", headers=HEADERS)
    try:
        sha = json.loads(urllib.request.urlopen(req).read())["sha"]
    except: sha = None
    payload = {"message": message, "content": content, "branch": BRANCH}
    if sha: payload["sha"] = sha
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{github_path}",
        data=data, headers={**HEADERS, "Content-Type": "application/json"}, method="PUT")
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"OK: {github_path} -> {result['commit']['sha'][:8]}")

files = [
    ("frontend/src/views/Dashboard.vue", "feat: Dashboard自动刷新频率可配置+统计卡片去AI化"),
    ("frontend/src/views/Login.vue", "style: Login页面去AI化(移除渐变背景/大圆角)"),
    ("frontend/src/views/Report.vue", "style: Report页面去AI化(移除渐变/大圆角/悬浮效果)"),
    ("frontend/src/views/Settings.vue", "style: Settings页面去AI化"),
    ("frontend/src/views/Blocking.vue", "style: Blocking页面去AI化"),
    ("frontend/src/views/Users.vue", "style: Users页面去AI化"),
    ("frontend/src/views/AlertRules.vue", "style: AlertRules页面去AI化"),
    ("frontend/src/views/Instances.vue", "style: Instances页面去AI化"),
    ("frontend/src/views/Deadlocks.vue", "style: Deadlocks页面去AI化"),
    ("frontend/src/components/Layout.vue", "style: Layout组件去AI化(头像/通知下拉框)"),
]
for local, msg in files:
    upload(local, local, msg)
print("All done!")
