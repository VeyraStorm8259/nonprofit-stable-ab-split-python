"""Stable assignment for a nonprofit's receipt, reminder, and report workflow."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiError, infrai


@dataclass(frozen=True)
class ProgramRequest:
    user_id: str
    flag_key: str
    workflow: str


@dataclass(frozen=True)
class ProgramDecision:
    user_id: str
    workflow: str
    variant: str
    action: str


def choose_action(workflow: str, variant: str) -> str:
    actions = {
        "donor_receipt": {"control": "send_receipt_email", "variant": "send_receipt_email_with_campaign_link"},
        "volunteer_reminder": {"control": "send_reminder_email", "variant": "send_reminder_email_with_shift_summary"},
        "campaign_report": {"control": "render_monthly_report", "variant": "render_report_with_channel_breakdown"},
    }
    try:
        return actions[workflow][variant]
    except KeyError as exc:
        raise ValueError(f"unknown workflow or variant: {workflow}/{variant}") from exc


def load_decision(request: ProgramRequest) -> ProgramDecision:
    user = infrai.auth.user.get(request.user_id)
    value = infrai.flags.get_value(request.flag_key, request.user_id)
    variant = str(value.get("value", value.get("default_value", "control")))
    if variant not in {"control", "variant"}:
        variant = "control"
    return ProgramDecision(request.user_id, request.workflow, variant, choose_action(request.workflow, variant))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one nonprofit program decision")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--flag-key", required=True)
    parser.add_argument("--workflow", choices=["donor_receipt", "volunteer_reminder", "campaign_report"], required=True)
    args = parser.parse_args()
    try:
        decision = load_decision(ProgramRequest(args.user_id, args.flag_key, args.workflow))
    except InfraiError as exc:
        raise SystemExit(f"Infrai rejected the request ({exc.code}); check the supplied user and flag") from exc
    print({"user": decision.user_id, "workflow": decision.workflow, "variant": decision.variant, "action": decision.action})


if __name__ == "__main__":
    main()
