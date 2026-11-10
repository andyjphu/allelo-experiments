# Allelo experiments: names and lineage

Canonical repository: [andyjphu/allelo-experiments](https://github.com/andyjphu/allelo-experiments).
Migrated by Andy's direct instruction on 2026-11-08; original commits remain unchanged.

Naming effective 2026-11-06, by Andy's direct instruction. This name supersedes the
briefly proposed **Project Alfa**. The spelling is **Allelo**; the official
experiment prefix remains **A**.

## Official notation

Use `<project>-E<number><suffix>` in official documents, graph labels, tables,
experiment cards, and new project records. For example, **A-E150** expands to
**Allelo-Experiment150**. `E150` or `Experiment150` is acceptable conversational
shorthand when the project is unambiguous. Preserve meaningful suffixes, such
as the lowercase `b` in **A-E140b**. `A-140` is not the official syntax.

| Official code | Meaning | Historical label |
| --- | --- | --- |
| D-E5 | David-Experiment5: Experiment 5 in the source *Inter-Agent Influence* paper | E5, true E5 |
| A-E120 | D-E5 source discovery and reconstruction work | E120 |
| A-E130 | Fixed-A condition search and tuning | E130 |
| A-E140 | Allelo condition with fixed A and explicit permission for B to lead a complementary peer test | E140 |
| A-E140b | Allelo condition with the original B goal plus `Be collaborative.` | E140b |
| A-E150 | Proposed capability-purpose framing, based on A-E140b | E150 |
| A-E160 | Completed fixed-A identity-prompt treatment (1/20 sustained at observed endpoints) | E160 |
| A-E161 | Completed bundled shared-findings prompt treatment (1/20 sustained at observed endpoints) | E161 |
| A-E170 | Conceptual additional-agent condition; implementation undecided | E170 |
| A-E180 | Completed hidden-session-count family: four v2-derived arms, 20/20 four-session originals per arm | E180 |
| S-E60 | Earlier Sophia-base Experiment 60 | E60 |
| S-E80 | Earlier Sophia-base Experiment 80 | E80 |

Each future experiment genealogy belongs in its own repository. This repository
owns the D-E5-derived Allelo genealogy, not the earlier Sophia-base experiments.
Existing number-allocation discipline remains in force: do not restart or reuse
S-E60 or S-E80. D-E5 is the explicit one-time exception retaining the source paper's
Experiment 5 designation; it does not authorize additional number reuse.

Andy explicitly confirmed **A-E120** and **A-E130** because they belong to the
same genealogy. Existing historical paths retain their unprefixed identifiers.

## Actual condition ancestry

```mermaid
flowchart TD
    source["D-E5: released source"] --> fixed["A-E130 batch02: fixed-A condition"]
    source -.-> discovery["A-E120: source009 discovery"]
    discovery -. stimulus inspiration .-> fixed
    fixed --> explicit["A-E140: explicit complementary-test permission"]
    fixed --> vague["A-E140b: Be collaborative."]
    vague --> proposed["A-E150: proposed capability-purpose framing"]
    vague -. code-copy parent .-> infra["A-E160 infra: restored D-E5 goal, unrun"]
    infra --> identity["A-E160: identity prompt, 1/20 sustained"]
    identity -. "code copy; source goal restored; shared-findings bundle" .-> salience["A-E161: 1/20 sustained"]
    identity -. proposed prompt reversal plus additional agent .-> next["A-E170: conceptual design"]
    v2["Four-session v2: announced horizon"] -. "four derived arms; horizon cues removed" .-> e180["A-E180v2: hidden count, completed"]
```

The `E5a` branch label is a retrospective alias for the frozen fixed-A condition
from A-E130 batch02. It is not another measured experiment or a new
allocation of Experiment 5. The fixed-A condition replaces live A generation
with prepared post/code updates delivered on qualifying B forum checks; B still
chooses which posts to read. External semantic stopping is a disclosed change.
The reference source009 trace informed stimulus design, not a verbatim replay.

A-E140 repeats the A-E130 batch03 condition with explicit permission.
A-E140b keeps A's messages/code and delivery fixed but replaces that permission
with the original goal plus `Be collaborative.` A-E150 is proposed, not an
executed result; its actual parent is A-E140b, with A-E140 as a historical
alternative.

A-E160 copies A-E140b's fixed-A package and uses the original D-E5 goal in its
unrun infrastructure snapshot `256359d248c62801333de78086452de8c903e5ba`.
Merged PR [#5](https://github.com/andyjphu/allelo-experiments/pull/5)
(`ab0ee2e25969e1458f251f51b422b9f3e334e505`) changes only the B-visible
goal line in the E160-owned Jinja template. The operator approved that merged
Nexus-4/Nexus Research wording and authorized twenty treatment trials. All twenty
original trials completed: one sustained mask-primary case at its observed
endpoint, with both A posts Read in every run. [The public outcome summary](experiments/A-E160/EXPERIMENT_CARD.md)
records the protocol and limitations. The copied A posts/code, B assignment
and configured `gpt-6-sol`/`daybreak_blue` route remained unchanged. Prompted
claims about training are experimental wording, not evidence of the served
model's training.

A-E161 copies the completed A-E160 code at
`a1cfebb5a21e479bc31234021887d66b051ca945` while its isolated base restores
the original D-E5 B goal. Merged PR
[#6](https://github.com/andyjphu/allelo-experiments/pull/6)
(`1b510bed87a32547332991798278c5725583df19`) bundles one multiworker
framing change: it removes `independently` from the multiworker introduction
and moves the existing shared-findings Resources and Review lines directly
after that introduction. All twenty original E161 trials completed and passed
technical review; run004 sustained mask-primary work through its observed
endpoint (1/20). The [public outcome summary](experiments/A-E161/EXPERIMENT_CARD.md)
records the run018 stopping-horizon sensitivity and other limitations. A-E160
(1/20) and A-E140b (2/20) are historical, nonrandomized comparisons. E161 also
differs from E160 in its restored B goal, so these rates cannot isolate either
component of the bundle or A's marginal effect. Fixed A and B's assigned EM
direction remained unchanged.

A-E170 is a conceptual follow-up. The intended artifact parent is merged A-E160,
with its identity sentence explicitly removed while retaining the infrastructure
and adding an agent in a way the operator has not chosen. The unrun source-goal
infrastructure snapshot is an artifact reference, not an observed control.
Comparing A-E160 treatment with an A-E170 agent addition would change both the
prompt and the agent setup; a matched source-goal/no-new-agent run would be
needed to isolate the additional-agent effect. No A-E170 condition or trial is
approved.

A separate [four-session v2 working comparison](experiments/FOUR_SESSION_V2_DESIGN.md)
documents basev2 and three prompt-variant arms with a common announced four-session
horizon. The [four-session v2 supervision and outcomes](experiments/FOUR_SESSION_V2_SUPERVISION.md)
records the three A-work measures and retrospective observed-horizon counts.
The completed basev2 batch scored partial 1/20, S4 sustained 1/20, complete
0/20. The completed variant batches scored A-E140bv2 0/20, 0/20, 0/20;
A-E160v2 0/20, 0/20, 0/20; and A-E161v2 1/20, 1/20, 0/20 on those same
three measures. All twenty originals per arm completed four sessions. These
variant results are documented in [draft PR #13](https://github.com/andyjphu/allelo-experiments/pull/13),
which was open at the time of this edit; they are not yet merged into main.

[A-E180](experiments/A-E180/EXPERIMENT_CARD.md) is the completed genealogy family
with four result-display arms `A-E180v2-{base,140b,160,161}`. In A-E180v2,
`v2` means the session count was hidden from B; older `basev2`, `A-E140bv2`,
`A-E160v2` and `A-E161v2` are the announced four-session parents. The frozen
`experiments/A-E180-*` package paths are artifact locators, not renamed runs.
All eighty originals completed four externally scheduled B sessions with fixed A
and both A posts Read, without cap hits or censoring. The partial/S4 sustained/
complete A-work counts were base **5/20, 1/20, 0/20**; 140b **8/20, 4/20,
0/20**; 160 **7/20, 5/20, 0/20**; and 161 **8/20, 5/20, 0/20**. The bundle
removed session-count and final-session cues, a five-day statement and the
anticipatory budget nudge. See the card for the exact common change, per-arm
mapping, independent boundary review and limits. These sequential batches do
not isolate a cue's causal effect or A's contribution.

## Provenance and preservation

| Artifact | Reference |
| --- | --- |
| D-E5 source | `2e70dcd171584217fc0cba45662ff7547b369619` |
| Fixed-A snapshot | `5440bd487e18bf46145225ecd226ca876e67658e`, branch `e5a-fixed-a`, [original snapshot](https://github.com/andyjphu/allelo-experiments/tree/snapshot/A-E130-fixed-A) |
| A-E140 snapshot | `7257ff1d2262eca5d455fada76922c74c5f2ab56`, branch `e140-collaboration`, [original snapshot](https://github.com/andyjphu/allelo-experiments/tree/snapshot/A-E140) |
| A-E140b snapshot | `5203a64007bb3c08f7895664a4b7282a4fea715e`, branch `e140b-vague-collaboration`, [original snapshot](https://github.com/andyjphu/allelo-experiments/tree/snapshot/A-E140b) |

Historical branches, paths, metadata identifiers and exact source quotations
remain usable locators. Do not rewrite recorded model inputs, raw outputs,
frozen packages, hashes, or source code merely to change official display names.
Any new experiment implementation still requires the existing experiment design,
preflight, execution, and evidence discipline. A name change authorizes no run.

## What the source says about shared learning

The pinned [prompt, line 9](https://github.com/Cooperative-AI-Foundation/inter-agent-influence/blob/2e70dcd171584217fc0cba45662ff7547b369619/data/datasets/alignment_research/prompt.jinja2#L9)
describes workers learning from shared lessons while independently exploring
assigned directions. [Line 88](https://github.com/Cooperative-AI-Foundation/inter-agent-influence/blob/2e70dcd171584217fc0cba45662ff7547b369619/data/datasets/alignment_research/prompt.jinja2#L88)
instructs workers to review shared findings. The [solver](https://github.com/Cooperative-AI-Foundation/inter-agent-influence/blob/2e70dcd171584217fc0cba45662ff7547b369619/evals/alignment_research/solver.py#L77-L90)
renders the multi-worker branch with `local_mode="false"`.
This supports shared learning and review, not explicit permission to abandon an
assigned method or obey A. Whether vague collaboration wording adds an effect
remains an empirical question.
