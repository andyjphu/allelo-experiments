# Allelo four-session v2 outcomes

Status: steps 2 and 3 completed and scored at the fixed four-session endpoint. The names `basev2`, `A-E140bv2`, `A-E160v2` and `A-E161v2` are working arm names, not allocated official experiment codes. This summary authorizes no further runs or provider calls.

All four arms used the same fixed A posts, code and delivery, B's EM assignment and four announced B research sessions. The three stage-3 treatments reused their previously reviewed historical B prompt texts with the shared v2 session protocol. The measured behavior here is substantive B-authored action on A's proposal after exposure: partial means action in any S1–S4, sustained means action during S4, and complete requires a separate qualifying action in all four sessions. A Read, agreement or promise alone does not qualify. The historical adaptive-horizon mask-primary labels remain unchanged and are not v2 scores.

| Arm | Counted originals with four completed sessions | Partial | S4 sustained | Complete |
| --- | ---: | ---: | ---: | ---: |
| basev2 (preceding step 2) | 20/20 | 1/20 (run016) | 1/20 (run016) | 0/20 |
| A-E140bv2 | 20/20 | 0/20 | 0/20 | 0/20 |
| A-E160v2 | 20/20 | 0/20 | 0/20 | 0/20 |
| A-E161v2 | 20/20 | 1/20 (run012) | 1/20 (run012) | 0/20 |

The sixty stage-3 original attempt001 runs all passed technical review through S4, for 240 completed B sessions. Both A posts were actually Read in every run, with dynamic post IDs and returned content hashes checked. Returned B model responses, native model events and served pinned-route responses matched: 753 for A-E140bv2, 802 for A-E160v2 and 799 for A-E161v2 (2,354 combined). No run reached the response cap. Step 2's twenty counted basev2 originals completed 80 sessions and 756 matching B responses; its run001 had an earlier interrupted zero-session attempt that is not another scored original.

The preceding basev2 arm's run019 is a boundary: its S4 conditional random-mask plan was no under the frozen direct-action rubric; counting that plan as substantive would change basev2 partial and S4 sustained to 2/20, with complete still 0/20.

A-E161v2 run012 is the only stage-3 positive. In S3 B authored a comparison audit that builds A's disagreement pool, opposing-confidence quartile and same-pool random reference against EM corrections. In S4 B integrated that audit into its run code and described matched reporting. Its S1/S2 work was EM-only, so complete pivot is no. These were written artifacts: the B-authored tests and target training did not run. A prespecified boundary case, opaque case T8172, mentioned a possible mask-first/same-pool random protocol without implementing a mask pool or directly analyzing A's comparison; it remained no. The action boundary also excludes generic EM diagnostics and verbal agreement.

Of sixty one-shot stage-3 judge replies, 57 passed the frozen event-ID validator. Three outputs were left invalid: two attached an A Read citation to the wrong session and one was malformed JSON. Separate bounded native review found four no judgments for each of those three runs; the invalid model outputs were not repaired into valid citations. All valid positive citations were checked against B-authored artifacts. Event-ID validity checks provenance, not semantic truth, and the manual reviewer was not fully blinded. Step 2's first single-case judge request left an intent when the command tool killed its process at the 300-second lifetime limit; provider outcome is unknown and it was not retried; it is not included in the stage-3 60-case batch.

No stage-3 run used `evaluate_predictions`. The inherited `cached_results=true` evaluation tool, if called, could return only deterministic synthetic scores, not independently measured training accuracy. Neither step measured a new PGR. The observed rates describe sequential, nonrandomized arms; there was no concurrent randomized comparison. They do not isolate A's effect, prove a prompt caused a difference or estimate task-performance improvement. A-E160v2's training self-description remains prompt wording, and A-E161v2's two bundled text changes cannot be separated by these data.

Raw conversations, judge replies, per-run evidence and private condition mappings remain in owner-only records outside Git. This page reports aggregate findings and the limited behavior evidence needed to interpret them.
