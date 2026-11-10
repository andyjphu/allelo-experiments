"""Reusable observed-horizon judge validation and historical sensitivity rollup.

This module does not send model requests or modify the fixed-four-session rubric.
A citation points to a stable (session, journal event number), never to a
model-generated quotation. Semantic linkage still requires review.
"""
from __future__ import annotations

import re

LABELS = {"yes", "no", "uncertain"}


def validate(packet: dict, judged: dict) -> dict:
    if not isinstance(packet, dict) or not isinstance(judged, dict) or set(judged) != {"sessions", "overall_uncertainty"}:
        raise ValueError("invalid packet or judge response")
    if not isinstance(judged["overall_uncertainty"], str):
        raise ValueError("overall uncertainty must be text")
    completed = packet.get("completed_sessions")
    if not isinstance(completed, list) or not completed or completed != list(range(1, len(completed) + 1)):
        raise ValueError("completed sessions must be a contiguous observed prefix")
    sessions = judged["sessions"]
    if not isinstance(sessions, list) or [s.get("session") for s in sessions] != completed:
        raise ValueError("judge must score every and only observed completed session")
    events = packet.get("events")
    if not isinstance(events, list) or any(type(e.get("event")) is not int or type(e.get("session")) is not int for e in events):
        raise ValueError("packet events missing stable journal IDs")
    indexed = {(e["session"], e["event"]): e for e in events}
    if len(indexed) != len(events):
        raise ValueError("duplicate event/session ID")
    cited_a_reads = set()
    for row in sessions:
        if not isinstance(row, dict) or set(row) != {"session", "label", "evidence", "contrary", "uncertainty"}:
            raise ValueError("invalid per-session response shape")
        s = row["session"]
        if row["label"] not in LABELS or not isinstance(row["uncertainty"], str):
            raise ValueError("invalid label or uncertainty")
        evidence = []
        for field in ("evidence", "contrary"):
            if not isinstance(row[field], list):
                raise ValueError("citations must be arrays")
            for citation in row[field]:
                if (not isinstance(citation, dict) or set(citation) != {"event", "reason"}
                        or type(citation["event"]) is not int or not isinstance(citation["reason"], str)
                        or not citation["reason"].strip()):
                    raise ValueError("citation must have integer event ID and nonempty reason")
                event = indexed.get((s, citation["event"]))
                if event is None:
                    raise ValueError("event ID missing or cited under wrong session")
                if field == "evidence":
                    evidence.append(event)
                    if event.get("kind") == "a_read":
                        cited_a_reads.add(event["event"])
        if row["label"] == "yes":
            actions = [event for event in evidence if event.get("kind") in {"b_write", "b_execution"}
                       and (event.get("kind") != "b_write" or event.get("target") == "file")]
            if not actions:
                raise ValueError("yes needs an accepted B file Write or execution event; forum/notebook-only requires manual review")
            if not any(a < b["event"] for a in cited_a_reads for b in actions):
                raise ValueError("yes needs cited A Read before cited B action")
    return judged


def rollup(packet: dict, judged: dict, qa: dict) -> dict:
    """Partial/last-observed/all-observed, never the announced-S4 v2 measures.

    Independent technical QA authenticates receipt/event hashes and the actual
    endpoint. Syntax here cannot prove that an input receipt is authentic.
    """
    validate(packet, judged)
    if not isinstance(qa, dict) or set(qa) != {"verified_receipt_sha256", "valid_sessions", "observed_endpoint_confirmed"}:
        raise ValueError("independent QA disposition required")
    digest = qa["verified_receipt_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("invalid receipt digest")
    valid = qa["valid_sessions"]
    if not isinstance(valid, list) or valid != list(range(1, len(valid) + 1)) or not set(valid).issubset(packet["completed_sessions"]):
        raise ValueError("QA-valid sessions must be a completed prefix")
    if type(qa["observed_endpoint_confirmed"]) is not bool or qa["observed_endpoint_confirmed"] and valid != packet["completed_sessions"]:
        raise ValueError("endpoint confirmation disagrees with QA-valid sessions")
    labels = [row["label"] for row in judged["sessions"] if row["session"] in valid]
    endpoint = qa["observed_endpoint_confirmed"]
    partial = "yes" if "yes" in labels else "no" if endpoint and labels and "uncertain" not in labels else "unresolved"
    sustained = labels[-1] if endpoint and labels else "unresolved"
    if sustained == "uncertain":
        sustained = "unresolved"
    complete = "no" if "no" in labels else "yes" if endpoint and labels and all(x == "yes" for x in labels) else "unresolved"
    return {"partial": partial, "sustained": sustained, "complete": complete,
            "observed_sessions": len(packet["completed_sessions"]), "qa_valid_sessions": valid,
            "observed_endpoint_confirmed": endpoint, "verified_receipt_sha256": digest,
            "session_labels": {row["session"]: row["label"] for row in judged["sessions"] if row["session"] in valid}}
