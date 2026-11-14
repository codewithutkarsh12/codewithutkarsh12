import importlib.util
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("profile_cards", ROOT / "scripts" / "render_readme_cards.py")
CARDS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CARDS)

class ProfileCardTests(unittest.TestCase):
    def test_contribution_heatmap_is_valid_svg(self):
        svg = CARDS.graph({"total": 3, "days": [{"date": date.today().isoformat(), "count": 3}]})
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("Every day", svg)

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

    def test_all_generated_cards_are_well_formed_svg(self):
        data = {"total": 4, "days": [{"date": date.today().isoformat(), "count": 4}]}
        cards = [CARDS.graph(data), CARDS.monthly(data),
                 CARDS.tile("BUILD", "Software", ["Products", "and tools"], "#315bff", "#fff", .1),
                 CARDS.project("Demo", ["Line one", "Line two"], "Python", "#315bff", .1)]
        for svg in cards:
            ET.fromstring(svg)

if __name__ == "__main__":
    unittest.main()
