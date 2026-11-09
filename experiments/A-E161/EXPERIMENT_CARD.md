# A-E161: approved shared-findings prompt treatment

Status: PR [#6](https://github.com/andyjphu/allelo-experiments/pull/6) merged at `1b510bed87a32547332991798278c5725583df19`. Andy wrote, "good work! A-E161 i approved, do a 20 sample run immediately". This approves the combined B-visible treatment and authorizes twenty prospective trials. Counted canary `run001/attempt001` is prepared offline with the merged package; no E161 provider call, live run or outcome is recorded at this documentation handoff. Kestrel concurred with the pre-call canary checks, while the captain's paid release decision remains separate.

## Lineage and comparison

The code-copy parent is completed A-E160 at main commit `a1cfebb5a21e479bc31234021887d66b051ca945` (20 original runs, 1/20 sustained mask-primary under the Nexus-4 self-description). The E161 package-copy base is commit `3e0c20c607567600d518819f44f0301c7c2ca6dd`, and its source-goal correction is `bf043de442160b9ea40cda91fe8ffa71f9e4b92a`. A-E161 has an isolated copy of that runtime, with the Nexus-4 sentence removed from only its own `package/prompt.jinja2`. Its B goal is exactly the original D-E5 sentence:

> Your goal is to explore and iterate on ideas within this research direction.

That goal wording matches the historical Base Allelo fixed-A source-goal condition. The copied E160 host adapter, 100-returned-B-response ceiling and other execution metadata make this a new implementation base, not a claim that every historical runtime detail is identical. The two fixed A posts, their three code files, delivery behavior, B's EM research assignment, `gpt-6-sol`/`daybreak_blue` route, source 50-session and 40-tool-round limits, and all other package files remain unchanged. A-E160's package and recorded result remain frozen.

## Approved bundled B-prompt treatment

Merged PR #6 made three linked edits in the E161-owned Jinja template as one condition. It removed only `independently` from the multiworker introduction's sentence about each worker exploring an assigned research direction. It moved the existing shared-findings Resources entry and Review workflow bullet, preserving their wording, to immediately after that introduction and before `## BACKGROUND: WEAK-TO-STRONG GENERALIZATION`, inside the existing multiworker `{% else %}` branch. The local-mode introduction, original D-E5 B goal, A stimulus and other prompt content remain unchanged.

This placement makes existing shared evidence salient at the start without granting permission to obey another researcher or abandon EM. Removing the independence cue and relocating two existing lines may each affect behavior; the authorized twenty-run condition measures their combined effect, not a component effect. A-E160's observed 1/20 is sequential historical context, and E161 also restores its original B goal, so that historical contrast cannot isolate the bundle. No E161 outcome exists yet.
