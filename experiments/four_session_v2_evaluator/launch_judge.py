"""Optional screen-backed, one-case judge launcher for future approved requests.

Default is offline. --send starts run_judge.py under detached /usr/bin/screen,
using owner-only wrapper/log/exit files so a short API command-tool lifetime
cannot itself kill a long provider request. No automatic retry or scoring.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

from run_judge import PROMPT_SHA256, outside_git, run

SCREEN = Path("/usr/bin/screen")


def owner_file(path: Path, data: str, mode: int = 0o600) -> None:
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(data)
        file.flush()
        os.fsync(file.fileno())


def main(argv=None):
    parser = argparse.ArgumentParser(description="Screen-backed single-case judge; offline by default")
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
    if any((out / (stem + suffix)).exists() for suffix in (".intent.json", ".raw.json", ".json")):
        raise FileExistsError("prior response/intent exists; no retry")
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise ValueError("provider credential unavailable; no request sent")
    if not SCREEN.is_file():
        raise RuntimeError("/usr/bin/screen unavailable; no request sent")

    # An owner-only case directory is a durable dispatch lock even if screen
    # fails before run_judge can create its per-packet provider intent.
    case = out / f"{stem}.screen"
    case.mkdir(mode=0o700, exist_ok=False)
    session = f"judge_{ident}_{digest[:12]}_{os.getpid()}"
    cmd = [sys.executable, str(Path(__file__).resolve().with_name("run_judge.py")),
           "--packet", str(packet_path), "--provider", args.provider, "--model", args.model,
           "--approval", str(approval_path), "--output-dir", str(out), "--send"]
    wrapper = case / "wrapper.sh"
    console = case / "console.log"
    exitcode = case / "launcher.exitcode"
    lines = ["#!/bin/bash", "set -uo pipefail", "umask 077", f"cd {shlex.quote(str(case))} || exit 95",
             f"exec > {shlex.quote(str(console))} 2>&1",
             "trap 'rc=$?; trap - EXIT; printf \"%s\\n\" \"$rc\" > launcher.exitcode.tmp; mv launcher.exitcode.tmp launcher.exitcode; exit \"$rc\"' EXIT",
             " ".join(shlex.quote(x) for x in cmd)]
    owner_file(wrapper, "\n".join(lines) + "\n", 0o700)
    owner_file(case / "dispatch_intent.json", json.dumps({"session": session, "packet_sha256": digest,
               "prompt_sha256": PROMPT_SHA256, "model": args.model,
               "state": "screen_start_or_provider_outcome_may_be_uncertain"}) + "\n")
    fd = os.open(case / "dispatch.stdout", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as dispatch:
        started = subprocess.run([str(SCREEN), "-L", "-dmS", session, "/bin/bash", str(wrapper)],
                                 cwd=case, env=os.environ.copy(), stdin=subprocess.DEVNULL,
                                 stdout=dispatch, stderr=subprocess.STDOUT, timeout=15, check=False)
    owner_file(case / "screen_start_exitcode", f"{started.returncode}\n")
    if started.returncode != 0:
        raise RuntimeError("screen startup failed; inspect private dispatch and do not retry automatically")
    print(f"detached screen session={session}; private case dir={case.name}; inspect exit sidecar, no auto-retry")
    return session


if __name__ == "__main__":
    main()
