"""
CLI Entry Point for Maintenance Agent
-------------------------------------
Usage:
    python -m maintenance_agent audit
    python -m maintenance_agent list-monitors
    python -m maintenance_agent run-monitor <monitor_id>
"""

import sys
import json
from pathlib import Path

from .executor import MaintenanceExecutor
from .monitors import MonitorRegistry


def main():
    args = sys.argv[1:]
    command = args[0] if args else "audit"
    executor = MaintenanceExecutor()

    if command == "list-monitors":
        print("=" * 80)
        print("🛠️  HERMES Operational Maintenance Monitors (15 Registered)")
        print("=" * 80)
        for m in executor.registry.all_monitors():
            print(f"[{m.id}] {m.name}")
            print(f"  • Frequency:               {m.frequency.value}")
            print(f"  • What it checks:          {m.what_it_checks}")
            print(f"  • Evidence source:         {m.evidence_source}")
            print(f"  • Change threshold:        {m.change_threshold}")
            print(f"  • False-positive handling: {m.false_positive_handling}")
            print(f"  • Notification dest:       {m.notification_destination}")
            print(f"  • Required owner action:   {m.required_owner_action}")
            print(f"  • Nature of action:        {m.action_nature.value} (Rule K Enforced)")
            if m.manual_alternative_sop:
                print(f"  • Manual Alternative SOP:  {m.manual_alternative_sop}")
            print("-" * 80)
        return

    elif command == "run-monitor":
        if len(args) < 2:
            print("Error: Missing monitor ID. Usage: python -m maintenance_agent run-monitor <MON-ID>")
            sys.exit(1)
        mon_id = args[1]
        result = executor.run_monitor(mon_id)
        print(f"Monitor: {result.monitor_id} | Status: {result.status.value}")
        for finding in result.findings:
            print(f"  - {finding}")
        if result.owner_action_needed:
            print(f"  Action needed: {result.action_summary}")
        return

    elif command == "audit":
        print("=" * 80)
        print("🚀 Running HERMES Operational Maintenance Audit (Rule K: Strict Read-Only)")
        print("=" * 80)
        results = executor.run_all()
        report = executor.generate_report(results)
        
        # Save report locally
        out_dir = Path("reports") / "maintenance"
        out_dir.mkdir(parents=True, exist_ok=True)
        report_file = out_dir / f"maintenance_audit_{report['report_id']}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        print(f"Total Monitors:  {report['monitors_total']}")
        print(f"Passed:          {report['monitors_passed']}")
        print(f"Warned:          {report['monitors_warned']}")
        print(f"Failed:          {report['monitors_failed']}")
        print(f"Actions Needed:  {report['owner_actions_required']}")
        print(f"Rule K Enforced: {report['rule_k_invariant_enforced']} (100% Read-Only)")
        print(f"Report written:  {report_file}")
        print("=" * 80)
        return

    else:
        print(f"Unknown command: {command}")
        print("Supported commands: audit, list-monitors, run-monitor <monitor_id>")
        sys.exit(1)


if __name__ == "__main__":
    main()
