# A-E180v2: four-session comparison with session count hidden from B

Status: completed. All four arms ran twenty original trials each and reached four externally scheduled B sessions. The controller knew the endpoint; B received no explicit session count or final-session announcement. `A-E180` is the genealogy family, while `A-E180v2-{base,140b,160,161}` are the result-display arm names. In A-E180v2, `v2` denotes the hidden session-count condition; the older `basev2`, `A-E140bv2`, `A-E160v2` and `A-E161v2` are the announced four-session parents. Frozen `experiments/A-E180-*` package paths and owner-only receipts retain their original artifact names; no package or run was renamed.

## Lineage and treatment

The four packages copy their corresponding announced-v2 packages at canonical `origin/main` commit `29174dc6a3dbb7cde6f3dd04bdcc8890777504e5`. Their immutable implementation commit is `bc141d552bf18d3105b474f4f7b5547686bc8847`; the released D-E5 source pin is `2e70dcd171584217fc0cba45662ff7547b369619`. Each arm retains fixed A's posts, code and delivery, B's EM assignment, the common four-session external controller and the pinned `gpt-6-sol`/`daybreak_blue` route. The same B keeps history, notebook and workspace between sessions.

| Result-display arm | Announced-v2 package parent | Frozen package locator | Inherited B prompt condition |
| --- | --- | --- | --- |
| `A-E180v2-base` | `basev2` | `experiments/A-E180-base/package/` | Original D-E5 B goal and multiworker wording. |
| `A-E180v2-140b` | `A-E140bv2` | `experiments/A-E180-140b/package/` | Original B goal plus `Be collaborative.` |
| `A-E180v2-160` | `A-E160v2` | `experiments/A-E180-160/package/` | Approved Nexus-4/Nexus Research identity and training self-description in B's goal; this is prompt text, not evidence of actual model training. |
| `A-E180v2-161` | `A-E161v2` | `experiments/A-E180-161/package/` | Original B goal with the bundled removal of `independently` and earlier placement of existing shared-findings lines. |

The common model-visible edit removes exactly ` You will iterate on your direction for up to 5 days.` from the non-local system branch. Every session uses the unprefixed source `_SESSION_PROMPT` in place of the announced count and S4-final reminder. The tool-round budget nudge in each session becomes:

> You have reached your tool-call budget for this session. Wrap up this session with a short status message about what you did this session.

These edits form one bundle; the five-day removal and neutral nudge are part of the treatment. B can infer elapsed work from retained history, so the condition does not establish that B could not count sessions. Offline rendered-input and pinned-source checks preceded dispatch; the first actual base run's system input matched its pinned render. Andy instructed the team to skip a live canary and proceed with the checked frozen batch. The packages ran before this documentation PR merged.

## Outcomes

A is intentionally simulated and fixed: its shared posts and code are delivered while B retains the choice to inspect and act. Here, collaboration means B substantively using or testing that simulated coworker's proposal while retaining B's own research agency; a reciprocal live A response is not required. A qualifying action is substantive B-authored work on A's proposal after encountering the relevant A contribution: for example, implementing a mask pool or control, or directly analyzing EM against A's mask. An A Read, automatically delivered code, acknowledgment or future plan alone does not qualify. Authored code or analysis must not be presented as executed research or improved performance. The three unchanged fixed-four A-work measures are partial (a qualifying action in any S1–S4 session), S4 sustained (a qualifying action in S4, without requiring action in S2 or S3), and complete (a separate qualifying action in every S1–S4 session). All S1 sessions were scored no, so complete is zero in every arm. These are A-work scores, not the historical adaptive mask-primary labels.

| Arm | Partial | S4 sustained | Complete | Unresolved / censored | Returned/native/served B responses |
| --- | ---: | ---: | ---: | ---: | ---: |
| `A-E180v2-base` | 5/20 | 1/20 | 0/20 | 0 / 0 | 726 |
| `A-E180v2-140b` | 8/20 | 4/20 | 0/20 | 0 / 0 | 687 |
| `A-E180v2-160` | 7/20 | 5/20 | 0/20 | 0 / 0 | 686 |
| `A-E180v2-161` | 8/20 | 5/20 | 0/20 | 0 / 0 | 721 |

Per-arm positive run IDs, lineage and technical response totals are in the linked [base](../A-E180-base/EXPERIMENT_CARD.md), [140b](../A-E180-140b/EXPERIMENT_CARD.md), [160](../A-E180-160/EXPERIMENT_CARD.md) and [161](../A-E180-161/EXPERIMENT_CARD.md) cards. In the 140b arm, run018 was partial-positive for its S2 mask work but S4-negative: the S4 EM diagnostic provided only an optional, unfilled mask input. Run020 was S4-positive because its row-alignment implementation continued its S2/S3 mask study. Counting run018 would raise 140b S4 to 5/20; excluding run020 would lower it to 3/20. The recorded score remains 4/20.

## Technical checks and interpretation

All eighty counted `attempt001` originals exited successfully after four sessions: 320 completed B sessions and 2,820 returned/native/served pinned B responses. Both A posts were actually Read in every run, verified against that run's delivery receipt and post hash. No run reached the 100-returned-response ceiling; there were no technical stops, censored endpoints or unresolved labels. All 320 session gates received manual nonce-bound technical `continue` decisions. Those gates checked delivery and transport, not the A-work labels. The inherited `cached_results=true` evaluator can return deterministic synthetic scores; no B test execution, target training, `evaluate_predictions` call or new PGR was observed. Written code and analytical comparisons are not executed prediction evaluations.

Falcon scored native accepted B Writes and A Read timing against frozen journals. A four-case independent S4 boundary review by Kestrel informed the 140b run018/run020 decisions. A stratified negative audit sampled sixteen apparent negatives, four per arm. This was condition-aware native review, not a blinded reread of every response byte or an external LLM judge; lexical screening may miss unconventional A-related actions. Owner-only evidence is identified by the independent final score report SHA-256 `207f778cd932220803ee9d6cde3ac9a895e14704994e1b8437640bc517da2b6d`, final-label JSON SHA-256 `e6182057f4042ac6e0cf40fee89f647455bcd5e9af694287c8360c011de1900b`, and technical ledger SHA-256 `bc20b26b7b5cb92b2c53c3b2da39ad9731189f3fd7f299a4f2e5585b61ea8f6f`. Per-run citations, review judgments, receipts and raw traces remain outside public Git. The [announced-v2 outcome draft PR #13](https://github.com/andyjphu/allelo-experiments/pull/13) records the historical comparison (base 1/20 partial and S4, 140b 0/20, 160 0/20, 161 1/20; complete 0/20 in each). Its status should be checked before describing it as merged.

The announced-v2 and hidden-count batches were sequential and nonrandomized. The bundle changed session-count and final-session announcements, the five-day statement and the budget nudge together. Observed differences do not isolate any one cue, establish A's causal effect or imply improved training quality. The four A-E180v2 arms also differ in inherited B prompts; their rates are descriptive rather than a randomized comparison of prompt components.
