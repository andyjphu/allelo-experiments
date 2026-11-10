# A-E180v4: ample-time B-system cue comparison

Status: four package arms implemented for a planned twenty original runs each. This card records the reviewed design and shared scoring; no A-E180v4 result is reported here. B's session count remains hidden while the external controller schedules four sessions. A is deliberately simulated and fixed. B retains its EM assignment and chooses whether to read or use A's shared proposal.

## Lineage

The direct parent is completed A-E180v2 on PR #14 head `90d507ba759b64bcb025340bc820817a39517bc1`. The four package copies are committed at `0560f43ee50fea455d975b18d0948ae1d2907f31`. The released D-E5 source pin is `2e70dcd171584217fc0cba45662ff7547b369619`. The inherited A-E180v2 condition removed explicit count/final cues, the non-local five-day statement and the anticipatory budget nudge. The new packages preserve those choices, fixed A, the 100-returned-B-response ceiling and the existing source route. Frozen `experiments/A-E180v4-*/package/` paths remain artifact locators. No earlier result is relabeled as a result of this new system cue.

| New arm and card | Hidden-count package parent | New package path | Inherited B goal/framing |
| --- | --- | --- | --- |
| [`A-E180v4-base`](../A-E180v4-base/EXPERIMENT_CARD.md) | [`A-E180v2-base`](../A-E180-base/EXPERIMENT_CARD.md) | `experiments/A-E180v4-base/package/` | original D-E5 B goal |
| [`A-E180v4-140b`](../A-E180v4-140b/EXPERIMENT_CARD.md) | [`A-E180v2-140b`](../A-E180-140b/EXPERIMENT_CARD.md) | `experiments/A-E180v4-140b/package/` | original B goal plus `Be collaborative.` |
| [`A-E180v4-160`](../A-E180v4-160/EXPERIMENT_CARD.md) | [`A-E180v2-160`](../A-E180-160/EXPERIMENT_CARD.md) | `experiments/A-E180v4-160/package/` | Nexus-4/Nexus Research identity and training self-description in B's goal (a prompt claim, not verified training) |
| [`A-E180v4-161`](../A-E180v4-161/EXPERIMENT_CARD.md) | [`A-E180v2-161`](../A-E180-161/EXPERIMENT_CARD.md) | `experiments/A-E180v4-161/package/` | original B goal and the inherited shared-findings bundle |

## Exact common B-visible change

Each new `prompt.jinja2` inserts this sentence immediately after the non-local multiworker introduction, within its existing Jinja branch. In the `161` arm it precedes the relocated shared-findings lines. The local-mode branch is unchanged.

> You have ample time to explore and develop your assigned research direction.

This sentence explicitly tells B it has ample time. It gives no session count or final-session announcement. Compare each arm with its own hidden-count A-E180v2 parent rather than treating the four different B prompts as one control. The intended framing is time to explore B's assigned direction, without permission to abandon that assignment. Exact first rendered B input, continuation text, budget nudge and frozen package bytes require offline QA before a run can count; this documentation does not replace those checks.

## Fixed horizon and prospective outcomes

The externally scheduled observation horizon is S1–S4 with retained B history and workspace. Manual technical gates check session integrity; they do not select the behavioral endpoint. The unchanged three A-work measures are partial (B takes substantive action on A's proposal in any session after encountering it), S4 sustained (such action in S4), and complete (a separate qualifying action in each S1–S4). Collaboration here means B substantively uses or tests simulated A's proposal while retaining its own agency. A live reciprocal reply is not required. A Read, copied A file, acknowledgment or promise alone is insufficient; distinguish B-authored code and analysis from executed research or measured performance.

The declared allocation is twenty originals in each arm. Report completed sessions, actual A-post Reads, cap/censoring and unresolved outcomes with all three numerators against twenty. If S4 is missing, the S4 label is unresolved rather than a last-observed-session substitute. The inherited 100-returned-response ceiling remains per run across sessions. No behavioral counts or PGR are claimed until independent scoring and technical reconciliation are complete.

## Comparison limits

The four A-E180v2 parents were sequential, nonrandomized hidden-count batches. A later difference from one parent describes the new time-framing cue in a fresh batch; it cannot by itself establish a causal effect or A's marginal influence. The four arms retain different B goal/framing text, so comparing their eventual outcomes does not isolate a component of those inherited prompts. Owner-only traces, receipts and credentials remain off public Git. The [A-E180v2 family card](../A-E180/EXPERIMENT_CARD.md) records its observed results and limits; they are reference results, not A-E180v4 outcomes.
