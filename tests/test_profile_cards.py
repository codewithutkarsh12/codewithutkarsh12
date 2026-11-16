import importlib.util
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("profile_cards", ROOT / "scripts" / "render_readme_cards.py")
CARDS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CARDS)
FETCH_SPEC = importlib.util.spec_from_file_location("fetch_contributions", ROOT / "scripts" / "fetch_contributions.py")
FETCH = importlib.util.module_from_spec(FETCH_SPEC)
FETCH_SPEC.loader.exec_module(FETCH)

class ProfileCardTests(unittest.TestCase):
    def test_current_github_calendar_markup_is_parsed(self):
        sample = '<table><td data-date="2026-11-15" data-level="2"><tool-tip aria-label="3 contributions on Nov 15, 2026">3 contributions on Nov 15, 2026</tool-tip></td><td data-date="2026-11-16" data-level="0"><tool-tip>No contributions on Nov 16, 2026</tool-tip></td></table>'
        days = FETCH.parse_contribution_calendar(sample)
        self.assertEqual(days, [{"date": "2026-11-15", "count": 3}, {"date": "2026-11-16", "count": 0}])

    def test_calendar_parser_does_not_guess_from_color_level(self):
        sample = '<td data-date="2026-11-16" data-level="4"></td>'
        self.assertEqual(FETCH.parse_contribution_calendar(sample), [])
    def test_contribution_heatmap_is_valid_svg(self):
        svg = CARDS.graph({"total": 3, "days": [{"date": date.today().isoformat(), "count": 3}]})
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("Every day", svg)

    def test_empty_heatmap_explains_why_activity_is_not_visible(self):
        svg = CARDS.graph({"total": None, "days": []})
        ET.fromstring(svg)
        self.assertIn("Awaiting public activity data", svg)
        self.assertIn("PROFILE VISIBILITY", svg)

    def test_empty_activity_never_invents_contribution_numbers(self):
        svg = CARDS.monthly({"total": None, "days": []})
        ET.fromstring(svg)
        self.assertIn("Awaiting data", svg)
        self.assertIn("current streak", svg)
        self.assertGreaterEqual(svg.count("—"), 4)
        self.assertNotIn("0 contributions", svg)

    def test_monthly_card_uses_supplied_total(self):
        today = date.today()
        days = [{"date": (today - timedelta(days=i)).isoformat(), "count": 1 if i != 2 else 0} for i in range(5)]
        svg = CARDS.monthly({"total": 4, "days": days})
        ET.fromstring(svg)
        self.assertIn("4", svg)
        self.assertIn("contributions", svg)

    def test_new_build_loop_and_original_hero_are_valid_svg(self):
        ET.parse(ROOT / "assets" / "build-loop.svg")
        ET.parse(ROOT / "assets" / "focus-orbit.svg")
        ET.parse(ROOT / "assets" / "project-timeline.svg")
        hero = (ROOT / "assets" / "hero.svg").read_text(encoding="utf-8")
        ET.fromstring(hero)
        self.assertIn("Software × Applied AI", hero)
        focus = (ROOT / "assets" / "focus-orbit.svg").read_text(encoding="utf-8")
        self.assertIn("@keyframes orbitDash", focus)
        self.assertIn("APPLIED AI", focus)

    def test_readme_keeps_hero_and_adds_profile_sections(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn('src="assets/hero.svg"', readme)
        self.assertIn("## GitHub Activity", readme)
        self.assertIn("## Project Milestones", readme)
        self.assertLess(readme.index("## GitHub Activity"), readme.index("## About Me"))
        self.assertLess(readme.index("## Project Milestones"), readme.index("## About Me"))
        self.assertIn("AUTO", readme)
        self.assertIn("CampusResolve AI", readme)
        self.assertIn("RepRise", readme)
        self.assertIn("## Education", readme)
        self.assertIn("## Project-Based Experience", readme)
        self.assertIn("assets/focus-orbit.svg", readme)
        self.assertIn("not a formal job or internship", readme)
        self.assertIn("## Skills & Tools", readme)
        self.assertIn("## Featured Projects", readme)

    def test_all_generated_cards_are_well_formed_svg(self):
        data = {"total": 4, "days": [{"date": date.today().isoformat(), "count": 4}]}
        cards = [CARDS.graph(data), CARDS.monthly(data),
                 CARDS.tile("BUILD", "Software", ["Products", "and tools"], "#315bff", "#fff", .1),
                 CARDS.project("Demo", ["Line one", "Line two"], "Python", "#315bff", .1)]
        for svg in cards:
            ET.fromstring(svg)

if __name__ == "__main__":
    unittest.main()
