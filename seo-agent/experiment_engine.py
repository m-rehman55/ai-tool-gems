"""
SEO Agent Experiment Engine
"""

ENGINE = {
  "description": "Controlled SEO experiment engine",
  "required_fields": {
    "hypothesis": "What we expect to happen",
    "control": "Current state for comparison",
    "variant": "New change to test",
    "metric": "How we measure success",
    "start": "Experiment start date",
    "end": "Experiment end date",
    "result": "Experiment result",
    "decision": "KEEP/REVERT/ITERATE/EXTEND/REJECT"
  },
  "decisions": [
    "KEEP",
    "REVERT",
    "ITERATE",
    "EXTEND",
    "REJECT"
  ],
  "default_duration_days": 14
}

DECISIONS = ["KEEP", "REVERT", "ITERATE", "EXTEND", "REJECT"]

def create_experiment(hypothesis, control, variant, metric, duration=14):
    """Create a new experiment."""
    from datetime import datetime, timedelta
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=duration)).strftime("%Y-%m-%d")
    return {
        "hypothesis": hypothesis,
        "control": control,
        "variant": variant,
        "metric": metric,
        "start": start,
        "end": end,
        "result": None,
        "decision": None
    }

def evaluate_experiment(result, metric_target):
    """Evaluate experiment result and return decision."""
    if result is None:
        return "ITERATE"
    if result >= metric_target:
        return "KEEP"
    if result >= metric_target * 0.8:
        return "EXTEND"
    if result >= metric_target * 0.5:
        return "ITERATE"
    return "REVERT"

def record_result(experiment, result):
    """Record experiment result."""
    experiment["result"] = result
    experiment["decision"] = evaluate_experiment(result, 0)
    return experiment
