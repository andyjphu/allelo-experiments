# Base Allelo

This branch contains one condition package: fixed A with B's original D-E5 research goal. Its A posts and code come from the A-E130 batch02 fixed-A condition (historically called E5a). The package was copied from A-E160 after its run and the Nexus identity sentence was removed. No trial of this branch has been authorized or run.

The B-visible goal and frozen A stimulus correspond to the historical fixed-A baseline. The runner is later A-E160 infrastructure, including the 100-response cap, macOS path override, and frozen Jinja template. It is not a byte-identical copy of the historical E5a package or a newly measured control.

The ten-file runtime package is under `environment/package/`. It depends on the pinned D-E5 author source (`2e70dcd171584217fc0cba45662ff7547b369619`), E120 wrapper, and W2S checkout (`79a0562fa1a2c246048ed7c009f3684907987b05`) supplied outside this branch. The full upstream source checkout, other experiment conditions, custom test fixtures, and raw traces are not included here. Provenance checks in the runner are runtime safeguards; they are not tests added to the source author's repository.
