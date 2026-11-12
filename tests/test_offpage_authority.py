import csv, json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import offpage_authority_tracker as oat

class OffpageAuthorityTests(unittest.TestCase):
    def test_tracker_csv_valid(self):
        rows, errs = oat.validate_tracker(ROOT / "seo-agent/data/offpage_authority_tracker.csv", ROOT / "index.html")
        self.assertEqual(errs, [])
        self.assertGreaterEqual(len(rows), 10)

    def test_live_link_requires_source_and_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.csv"
            with p.open("w", newline="") as f:
                w = csv.writer(f); w.writerow(oat.REQUIRED_COLS)
                w.writerow(["x.com","https://x.com","Dir","80","Eligible","Editorial","active","","https://aitoolgems.tech/","AI Tool Gems","live","no","no","none","2026-11-12",""])
            _, errs = oat.validate_tracker(p, ROOT / "index.html")
            self.assertTrue(any("missing source_page" in e for e in errs))

    def test_prices_datasets_match_index(self):
        rows = list(csv.DictReader((ROOT / "prices/ai-tools-pricing-pakistan.csv").open()))
        data = json.loads((ROOT / "prices/ai-tools-pricing-pakistan.json").read_text())
        self.assertEqual(len(rows), 40)
        self.assertEqual(data["count"], 40)
        cursor = [r for r in rows if "Cursor" in r["product"]]
        self.assertEqual(cursor[0]["price_pkr"], "2800")
        self.assertEqual(cursor[0]["duration"], "1 Month")

    def test_skills_and_public_build_include_datasets(self):
        self.assertTrue((ROOT / ".agents/skills/off-page-authority-builder/SKILL.md").exists())
        self.assertIn("Off-Page Citation", (ROOT / ".agents/skills/geo-aeo-optimizer/SKILL.md").read_text())
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([sys.executable, str(ROOT / "scripts/build_public_site.py"), "--out-dir", td], check=True)
            self.assertTrue((Path(td) / "prices/ai-tools-pricing-pakistan.csv").exists())
            self.assertTrue((Path(td) / "prices/ai-tools-pricing-pakistan.json").exists())

if __name__ == "__main__":
    unittest.main()
