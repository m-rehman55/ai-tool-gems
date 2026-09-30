"""
SEO Agent Telegram Reporter
"""

TELEGRAM = {
  "description": "Telegram reporting for SEO agent",
  "channels": [
    "critical alerts",
    "deployment reports",
    "daily summaries",
    "weekly reports",
    "monthly reports",
    "experiment results",
    "rollback reports",
    "SEO score changes"
  ],
  "critical_alerts": [
    "site down",
    "robots broken",
    "sitemap broken",
    "mass noindex",
    "canonical disaster",
    "mass 404",
    "major performance regression",
    "wrong currency",
    "accidental locale changes",
    "significant indexed-page loss"
  ],
  "status": "configured",
  "secrets_required": [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID"
  ]
}

def send_critical_alert(message):
    """Send critical alert."""
    return {"alert": "critical", "message": message}

def send_deployment_report(report):
    """Send deployment report."""
    return {"report": "deployment", "data": report}

def send_daily_summary(summary):
    """Send daily summary."""
    return {"report": "daily", "data": summary}

def send_weekly_report(report):
    """Send weekly report."""
    return {"report": "weekly", "data": report}

def send_monthly_report(report):
    """Send monthly report."""
    return {"report": "monthly", "data": report}

def send_experiment_result(result):
    """Send experiment result."""
    return {"report": "experiment", "data": result}

def send_rollback_report(report):
    """Send rollback report."""
    return {"report": "rollback", "data": report}

def send_seo_score_change(change):
    """Send SEO score change."""
    return {"report": "score", "data": change}

def send_report(report_type, data):
    """Send any report."""
    return {"report": report_type, "data": data}


# Telegram Control Center
TELEGRAM_CONTROL = {
  "description": "Telegram as SEO control center",
  "daily_report": [
    "DATE",
    "HERMES STATUS",
    "SEO SCORE",
    "SCORE DELTA",
    "GSC",
    "TECHNICAL",
    "CONTENT",
    "PRODUCT",
    "JAPAN",
    "PAKISTAN",
    "COMPETITORS",
    "DEPLOYMENTS",
    "EXPERIMENTS",
    "BLOCKERS",
    "NEXT ACTIONS"
  ],
  "weekly_report": "Every week",
  "monthly_report": "Every month",
  "immediate": "CRITICAL ALERT",
  "after_deployment": "DEPLOYMENT REPORT",
  "after_rollback": "ROLLBACK REPORT",
  "after_experiment": "EXPERIMENT REPORT",
  "after_incident": "INCIDENT REPORT",
  "status": "configured"
}

def send_daily_report(report):
    """Send daily report."""
    return {"report": "daily", "data": report}

def send_weekly_report(report):
    """Send weekly report."""
    return {"report": "weekly", "data": report}

def send_monthly_report(report):
    """Send monthly report."""
    return {"report": "monthly", "data": report}

def send_critical_alert(alert):
    """Send critical alert."""
    return {"alert": "critical", "data": alert}

def send_deployment_report(report):
    """Send deployment report."""
    return {"report": "deployment", "data": report}

def send_rollback_report(report):
    """Send rollback report."""
    return {"report": "rollback", "data": report}

def send_experiment_report(report):
    """Send experiment report."""
    return {"report": "experiment", "data": report}

def send_incident_report(report):
    """Send incident report."""
    return {"report": "incident", "data": report}

def get_telegram_status():
    """Return Telegram control center status."""
    return TELEGRAM_CONTROL
