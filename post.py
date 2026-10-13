import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

API = "https://graph.threads.net/v1.0"
TOKEN = os.environ["THREADS_TOKEN"]
MAX_PER_RUN = 3


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params)
    url = f"{API}/{path}"
    req = urllib.request.Request(url + ("?" + data if method == "GET" else ""),
                                 data=None if method == "GET" else data.encode(), method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


posts = json.load(open("posts.json"))
now = datetime.now(timezone.utc)
due = [p for p in posts if p["status"] == "pending" and datetime.fromisoformat(p["at"]) <= now]
due.sort(key=lambda p: p["at"])
if not due:
    print("nothing due")
    sys.exit(0)

uid = call("GET", "me", fields="id")["id"]
for p in due[:MAX_PER_RUN]:
    cid = call("POST", f"{uid}/threads", media_type="TEXT", text=p["text"])["id"]
    time.sleep(5)
    p["threads_id"] = call("POST", f"{uid}/threads_publish", creation_id=cid)["id"]
    p["status"] = "posted"
    p["posted_at"] = datetime.now(timezone.utc).isoformat()
    json.dump(posts, open("posts.json", "w"), indent=1, ensure_ascii=False)
    print("posted", p["id"])
