#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar for the profile owner."""
import json, re, urllib.request
from datetime import date, timedelta
from pathlib import Path
user="codewithutkarsh12"; end=date.today(); start=end-timedelta(days=365)
url=f"https://github.com/users/{user}/contributions?from={start.isoformat()}&to={end.isoformat()}"
req=urllib.request.Request(url,headers={"User-Agent":"profile-readme-activity-bot/1.0","Accept":"text/html"})
try:
    with urllib.request.urlopen(req,timeout=30) as response: page=response.read().decode("utf-8","replace")
except Exception as exc:
    print(f"Public contribution calendar unavailable: {exc}")
    print("Keeping last verified data; make the profile public to enable fresh activity data.")
    raise SystemExit(0)
days=[]
for match in re.finditer(r'data-date="(20\d\d-\d\d-\d\d)"[^>]*data-count="(\d+)"|data-count="(\d+)"[^>]*data-date="(20\d\d-\d\d-\d\d)"',page):
    if match.group(1): day,count=match.group(1),int(match.group(2))
    else: count,day=int(match.group(3)),match.group(4)
    days.append({"date":day,"count":count})
if len(days)<300:
    print("No public contribution calendar found. Keeping last verified data; no fake stats generated.")
    raise SystemExit(0)
payload={"username":user,"total":sum(x["count"] for x in days),"days":days}
out=Path("data/contributions.json"); out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload,indent=2)+"\n")
print(f"Fetched {len(days)} days and {payload['total']} contributions.")
