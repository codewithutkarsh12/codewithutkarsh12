#!/usr/bin/env python3
"""Fetch official GitHub contributions, with a clearly labelled public-repository fallback."""
import json, re, urllib.request
from html.parser import HTMLParser
from datetime import date, timedelta
from pathlib import Path

USER = "codewithutkarsh12"
FEATURED_REPOS = ("auto-orchestrator", "campusresolve-ai", "DAILY-ONE-PUSHUP-INCREASE-")

class ContributionCalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = []
        self.current = None
        self.text = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and re.fullmatch(r"20\d{2}-\d{2}-\d{2}", attrs.get("data-date", "")):
            self.current = {"date": attrs["data-date"], "count": None}
            self.text = []
            self.labels = []
            if attrs.get("data-count", "").isdigit():
                self.current["count"] = int(attrs["data-count"])
        elif self.current is not None:
            for key in ("aria-label", "title", "data-count"):
                value = attrs.get(key, "")
                if value:
                    self.labels.append(value)
            if attrs.get("data-count", "").isdigit():
                self.current["count"] = int(attrs["data-count"])

    def handle_data(self, data):
        if self.current is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.current is not None:
            combined = " ".join(self.labels + self.text)
            match = re.search(r"(\d+)\s+contributions?", combined, re.I)
            if match:
                self.current["count"] = int(match.group(1))
            elif re.search(r"no contributions", combined, re.I):
                self.current["count"] = 0
            if self.current["count"] is not None:
                self.days.append(self.current)
            self.current = None

def parse_contribution_calendar(page):
    parser = ContributionCalendarParser()
    parser.feed(page)
    return sorted(parser.days, key=lambda item: item["date"])

def request_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "profile-readme-activity-bot/2.1", "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8", "replace"))

def fetch_featured_repo_commits():
    commits = []
    for repo in FEATURED_REPOS:
        page = 1
        while True:
            url = f"https://api.github.com/repos/{USER}/{repo}/commits?author={USER}&per_page=100&page={page}"
            try:
                batch = request_json(url)
            except Exception as exc:
                print(f"Could not fetch {repo} commits: {exc}")
                break
            if not isinstance(batch, list) or not batch:
                break
            for item in batch:
                stamp = (item.get("commit", {}).get("author") or {}).get("date")
                if stamp:
                    commits.append(stamp[:10])
            if len(batch) < 100:
                break
            page += 1
    return commits

def build_commit_calendar(commit_dates, start, end):
    counts = {}
    for stamp in commit_dates:
        try:
            day = date.fromisoformat(stamp[:10])
        except (TypeError, ValueError):
            continue
        if start <= day <= end:
            key = day.isoformat()
            counts[key] = counts.get(key, 0) + 1
    days = []
    current = start
    while current <= end:
        key = current.isoformat()
        days.append({"date": key, "count": counts.get(key, 0)})
        current += timedelta(days=1)
    return days

def main():
    end = date.today()
    start = end - timedelta(days=365)
    url = f"https://github.com/users/{USER}/contributions?from={start.isoformat()}&to={end.isoformat()}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "profile-readme-activity-bot/2.1", "Accept": "text/html"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", "replace")
    except Exception as exc:
        print(f"Official contribution calendar unavailable: {exc}")
        page = ""

    official_days = parse_contribution_calendar(page)
    if len(official_days) >= 300:
        payload = {
            "username": USER,
            "source": "github_contributions",
            "scope": "Official GitHub contribution calendar",
            "total": sum(day["count"] for day in official_days),
            "days": official_days,
        }
        print(f"Fetched {len(official_days)} official calendar days.")
    else:
        print(f"Official calendar unavailable or incomplete ({len(official_days)} dated cells).")
        print("Falling back to commits in the three featured public repositories only.")
        commit_dates = fetch_featured_repo_commits()
        if not commit_dates:
            print("No public commits were returned. Existing activity data is preserved.")
            return
        fallback_days = build_commit_calendar(commit_dates, start, end)
        payload = {
            "username": USER,
            "source": "featured_public_repos",
            "scope": ", ".join(FEATURED_REPOS),
            "total": sum(day["count"] for day in fallback_days),
            "days": fallback_days,
        }
        print(f"Fetched {payload['total']} commits from {len(FEATURED_REPOS)} featured public repositories.")

    output = Path("data/contributions.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved activity data from source: {payload['source']}")

if __name__ == "__main__":
    main()
