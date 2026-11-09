# Allelo experiments agent guide

The canonical repository is `andyjphu/allelo-experiments`. This repository owns the experiment genealogy derived from the source paper's
D-E5. Read [PROJECT.md](PROJECT.md) for official names, actual condition ancestry,
source commit references, and proposed versus executed status.

Use official project-prefixed experiment codes in current cards, reports, tables,
graphs, and new records: A-E120, A-E130, A-E140, A-E140b, A-E150. The source-paper
experiment is D-E5. Earlier Sophia-base experiments use S-E... . Do not reuse
existing experiment numbers; D-E5 retains the source paper number as the single
explicit exception. Historical E5a is only a fixed-condition snapshot alias.

New work in this genealogy belongs in this repository. Preserve experimental
code discipline: validated base, explicit actual parent, minimal declared
perturbation, reviewed design and model-visible text, frozen conditions, preflight,
and evidence-backed outcome reporting. A documentation or repository rename is
not permission to start experiments or bypass an outstanding sign-off.

Keep source prompts, frozen package manifests, raw traces, tool results, and
historical hashes unchanged when updating display names. Legacy artifact paths
and branch identifiers are locators, not new official experiment names. Record
intentional implementation changes separately from naming changes. Do not commit
credentials or private raw conversations for the purpose of making a viewer work.
