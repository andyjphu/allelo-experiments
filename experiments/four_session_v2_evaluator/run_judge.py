"""Optional single-case judge runner. Default is offline; --send is deliberate.

No private trace is written under Git. Never execute --send without independent
packet privacy review and authorization for the selected external provider/model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request

from judge import PROMPT, parse

URL = "https://openrouter.ai/api/v1/responses"


def outside_git(path: Path) -> Path:
    # Reject symlinked path components before resolve() can erase evidence of them.
    raw = path.expanduser().absolute()
    cursor = Path(raw.anchor)
    for part in raw.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError("symlinked private path is not allowed")
    resolved = raw.resolve()
    anchor = resolved if resolved.exists() and resolved.is_dir() else resolved.parent
    while not anchor.exists():
        anchor = anchor.parent
    probe = subprocess.run(["git", "-C", str(anchor), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=False)
    if probe.returncode == 0:
        raise ValueError("private packet/approval/output must be outside any Git worktree")
    return resolved


def output_text(reply: dict) -> str:
    pieces = []
    for item in reply.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") in {"output_text", "text"} and isinstance(part.get("text"), str):
                pieces.append(part["text"])
    if not pieces:
        raise ValueError("provider returned no output text")
    return "\n".join(pieces)


def options(argv=None):
    cli = argparse.ArgumentParser(description="Offline by default; one authorized judge request with --send")
    cli.add_argument("--packet", required=True, type=Path, help="reviewed owner-only packet JSON outside Git")
    cli.add_argument("--provider", required=True, choices=["openrouter"])
    cli.add_argument("--model", required=True, help="explicit provider model id")
    cli.add_argument("--send", action="store_true", help="send ONE approved packet to external provider")
    cli.add_argument("--approval", type=Path, help="independent reviewer approval JSON outside Git, required for --send")
    cli.add_argument("--output-dir", type=Path, help="owner-only directory outside Git, required for --send")
    return cli.parse_args(argv)


def run(argv=None):
    args = options(argv)
    packet_path = outside_git(args.packet)
    if not packet_path.is_file() or packet_path.is_symlink():
        raise ValueError("packet must be an ordinary off-repo file")
    raw = packet_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    packet = json.loads(raw)
    if not isinstance(packet, dict) or not isinstance(packet.get("opaque_id"), str) or not re.fullmatch(r"T[0-9]{3,}", packet["opaque_id"]) or not isinstance(packet.get("events"), list) or not isinstance(packet.get("completed_sessions"), list):
        raise ValueError("invalid judge packet")
    if not args.send:
        print(f"DRY RUN: {packet['opaque_id']} sha256={digest}; no approval, credential or provider accessed")
        return None
    if not args.approval or not args.output_dir:
        raise ValueError("--send requires --approval and --output-dir")
    approval_path = outside_git(args.approval)
    if not approval_path.is_file() or approval_path.is_symlink():
        raise ValueError("approval must be an ordinary off-repo file")
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if not isinstance(approval, dict) or approval.get("packet_sha256") != digest or approval.get("provider") != args.provider or approval.get("model") != args.model or approval.get("reasoning_effort") != "high" or not isinstance(approval.get("reviewer"), str) or not approval["reviewer"].strip():
        raise ValueError("packet/model/provider not independently approved; do not send")
    out = outside_git(args.output_dir)
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    if out.is_symlink() or out.stat().st_mode & 0o077:
        raise ValueError("output directory must be owner-only (0700)")
    dest = out / f"{packet['opaque_id']}-{digest[:16]}.json"
    intent = out / f"{packet['opaque_id']}-{digest[:16]}.intent.json"
    if dest.exists() or intent.exists():
        raise FileExistsError("prior request or intent exists; reconcile manually before any resend")
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is missing; no call made")
    payload = {"model": args.model, "reasoning": {"effort": "high"}, "input": [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": json.dumps(packet, ensure_ascii=False)}]}
    # Reserve intent atomically before any possible HTTP request. Keep it even
    # after timeout/parse error: the provider may have billed or received data.
    intent_fd = os.open(intent, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(intent_fd, "w", encoding="utf-8") as file:
        json.dump({"opaque_id": packet["opaque_id"], "packet_sha256": digest,
                   "provider": args.provider, "model": args.model, "reasoning_effort": "high",
                   "status": "request_may_have_been_sent"}, file)
        file.write("\n")
    request = urllib.request.Request(URL, data=json.dumps(payload, ensure_ascii=False).encode(), method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    # A request may have been billed even if a timeout/parse error follows. No retries.
    with urllib.request.urlopen(request, timeout=240) as response:
        reply = json.load(response)
    judged = parse(packet, output_text(reply))
    record = {"opaque_id": packet["opaque_id"], "packet_sha256": digest, "provider": args.provider,
              "model": args.model, "reasoning_effort": "high", "approved_by": approval["reviewer"], "provider_response_id": reply.get("id"),
              "usage": reply.get("usage"), "judge": judged}
    fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"private judge response saved: {dest.name}; review semantics before rollup")
    return record


if __name__ == "__main__":
    run()
