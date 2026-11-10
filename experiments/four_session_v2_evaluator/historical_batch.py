"""Optional 60-case, one-shot historical judge transport. Offline by default.

Private packet data, mapping, approval and response files belong outside Git.
A frozen manifest plus a separate operator approval is required for --send.
No provider call is made by import or --validate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.request

from historical import validate
from run_judge import outside_git, output_text

URL = "https://openrouter.ai/api/v1/responses"
ID = re.compile(r"T[0-9]{3,}\Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_json(path: Path, value: dict) -> None:
    """Create a new, owner-only file; never overwrite an intent or reply."""
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())


def freeze(root: Path):
    manifest_file = root / "manifest.json"
    if (root / "manifest.json").is_symlink() or (root / "prompt.txt").is_symlink() or (root / "packets").is_symlink():
        raise ValueError("frozen inputs must not be symlinked")
    raw = manifest_file.read_bytes()
    manifest = json.loads(raw)
    hashes = manifest.get("packet_sha256")
    if (not isinstance(hashes, dict) or len(hashes) != 60 or manifest.get("packet_count") != 60
            or not isinstance(manifest.get("model"), str) or not manifest["model"].strip()
            or manifest.get("provider") != "openrouter" or manifest.get("endpoint") != URL
            or manifest.get("reasoning") != {"effort": "high"}):
        raise ValueError("manifest must freeze exactly 60 packets and OpenRouter high settings")
    prompt = (root / "prompt.txt").read_bytes()
    if sha(prompt) != manifest.get("prompt_sha256") or not prompt.strip():
        raise ValueError("prompt hash mismatch")
    packets = {}
    for name, digest in sorted(hashes.items()):
        if not ID.fullmatch(name):
            raise ValueError("packet ID invalid")
        file = root / "packets" / f"{name}.json"
        if file.is_symlink() or not file.is_file():
            raise ValueError("packet unavailable or symlinked")
        raw_packet = file.read_bytes()
        packet = json.loads(raw_packet)
        if sha(raw_packet) != digest or packet.get("opaque_id") != name:
            raise ValueError("packet/hash/ID mismatch")
        packets[name] = (raw_packet, packet)
    if {p.name for p in (root / "packets").glob("T*.json")} != {f"{i}.json" for i in packets}:
        raise ValueError("unexpected extra packet")
    return manifest, sha(raw), prompt, packets


def send_one(name: str, raw_packet: bytes, packet: dict, prompt: bytes,
             manifest: dict, manifest_hash: str, batch: Path, barrier: threading.Barrier, key: str):
    folder = batch / name
    folder.mkdir(mode=0o700)
    request_body = json.dumps({"model": manifest["model"], "reasoning": manifest["reasoning"],
        "input": [{"role": "system", "content": prompt.decode("utf-8")},
                  {"role": "user", "content": raw_packet.decode("utf-8")}]}).encode("utf-8")
    private_json(folder / "intent.json", {"id": name, "manifest_sha256": manifest_hash,
        "packet_sha256": sha(raw_packet), "prompt_sha256": sha(prompt),
        "request_sha256": sha(request_body), "state": "request_may_have_been_sent", "epoch": time.time()})
    started = time.time()
    try:
        barrier.wait(timeout=120)  # all sixty durable intents before network dispatch
        req = urllib.request.Request(URL, data=request_body, method="POST",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as response:
            body = response.read()
            status = response.status
        private_json(folder / "raw.json", {"status": status, "body": body.decode("utf-8", errors="replace")})
        reply = {}
        try:
            reply = json.loads(body)
            text = output_text(reply).strip()
            if text.startswith("```json") and text.endswith("```"):
                text = text[7:-3].strip()
            judged = validate(packet, json.loads(text))
            result = {"state": "validated_event_ids", "judge": judged}
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            result = {"state": "unresolved_invalid_reply", "error_type": type(exc).__name__,
                      "validation_error": str(exc)}
        result.update({"status": status, "usage": reply.get("usage"), "provider_response_id": reply.get("id")})
    except urllib.error.HTTPError as exc:
        private_json(folder / "raw.json", {"status": exc.code,
                     "body": exc.read().decode("utf-8", errors="replace")})
        result = {"state": "http_error_uncertain_billing", "status": exc.code}
    except BaseException as exc:
        result = {"state": "transport_error_uncertain_billing", "error_type": type(exc).__name__,
                  "error": str(exc)}
    result.update({"id": name, "manifest_sha256": manifest_hash, "packet_sha256": sha(raw_packet),
                   "elapsed_seconds": time.time() - started})
    private_json(folder / "result.json", result)
    return {"id": name, "state": result["state"], "usage": result.get("usage")}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="owner-only corpus directory outside Git")
    parser.add_argument("--send", action="store_true", help="one simultaneous 60-case batch; no retry")
    parser.add_argument("--approval", type=Path, help="separate, reviewer-approved manifest digest JSON")
    args = parser.parse_args(argv)
    os.umask(0o077)
    root = outside_git(args.root)
    if not root.is_dir() or root.stat().st_mode & 0o077:
        raise ValueError("corpus root must be owner-only (0700)")
    manifest, manifest_hash, prompt, packets = freeze(root)
    if not args.send:
        print(json.dumps({"validated_packets": len(packets), "manifest_sha256": manifest_hash,
                          "prompt_sha256": sha(prompt), "model": manifest["model"], "workers_if_approved": 60}))
        return None
    if args.approval is None:
        raise ValueError("--send requires independent approval")
    approval_path = outside_git(args.approval)
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if (approval.get("manifest_sha256") != manifest_hash or approval.get("approved") is not True
            or not isinstance(approval.get("reviewer"), str) or not approval["reviewer"].strip()):
        raise ValueError("approval does not match reviewed frozen manifest")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY unavailable; no request made")
    outside_git(root / "responses")  # reject symlinked output or Git redirection
    batch = root / "responses" / manifest_hash
    batch.mkdir(mode=0o700, parents=True, exist_ok=False)
    private_json(batch / "batch_intent.json", {"manifest_sha256": manifest_hash,
        "reviewer": approval["reviewer"], "requests": 60, "workers": 60,
        "state": "one_shot_simultaneous", "epoch": time.time()})
    barrier = threading.Barrier(60)
    with ThreadPoolExecutor(max_workers=60) as pool:
        futures = [pool.submit(send_one, name, raw, parsed, prompt, manifest, manifest_hash, batch, barrier, key)
                   for name, (raw, parsed) in packets.items()]
        rows = [future.result() for future in futures]
    usage = [x["usage"] for x in rows if isinstance(x.get("usage"), dict)]
    summary = {"manifest_sha256": manifest_hash,
               "states": {state: sum(x["state"] == state for x in rows)
                          for state in sorted({x["state"] for x in rows})},
               "usage_rows": len(usage),
               "tokens": {name: sum(u.get(name) or 0 for u in usage)
                          for name in ("input_tokens", "output_tokens", "total_tokens")}}
    private_json(batch / "summary.json", summary)
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    main()
