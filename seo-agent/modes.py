"""
SEO Agent Modes - AUDIT, PROPOSE, PR, AUTO
"""

MODES = {
  "AUDIT": {
    "description": "Inspect only, no changes",
    "actions": [
      "crawl",
      "inspect",
      "analyze",
      "report"
    ],
    "auto_deploy": false,
    "requires_approval": false
  },
  "PROPOSE": {
    "description": "Propose changes, create PR",
    "actions": [
      "propose",
      "pr",
      "review"
    ],
    "auto_deploy": false,
    "requires_approval": true
  },
  "PR": {
    "description": "Create PR for review",
    "actions": [
      "branch",
      "commit",
      "push",
      "pr"
    ],
    "auto_deploy": false,
    "requires_approval": true
  },
  "AUTO": {
    "description": "Auto-execute low-risk verified changes",
    "actions": [
      "implement",
      "test",
      "deploy",
      "verify"
    ],
    "auto_deploy": true,
    "requires_approval": false
  }
}

DEFAULT_MODE = "AUTO"

def get_mode():
    """Return current mode."""
    return DEFAULT_MODE

def set_mode(mode):
    """Set operating mode."""
    global DEFAULT_MODE
    if mode in MODES:
        DEFAULT_MODE = mode
        return True
    return False

def can_auto_deploy(mode):
    """Check if mode allows auto deployment."""
    return MODES.get(mode, {}).get("auto_deploy", False)

def requires_approval(mode):
    """Check if mode requires human approval."""
    return MODES.get(mode, {}).get("requires_approval", True)
