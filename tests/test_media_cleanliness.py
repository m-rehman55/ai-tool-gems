import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class MediaCleanlinessTests(unittest.TestCase):
    def test_no_mp4_in_social_deals(self):
        """Ensure heavy video files are not tracked in git for assets/social-deals/."""
        social_deals_dir = ROOT / "assets" / "social-deals"
        if social_deals_dir.exists():
            mp4_files = list(social_deals_dir.glob("*.mp4"))
            self.assertEqual(
                len(mp4_files),
                0,
                f"Found tracked/loose mp4 video files in {social_deals_dir}: {mp4_files}"
            )

    def test_gitignore_contains_social_deals_mp4(self):
        """Ensure .gitignore explicitly ignores mp4 videos in assets/social-deals."""
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("assets/social-deals/*.mp4", gitignore)

if __name__ == "__main__":
    unittest.main()
