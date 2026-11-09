"""Offline release check: compare a prepared E160 package with an approved Git tree.

Run this with an explicitly approved commit before any provider call. A successful
prepare receipt authenticates the freeze against itself, not against approved code.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


PACKAGE_FILES = (
    "launcher.py", "source_hooks.py", "adapter.py", "preflight.py",
    "SOURCE_HOOK_DIFF.patch", "stimulus/manifest.json",
    "stimulus/files/mask_loss.py", "stimulus/files/eligible_random.py",
    "stimulus/files/mask_covariate_balance.py",
)
PREFIX = "experiments/A-E160/package/"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify(repo: Path, commit: str, attempt: Path) -> dict:
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("approved commit must be a full lowercase SHA-1")
    root = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], text=True).strip()
    repo = Path(root).resolve(strict=True)
    resolved = subprocess.check_output([
        "git", "-C", str(repo), "rev-parse", "--verify", f"{commit}^{{commit}}",
    ], text=True).strip()
    if resolved != commit:
        raise ValueError("approved commit does not resolve exactly")
    receipt = json.loads((attempt / "prepare_receipt.json").read_text())
    if (attempt / "launch_intent.json").exists() or (attempt / "run_receipt.json").exists():
        raise ValueError("release check must precede launch")
    hashes = receipt["package_hashes"]
    if (receipt.get("status") != "prepared_no_model_call"
            or receipt.get("experiment") != "E160"
            or receipt.get("attempt") != str(attempt.resolve(strict=True))
            or set(hashes) != set(PACKAGE_FILES)):
        raise ValueError("prepared package receipt or runtime roster mismatch")
    digest = sha(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode())
    if receipt.get("package_digest_sha256") != digest:
        raise ValueError("prepared package digest mismatch")
    for name in PACKAGE_FILES:
        from_git = subprocess.check_output([
            "git", "-C", str(repo), "show", f"{commit}:{PREFIX}{name}",
        ])
        if (sha(from_git) != hashes[name]
                or sha((attempt / "package" / name).read_bytes()) != hashes[name]):
            raise ValueError(f"approved Git tree / frozen package mismatch: {name}")
    return {"status": "approved_tree_matches_prepared_package", "approved_commit": commit,
            "package_digest_sha256": digest, "runtime_files": len(PACKAGE_FILES)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--approved-commit", required=True)
    parser.add_argument("--attempt", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.repo, args.approved_commit, args.attempt), sort_keys=True))


if __name__ == "__main__":
    main()
