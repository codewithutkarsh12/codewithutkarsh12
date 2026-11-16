#!/usr/bin/env python3
"""Fetch and parse the public GitHub contribution calendar without guessing counts."""
import json, re, urllib.request
from html.parser import HTMLParser
from datetime import date, timedelta
from pathlib import Path

USER = "codewithutkarsh12"

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

def main():
    end = date.today()
    start = end - timedelta(days=365)
    url = f"https://github.com/users/{USER}/contributions?from={start.isoformat()}&to={end.isoformat()}"
    request = urllib.request.Request(url, headers={"User-Agent": "profile-readme-activity-bot/2.0", "Accept": "text/html"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", "replace")
    except Exception as exc:
        print(f"Public contribution calendar unavailable: {exc}")
        print("Check profile visibility and contribution privacy settings. Existing data is preserved.")
        return
    days = parse_contribution_calendar(page)
    if len(days) < 300:
        print(f"Expected at least 300 dated contribution cells; parsed {len(days)}.")
        print("GitHub may be hiding the calendar because the profile is private, or its markup changed.")
        print("No data was overwritten and no contribution counts were guessed.")
        return
    payload = {"username": USER, "total": sum(day["count"] for day in days), "days": days}
    output = Path("data/contributions.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(days)} days and {payload['total']} contributions.")

if __name__ == "__main__":
    main()