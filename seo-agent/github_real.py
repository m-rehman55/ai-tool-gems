"""
GitHub Workflow - FREE-FIRST: Uses free data sources only.
"""

GITHUB = {
    "description": "GitHub workflow",
    "branch": "feature/real-seo-data-engine",
    "rule": "All implementation must be committed to GitHub. Do not overwrite unrelated work. Create PR according to repository workflow."
}

def get_github_status():
    """Return GitHub status."""
    return GITHUB
