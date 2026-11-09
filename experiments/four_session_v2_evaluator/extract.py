"""Offline extraction of B-visible evidence from a native events.jsonl.

Returns an in-memory judge packet; never writes private traces to the repository.
Only a caller-supplied opaque id is included. Gate decisions, system prompts,
model inputs and condition/route/receipt metadata are never passed to the judge.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# Historical extractor: E140b/peer_uptake_discovery/extract.py. Its fixed
# 2,500-character truncation is unsuitable for judging substantive edits.
CONDITION = re.compile(r"(?i)\b(?:A-)?E(?:5a|1[0-9]{2}[a-z]?)(?:v2)?\b|\bbase(?:[ -]allelo|v2)\b|\bNexus(?:-4| Research)?\b|\bBe collaborative\.?")


def scrub(text: object) -> str:
    """Best-effort treatment-word masking; independent reviewer must audit leaks."""
    return CONDITION.sub("[condition redacted]", str(text))


def model_text(output: dict) -> str:
    try:
        content = output["choices"][0]["message"].get("content") or []
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        text = item if isinstance(item, str) else item.get("text", item.get("output_text", "")) if isinstance(item, dict) else ""
        if isinstance(text, str):
            parts.append(text)
    return "\n".join(parts)


def extract(events_path: Path, delivery_path: Path, opaque_id: str) -> dict:
    """Parse original events, preserving complete text and 1-based journal rows.

    Only A Reads with valid JSON and a delivery-matched ID/hash count as exposure.
    Caller verifies receipt/native hashes separately. Packet must stay private.
    """
    if not re.fullmatch(r"T[0-9]{3,}", opaque_id):
        raise ValueError("use a treatment-free opaque id, e.g. T001")
    delivery = json.loads(Path(delivery_path).read_text(encoding="utf-8"))
    updates = delivery.get("deliveries")
    if delivery.get("status") != "ready" or not isinstance(updates, list):
        raise ValueError("delivery evidence is not ready")
    verified = {(x.get("post_id"), x.get("post_sha256")) for x in updates}
    if len(verified) != len(updates):
        raise ValueError("ambiguous delivery receipt")
    rows, completed = [], set()
    with Path(events_path).open(encoding="utf-8") as fp:
        for line_no, line in enumerate(fp, 1):
            event = json.loads(line)
            kind = event.get("kind")
            p = event.get("payload") or {}
            session = p.get("session")
            if kind == "session_complete":
                if type(session) is int and 1 <= session <= 4:
                    completed.add(session)
                continue
            if type(session) is not int or not 1 <= session <= 4:
                continue
            entry = {"event": line_no, "session": session}
            if kind == "model":
                text = model_text(p.get("output") or {})
                if not text:
                    continue
                entry.update(kind="b_message", text=scrub(text))
            elif kind == "tool_result":
                call = p.get("call") or {}
                args = call.get("arguments") or {}
                if not isinstance(args, dict):
                    args = {}
                fn, path = call.get("function"), str(args.get("file_path", ""))
                result = p.get("result", "")
                # Tool results belong to B's action, not proof that proposed code ran.
                if fn == "Read" and "shared_findings" in path and "agent_a" in path.lower():
                    try:
                        post = json.loads(result)
                    except (TypeError, ValueError) as exc:
                        raise ValueError(f"unparseable A Read at journal row {line_no}") from exc
                    digest = hashlib.sha256(result.encode("utf-8")).hexdigest()
                    if post.get("author") != "agent_a" or (post.get("id"), digest) not in verified or not path.endswith(
                        next(x["post_file"] for x in updates if x.get("post_id") == post.get("id") and x.get("post_sha256") == digest)
                    ):
                        raise ValueError(f"A Read does not match delivery receipt at journal row {line_no}")
                    entry.update(kind="a_read", text=scrub(result))
                elif fn == "Read" and path.endswith("notebook.json"):
                    entry.update(kind="notebook_read", text=scrub(result))
                elif fn in {"Write", "Edit"}:
                    text = args.get("content")
                    if text is None:
                        text = json.dumps(args, ensure_ascii=False)
                    accepted = isinstance(result, str) and (result.startswith("Wrote ") if fn == "Write" else
                        bool(re.match(r"(?i)^(?:edited|successfully edited|replaced|updated)\b", result)))
                    entry.update(kind="b_write" if accepted else "b_write_attempt",
                                 target="notebook" if path.endswith("notebook.json") else "file",
                                 text=scrub(text), tool_result=scrub(result))
                elif fn == "share_finding":
                    entry.update(kind="b_forum_post", text=scrub(json.dumps(args, ensure_ascii=False)),
                                 tool_result=scrub(result))
                elif fn in {"Bash", "bash", "execute", "evaluate_predictions"}:
                    entry.update(kind="b_execution", text=scrub(json.dumps(args, ensure_ascii=False)),
                                 tool_result=scrub(result))
                else:
                    continue
            else:
                continue
            rows.append(entry)
    return {"opaque_id": opaque_id, "completed_sessions": sorted(completed), "events": rows}
