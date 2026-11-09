# A-E160 preflight on mm-west-2

Status, 2026-11-09: **technical offline preflight passes**. No counted trial or provider request was made. This document does not release trials or replace the experiment owner's exact-text/review requirements.

## Recovered inputs and environment

All paths below are on mm-west-2 under `~/allelo-source-recovery-20261109/`:

- `author-e5-pinned/`: original D-E5 commit `2e70dcd171584217fc0cba45662ff7547b369619` with the original two-file task/CLI patch. Binary diff SHA-256 `1cae3dde4cdcecbfc0293bee9cd8957387eda23fb1eb32ad1f923df381fe0874`.
- `e120_source_e5_sol/`: original S3 wrapper bytes, all four hashes matching unchanged `preflight.py` constants.
- `automated-w2s-research-git/`: clean source checkout at `79a0562fa1a2c246048ed7c009f3684907987b05`; initial ideas/core tree matches `c3d3be8fee0ff7d28b082dc1a2cd239927bf6279ad4117e28a6c3623b643de25`.
- `author-e5-pinned/.venv/`: Python 3.12.15, all 94 original package versions. Actual `uv pip freeze` matches the original 1,653-byte record and SHA-256 `46b3002fc1f542e5da7eee19bdda03e3a7564677dd3c8ce3f5a619d6d045b3d1`. No runtime-pin exception was used.

Provenance receipts: `RECOVERY_RECEIPT.json`, `author-recovery-evidence/AUTHOR_RECOVERY_RECEIPT.json`, and `environment-recovery-evidence/environment.json`. The freeze was recovered from the original installation transcript and accepted only after matching the historical hash.

## Explicit host adaptation

`launcher.py` now reads `ALLELO_SOURCE_ROOT` before importing the original wrapper. Its children retain the original names above. `ALLELO_CREDENTIAL_FILE` selects the existing dotenv file. Unset variables retain the historical Linux defaults. Blank/missing explicit overrides fail, and source validation is unchanged. Importing no longer generates bytecode inside preserved source directories.

These are the only changes to the ten-file runtime package beyond commit `cfb3bcb746b38d78c041e686806ef8c26a934c1d`. The other nine package files, including the treatment template, hooks, adapter and A stimulus, remain byte-identical. Tests outside the runtime package now accept the explicit host root and assert the exact Nexus-4 treatment delta rather than the stale base-only prompt. The card distinguishes current treatment from historical base status.

The default Mac filesystem ignores filename case. A separate user-owned, case-sensitive APFS sparse image removes that avoidable difference for both per-attempt W2S state and source temporary workspaces. It is currently mounted at `~/allelo-source-recovery-20261109/case-sensitive-workspaces/`. Both attempts and temp directories passed independent case-distinction probes. The image was created with a 1 GiB maximum for preflight and then expanded to 8 GiB under the launch captain's capacity authorization. Its volume UUID, mount path and offline evidence hashes survived the resize. See `/Users/andyphu/allelo-source-recovery-20261109/preflight-evidence/CAPACITY_RESIZE_RECEIPT.json` for the backup and before/after checks. The 8 GiB maximum is not a worst-case twenty-run guarantee: pause new dispatch and alert the captain if free image space falls below 2 GiB or Mac free space below 10 GiB; do not interrupt a live run without operator direction.

## Commands and operational rules

In a shell on mm-west-2:

```sh
source ~/allelo-source-recovery-20261109/activate-mm-west-2.sh
cd ~/allelo-experiments
python experiments/A-E160/package/preflight.py \
  --author "$ALLELO_SOURCE_ROOT/author-e5-pinned" \
  --w2s-source "$ALLELO_SOURCE_ROOT/automated-w2s-research-git" \
  --source-package "$ALLELO_SOURCE_ROOT/e120_source_e5_sol"
```

This command performs no model call. The activation script sets process-start `TMPDIR`, Python/PYTHONPATH, explicit source paths and the **path** to the existing Daybreak credential file. It does not print credentials or load them for an offline check. Credentials remain outside the repository and recovery evidence. The script refuses to proceed if the mounted temp directory is missing.

For a later authorized preparation, choose a fresh `--attempt` beneath the mounted `case-sensitive-workspaces/attempts/`, and keep the same process-start `TMPDIR` for the frozen launcher. Do not move prepared attempts: receipts pin absolute paths. Never reuse either offline rehearsal as a counted attempt. Their `OFFLINE_ONLY.json` markers identify synthetic outputs and modified post-delivery workspaces. Do not detach the image while an owned process uses it.

If the image is detached, its receipt contains the verified reusable attach command and volume identity: `environment-recovery-evidence/case-sensitive-workspace-receipt.json`. No Linux `/home/...` compatibility symlink or source-check bypass was introduced.

## Evidence and results

Canonical summary: `preflight-evidence/FINAL_PREFLIGHT_RECEIPT.json`.

Final consumer evidence is under `case-sensitive-workspaces/attempts/offline-preflight/`:

- `prepare_receipt.json`: the actual launcher preparation path passes unchanged original-source verification and freezes all ten runtime files. Package digest `85931b852211c3ee85643a0e93026b6ba6a9b7b8f96d2b938aaf4a0b71604938`.
- `first_b_input.json`, `first_b_system_prompt.txt`, `source_b_system_prompt.txt`: exact rendered source input with only the committed Nexus-4 goal suffix added. EM research assignment remains intact; canary stripped by the source loader.
- `first_b_responses_request.json`: actual Inspect/OpenAI serialization captured by replacing the SDK create boundary before HTTP. It preserves the prompt, session message and nine source tools, requests `gpt-6-sol`, and injects `access_programs.cyber=daybreak_blue`.
- `mock_events.jsonl`, `mock_delivery.json`, `mock_logs/`, `mock_workspace_final/`: two mock B sessions, six synthetic model responses, two fixed-A deliveries. Actual source Read results for posts 3 and 4 match saved forum files and occur in subsequent B inputs. Installed A code hashes match the parent stimulus. These prove installation and ingestion, not a behavioral pivot or model code execution.
- `workspace_paths.json`: actual source workspace, forum and resolved W2S ideas all lie on the case-sensitive mount.
- `offline_route_receipt.json`: zero provider/HTTP calls. Synthetic mismatch tests exercise rejection of wrong request model/program and wrong response program. This is not a verified live served response.

Seven adapter checks and seven failure-path checks also pass. Import-only path tests reject malformed overrides and a tampered wrapper. Original source diff and freeze remain unchanged after checks. The earlier default-filesystem rehearsal is preserved under `preflight-evidence/offline-rehearsal/` as prior evidence; the mounted rehearsal supersedes it for writable-path configuration.

## Remaining limits and owner decisions

The runtime is Darwin arm64 with native wheel/interpreter binaries and host-specific absolute paths, rather than the original Linux machine. Matching Python and all dependency versions plus the observed source/tool/request behavior does not establish universal binary or behavioral equivalence. These host differences are explicit and are not the scientific prompt lever.

A real served Sol/Daybreak response and account entitlement are untested here. The existing counted-canary/release process must verify them; no extra paid test was silently added. Exact prompt/release approval belongs to the current experiment owner. The source recovery and technical preflight do not declare a result, change the denominator, authorize comparator trials, or launch the twenty-run batch.
