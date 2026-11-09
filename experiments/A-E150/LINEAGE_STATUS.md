# Project Allelo: D-E5 to A-E150 Git lineage, updated 2026-11-06

Canonical repository: `https://github.com/andyjphu/allelo-experiments`, migrated from
`project-allelo` on 2026-11-08. The released D-E5 source remains pinned at
`2e70dcd171584217fc0cba45662ff7547b369619`. Original snapshot commits and their
experiment-file trees are unchanged. The review branches also inherit the new
repository index and CodeRabbit configuration.

| Layer | Commit/branch | Draft PR | Content | Verification |
| --- | --- | --- | --- | --- |
| Fixed-A snapshot (historical `E5a` alias) | `5440bd487e18bf46145225ecd226ca876e67658e`, `e5a-fixed-a` | [#1](https://github.com/andyjphu/allelo-experiments/pull/1), base `main` | Frozen A-E130 batch02 package, original B goal; no new numbered experiment | Twelve manifest file hashes and byte comparison with archived package |
| A-E140b current parent | `5203a64007bb3c08f7895664a4b7282a4fea715e`, `e140b-vague-collaboration` | [#3](https://github.com/andyjphu/allelo-experiments/pull/3), base `e5a-fixed-a` | Exact frozen A-E140b package: original B goal plus `Be collaborative.`; A content unchanged | Twelve manifest hashes, byte comparison with archived package, ten Python syntax checks, `git diff --check` |
| A-E140 historical alternative | `7257ff1d2262eca5d455fada76922c74c5f2ab56`, `e140-collaboration` | [#2](https://github.com/andyjphu/allelo-experiments/pull/2), historical review | Exact frozen A-E140 package with explicit peer-test permission | Preserved branch and prior verification; outside A-E150 lineage |
| A-E150 | Design documents originally committed at `68ff6c0`; no implemented condition | [Design PR #4](https://github.com/andyjphu/allelo-experiments/pull/4) | Capability-purpose frame, pending exact prompt sign-off and readable-source diff review | No model call or rollout |

The draft PRs belong to the standalone review repository, not the source publisher. Their bases are the actual condition parents. Metadata-only merge commits retain the original history without adding repository-document changes to each condition diff. The current branch chain is D-E5 main → fixed-A snapshot (`E5a` alias) → A-E140b → proposed A-E150. A-E120 discovery and A-E130 tuning belong to this genealogy, but are not additional commits in that branch chain. The earlier A-E140 commit and branch remain available as historical evidence, while its PR is closed. The fixed-A and A-E140b packages retain archived host-specific paths and A-E130 provenance where these were frozen; the PR descriptions explicitly say they are condition snapshots rather than portable new evaluations.

The **A-E140b-based** proposed A-E150 first system text and one-line diff are in `review/E150_proposed_from_E140b_system_normalized.txt` and `review/E140b_SYSTEM_PROMPT.diff`. Earlier A-E140-based preview files are superseded. The proposed `share_finding` help phrase is in `PROMPT_SIGNOFF.md`. A first mechanical preview of the W2S AAR-name replacement was rejected for awkward duplicated prose; `review/W2S_VISIBLE_SOURCE_PROPOSAL_v1.diff` is the improved **design preview only**, still awaiting review. Neither has been installed in the fork. The design-document commit and review PR do not install or approve the proposed condition. Exact text review and package verification remain pending before implementation or rollout.

## Current design location

The current review branch is `a-e150-design-review` in `allelo-experiments`,
with documents under `experiments/A-E150/`. The source design-document commit
`68ff6c0` remains unchanged under `snapshot/A-E150-design`. The earlier linked
worktree and `research/E150/` packet remain preserved migration references.
