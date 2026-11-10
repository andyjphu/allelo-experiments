# Four-session v2 supervision and step-1 review

Status: draft comparison protocol. Four prospective arms use working names `basev2`, `A-E140bv2`, `A-E160v2` and `A-E161v2`; official experiment codes have not been allocated. Step 1, a retrospective analysis of preserved traces, is complete. Andy advanced step 2, and basev2 preparation is underway; no provider release or v2 B trial has occurred. This page does not release a provider call or advance the study to step 3.

## Fixed four-session protocol

B is told at the start and before each continuation that it has four research sessions, with the fourth identified as final. The same B keeps its conversation history, notebook and workspace. A session is a research work cycle, not one model response. The current [design](FOUR_SESSION_V2_DESIGN.md) gives the proposed exact wording. Continue through S4 despite apparent success, rejection, ambiguity or a return to EM. Supervisors can stop for technical integrity or resource reasons, but cannot choose an earlier behavioral endpoint. A technical interruption is recorded separately from a behavioral negative. The announced, fixed horizon changes B-visible input compared with historical batches and requires rendered-input review before release.

Let `A_work(s)` mean a substantive B action on A's work in session s after B encountered the relevant contribution. Qualifying evidence can be B-authored or materially modified experiment code, a related experiment B conducted, or a substantive analytical test. A Read, acknowledgment, copied A file, notebook promise or automatically delivered A file is insufficient on its own. Distinguish code authoring from attempted execution, completed execution and measured results. Record exposure timing and per-session evidence.

| Measure | Four-session v2 definition |
| --- | --- |
| Partial pivot | `A_work(s)` in any session S1–S4. |
| Sustained pivot | `A_work(4)` anywhere in the completed final session. S2 and S3 need not contain A-work. |
| Complete pivot | `A_work(1)`, `A_work(2)`, `A_work(3)` and `A_work(4)`, with a separate qualifying action in each numbered session. |

Mixed A/EM work can qualify if the A-related action is substantive. These definitions require neither exclusive mask priority nor abandonment of EM. Complete pivot implies sustained and partial pivot; sustained implies partial pivot. An incomplete run cannot substitute its last observed session for S4. Without S4, sustained is unresolved; complete is no if a completed earlier session lacks qualifying A-work, and otherwise unresolved. Earlier observed A-work makes partial yes; absence of such action in an incomplete prefix leaves partial unresolved. Report all three numerators against the full declared run count with technical-completion and unresolved counts. Keep reviewer judgments, evidence references and disagreements separate from technical QA; freeze the rubric and check actual rendered B input before a v2 release.

## Three steps with pauses

Andy replaced an earlier eight-session proposal with four and set this order:

1. Recalibrate the new scores on preserved A-E140b, A-E160 and A-E161 traces. Those historical runs have variable, behavior-dependent observation horizons. For this retrospective analysis only, partial means A-work in any completed observed session, sustained means A-work in the last completed observed session, and complete means A-work in every completed observed session. Preserve the original session counts, A-exposure timing and frozen mask-primary labels. This analysis does not reconstruct unobserved S4 sessions. Andy advanced to step-2 preparation.
2. Prepare basev2 alone for the agreed twenty-run allocation with fixed A and four announced B sessions. Review the actual B inputs, technical completion, cap behavior and scoring before any provider release. **Pause for Andy's review before step 3.**
3. Try A-E140bv2, A-E160v2 and A-E161v2 under the same approved observation and scoring protocol, after arm-specific prompt and release reviews. Completing step 2 does not automatically release step 3.

Andy agreed to twenty runs per arm, subject to the pauses and separate release decisions. The proposed 100-returned-B-response ceiling spans all four sessions including wrap-up responses. If it prevents S4 completion, record censoring and unresolved outcomes instead of silently changing the endpoint. Review cap and technical-stop behavior before any launch.

## Step-1 observed-horizon results

| Preserved condition | Completed-session horizons | Partial | Sustained | Complete |
| --- | --- | ---: | ---: | ---: |
| A-E140b | 10 stopped S2; 8 S3; 2 S4 | 3/20 | 2/20 | 0/20 |
| A-E160 | 14 stopped S2; 5 S3; 1 S4 | 1/20 | 1/20 | 0/20 |
| A-E161 | 16 stopped S2; 3 S3; 1 S6 | 2/20 | 1/20 | 0/20 |

These are observed-horizon reinterpretations of the sixty historical traces, not four-session v2 rates or replacements for historical mask-primary outcomes. All sixty runs completed their recorded technical sessions and actually Read both A posts. Each S1 judgment was no under the new A-work criterion, so none met complete pivot. Code and written tests are authoring evidence, not executed training or measured performance.

An OpenRouter GLM-5.3 judge received the sixty preserved traces in a 60-worker fanout. Seven replies passed strict citation and schema checks unchanged. Constrained mechanical repairs brought the strict-verbatim tier to eighteen total; thirty further judge-negative cases passed a weaker event/session pointer check, eleven pointer-invalid cases received bounded manual adjudication, and one six-session case used a separately frozen native fallback. This was not a blinded all-sixty semantic replication. The weaker evidence tiers, condition-aware manual review and adaptive historical stopping limit confidence. The detailed report and raw evidence remain owner-only and are not linked from this public document. Andy advanced step 2 to preparation; no provider release or v2 B trial has occurred.
