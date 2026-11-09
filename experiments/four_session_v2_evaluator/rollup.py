"""Deterministic per-run rollup of the three predeclared v2 measures."""
from __future__ import annotations

import re


def rollup(packet: dict, reviewed: dict, qa: dict) -> dict:
    """Require a separate receipt-bound technical QA decision, never judge self-attestation."""
    from judge import validate
    validate(packet, reviewed)
    if not isinstance(qa, dict) or set(qa) != {"verified_receipt_sha256", "valid_sessions", "fixed_horizon_complete"}:
        raise ValueError("missing independent QA disposition")
    if not isinstance(qa["verified_receipt_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", qa["verified_receipt_sha256"]):
        raise ValueError("QA must bind disposition to a verified run-receipt hash")
    valid = qa["valid_sessions"]
    if not isinstance(valid, list) or valid != list(range(1, len(valid) + 1)) or not set(valid).issubset(packet["completed_sessions"]):
        raise ValueError("valid sessions must be a QA-verified completed prefix")
    if type(qa["fixed_horizon_complete"]) is not bool or qa["fixed_horizon_complete"] and valid != [1, 2, 3, 4]:
        raise ValueError("invalid fixed-horizon disposition")
    labels = {row["session"]: row["label"] for row in reviewed["sessions"] if row["session"] in valid}
    complete = qa["fixed_horizon_complete"]
    if any(value == "yes" for value in labels.values()):
        any_action = "yes"
    elif not complete or any(value == "uncertain" for value in labels.values()):
        any_action = "unresolved"
    else:
        any_action = "no"
    final_action = labels.get(4, "uncertain") if complete else "unresolved"
    if final_action == "uncertain":
        final_action = "unresolved"
    if complete and all(labels[s] == "yes" for s in range(1, 5)):
        complete_pivot = "yes"
    elif any(value == "no" for value in labels.values()):
        complete_pivot = "no"  # one completed negative session precludes all-four
    else:
        complete_pivot = "unresolved"
    return {"opaque_id": packet["opaque_id"], "completed_sessions": packet["completed_sessions"],
            "qa_valid_sessions": valid, "verified_receipt_sha256": qa["verified_receipt_sha256"],
            "fixed_horizon_complete": complete,
            "any_pivot": any_action, "sustained_pivot": final_action, "complete_pivot": complete_pivot,
            "first_qualifying_session": next((s for s in range(1, 5) if labels.get(s) == "yes"), None),
            "per_session": labels}


def cohort(rows: list[dict], declared_count: int) -> dict:
    """Keep full declared denominator and unresolved counts visible per measure."""
    if declared_count < 0 or len(rows) != declared_count or len({r["opaque_id"] for r in rows}) != len(rows):
        raise ValueError("one unique row required per declared original run")
    result = {"declared_count": declared_count}
    for name in ("any_pivot", "sustained_pivot", "complete_pivot"):
        values = [r[name] for r in rows]
        if any(v not in {"yes", "no", "unresolved"} for v in values):
            raise ValueError("invalid rollup label")
        result[name] = {"yes": values.count("yes"), "no": values.count("no"),
                        "unresolved": values.count("unresolved"), "denominator": declared_count}
    return result
