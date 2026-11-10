"""Detached, one-case judge launcher for separately authorized future requests.

Default is offline. --send starts run_judge.py in a new OS session with a
private log so an API command-tool lifetime cannot kill an in-flight request.
It does not automatically retry, wait for, or score the request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from run_judge import PROMPT_SHA256, outside_git, run


def main(argv=None):
    parser = argparse.ArgumentParser(description="Detached optional single-case judge; offline by default")
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--provider", required=True, choices=["openrouter"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args(argv)
    base = ["--packet", str(args.packet), "--provider", args.provider, "--model", args.model]
    if not args.send:
        return run(base)
    if args.approval is None or args.output_dir is None:
        raise ValueError("explicit --approval and --output-dir required for detached send")
    packet_path = outside_git(args.packet)
    if not packet_path.is_file() or packet_path.is_symlink():
        raise ValueError("missing ordinary packet")
    raw = packet_path.read_bytes()
    packet = json.loads(raw)
    ident = packet.get("opaque_id")
    if not isinstance(ident, str) or not re.fullmatch(r"T[0-9]{3,}", ident):
        raise ValueError("invalid opaque case ID")
    digest = hashlib.sha256(raw).hexdigest()
    approval_path = outside_git(args.approval)
    if not approval_path.is_file() or approval_path.is_symlink():
        raise ValueError("missing ordinary reviewer approval")
    approved = json.loads(approval_path.read_text(encoding="utf-8"))
    if (approved.get("packet_sha256") != digest or approved.get("prompt_sha256") != PROMPT_SHA256
            or approved.get("provider") != args.provider or approved.get("model") != args.model
            or approved.get("reasoning_effort") != "high" or not str(approved.get("reviewer", "")).strip()):
        raise ValueError("reviewer approval does not bind this packet/prompt/model")
    out = outside_git(args.output_dir)
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    if out.stat().st_mode & 0o077:
        raise ValueError("output directory must be owner-only")
    stem = f"{ident}-{digest[:16]}"
    if any((out / (stem + suffix)).exists() for suffix in (".intent.json", ".raw.json", ".json", ".launcher.log")):
        raise FileExistsError("prior response/intent/log exists; no retry")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise ValueError("provider credential unavailable; no request sent")
    log = out / f"{stem}.launcher.log"
    log_fd = os.open(log, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    cmd = [sys.executable, str(Path(__file__).resolve().with_name("run_judge.py")),
           *base, "--approval", str(approval_path), "--output-dir", str(out), "--send"]
    with os.fdopen(log_fd, "wb") as logfile:
        child = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=logfile,
                                 stderr=subprocess.STDOUT, start_new_session=True,
                                 close_fds=True, env=os.environ.copy())
    print(f"detached single-case judge pid={child.pid}; private log={log.name}; do not auto-retry")
    return child.pid


if __name__ == "__main__":
    main()
