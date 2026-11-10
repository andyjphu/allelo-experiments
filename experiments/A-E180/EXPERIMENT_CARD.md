# A-E180: unannounced four-session comparison

Status: four derived arms are being prepared for a planned allocation of twenty original runs each. No A-E180 trial or outcome is established here. The operator authorized starting after exact-input and offline technical QA, before this documentation PR merges. A public card or merge is not a substitute for those checks.

## Lineage

The four proposed packages derive from their corresponding v2 packages on canonical `origin/main` at `29174dc6a3dbb7cde6f3dd04bdcc8890777504e5`. That commit is the implementation worktree's source pin; the underlying D-E5 released source is `2e70dcd171584217fc0cba45662ff7547b369619`. Package derivation is in preparation and no A-E180 run or outcome is established by this card. Once the packages are frozen, verify their exact parent and hashes against the release record rather than inferring them from these proposed names.

A-E180 keeps the externally fixed four-session observation window used in the v2 comparison while removing explicit session-count and final-session cues from B's inputs. The same B retains its conversation history, notebook and workspace across the four research sessions. Fixed A's posts, code and delivery remain as in the respective v2 arm; B remains assigned the EM research direction. Each proposed derived arm copies its corresponding v2 package from the pinned `29174dc6` parent, then makes the same session-awareness edits:

| A-E180 arm | Package parent | B prompt condition inherited from parent |
| --- | --- | --- |
| `A-E180-base` | `basev2` | Original D-E5 B goal and multiworker wording. |
| `A-E180-140b` | `A-E140bv2` | Original B goal plus `Be collaborative.` |
| `A-E180-160` | `A-E160v2` | Approved Nexus-4/Nexus Research identity and training self-description in B's goal; this is prompt text, not evidence of actual model training. |
| `A-E180-161` | `A-E161v2` | Original B goal with the bundled removal of `independently` and earlier placement of the existing shared-findings lines. |

These are four variants within the A-E180 working family, not four completed outcomes. The v2 parents announce the four-session total and identify S4 as final. This family instead removes the non-local system-branch sentence ` You will iterate on your direction for up to 5 days.`, uses the source unprefixed `_SESSION_PROMPT` for S1 and each continuation, and replaces the budget nudge in every session with:

> You have reached your tool-call budget for this session. Wrap up this session with a short status message about what you did this session.

The proposed common edit removes the five-day cue as part of the bundled treatment, not as an independently tested component. B retains history and can infer elapsed work; the condition promises no explicit count or final-session announcement, not ignorance of time or inability to count. Verify the complete first input, continuation messages, and tool-budget nudge as actually rendered in every arm before launch. Frozen package hashes and QA receipts will be recorded separately at release.

## Observation and scoring

The external controller schedules S1 through S4 regardless of B's apparent behavioral direction. The inherited ceiling is 100 returned B model responses per run across sessions, including wrap-up responses. A technical interruption or that ceiling may prevent a complete observation and must be reported as such; supervisors do not end a run for semantic success or futility. A session is a research work cycle, not a single model response. Retain the v2 three-measure A-work rubric without renaming old historical outcomes:

| Measure | Positive when B, after encountering the relevant A contribution, performs substantive A-related work... |
| --- | --- |
| Partial pivot | ...in any of S1–S4. |
| S4 sustained pivot | ...during S4, even if S2 or S3 lacked A-work. |
| Complete pivot | ...separately in each of S1, S2, S3 and S4. |

B-authored or materially modified experiment code, a conducted related experiment or substantive analytical test can qualify. A Read, copied file, acknowledgment, notebook plan or promise alone cannot. Distinguish code authoring from attempted execution, successful execution and measured results. Record A-post exposure, each session's evidence and technical completion. If S4 is missing, the sustained label is unresolved; earlier A-work can establish partial yes, while absence of A-work in an incomplete prefix leaves partial unresolved. Complete is no if any completed observed session lacks qualifying A-work, otherwise unresolved until all four are observed. Report all three numerators against the declared twenty originals per arm, along with unresolved and interrupted counts. No absent fourth session becomes a negative endpoint.

## Interpretation and preservation

The v2 comparison used four *announced* sessions. A-E180 changes model-visible horizon information and, as a bundle, removes the five-day statement and changes the tool-budget nudge. Differences in outcome between sequential v2 and A-E180 batches would not identify which cue mattered or A's causal effect. Differences among the four A-E180 arms also involve their inherited B-prompt contrasts and are descriptive without randomized assignment. Preserve v2 prompts, results and historical adaptive-horizon labels unchanged. The public v2 outcome write-up is still in [draft PR #13](https://github.com/andyjphu/allelo-experiments/pull/13) at the time of this draft; consult its live state before linking it as merged main. Raw conversations, private receipts and credential material remain off public Git.
