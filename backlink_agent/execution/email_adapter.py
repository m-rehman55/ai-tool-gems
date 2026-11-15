"""Editorial Email Pitch Automated Adapter.

Dispatches structured editorial guest post & case study pitches directly
to tech news publication editors (e.g. editors@techjuice.pk).
"""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from typing import Any, Dict, Optional

from .models import ExecutionResult, ExecutionStatus


class EmailPitchAdapter:
    """Automates editorial email pitching for tech media publications."""

    ADAPTER_NAME = "email_editorial_pitch"

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        self.smtp_host = smtp_host or os.environ.get("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.environ.get("SMTP_USER")
        self.smtp_password = smtp_password or os.environ.get("SMTP_PASSWORD")

    def execute(
        self,
        prospect: Any,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Executes email pitch dispatch."""
        domain = getattr(prospect, "prospect_domain", "techjuice.pk")
        draft = getattr(prospect, "draft", {}) or {}

        recipient = "editors@techjuice.pk" if domain == "techjuice.pk" else f"editors@{domain}"
        subject = "Story Pitch: Tracking AI Software Pricing & Local Payment Rails in Pakistan"

        body = (
            "Hi Editorial Team,\n\n"
            "I wanted to share a timely data-driven study on Pakistan's AI adoption ecosystem.\n\n"
            "AI Tool Gems (https://aitoolgems.tech/) has published an index analyzing 40 commercial AI software tools, "
            "documenting subscription price parity in Pakistani Rupee (PKR) and domestic rails (EasyPaisa, JazzCash, Raast, SadaPay).\n\n"
            "Dataset reference: https://aitoolgems.tech/prices/\n"
            "CSV source: https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv\n\n"
            "Would love to offer this as an exclusive guest op-ed or community data story for your readers.\n\n"
            "Best regards,\n"
            "AI Tool Gems Editorial Team\n"
            "https://aitoolgems.tech/\n"
        )

        # Dry run or unconfigured SMTP
        if dry_run or not (self.smtp_host and self.smtp_user and self.smtp_password):
            return ExecutionResult(
                prospect_domain=domain,
                adapter_name=self.ADAPTER_NAME,
                status=ExecutionStatus.DRY_RUN,
                live_url=f"Sent via editorial pitch to {recipient}",
                evidence_message=f"Simulated email pitch sent to {recipient}",
                audit_metadata={
                    "recipient": recipient,
                    "subject": subject,
                    "simulated": True,
                },
            )

        # Live SMTP sending
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return ExecutionResult(
                prospect_domain=domain,
                adapter_name=self.ADAPTER_NAME,
                status=ExecutionStatus.SUCCESS,
                live_url=f"Sent via email pitch to {recipient}",
                evidence_message=f"Live email pitch delivered to {recipient}",
                audit_metadata={
                    "recipient": recipient,
                    "subject": subject,
                },
            )
        except Exception as exc:
            return ExecutionResult(
                prospect_domain=domain,
                adapter_name=self.ADAPTER_NAME,
                status=ExecutionStatus.FAILED,
                error_message=str(exc),
                evidence_message=f"SMTP dispatch to {recipient} failed: {exc}",
            )
