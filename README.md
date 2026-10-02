# BCM4360 research

A working notebook for investigating open-driver support for the Broadcom BCM4360 in a MacBook Air and contributing small, reproducible improvements to existing projects.

**This is not a working driver, a new driver fork, or a firmware distribution.** The initial research reproduced userspace tests and inspected pinned source. It did not validate an experimental driver on our laptop.

## Start here

- [Deep research report, 2 October 2026](REPORT.md): architecture, project findings, reproduced counterexamples, and viability.
- [Frozen source manifest](evidence/SNAPSHOT.md) and [evidence index](evidence/README.md): exact revisions and what is intentionally omitted.
- [Roadmap](docs/ROADMAP.md): the first bounded contribution and later acceptance gates.
- [Air access setup](docs/ACCESS.md) and [hardware safety policy](docs/SAFETY.md).
- [Contribution workflow](CONTRIBUTING.md), [provenance policy](PROVENANCE.md), and [agent instructions](AGENTS.md).
- [Experiment record template](experiments/TEMPLATE.md).
- [Acceptance revalidation](experiments/2026-10-02-acceptance-revalidation.md): original public gate witness, host-test outcomes, and remaining integration/access blocks.

## Initial direction

Collaborate with the existing b43/mac80211 efforts rather than starting an entire driver again. Begin with host-only test correctness, then improve trace semantics and board-data coverage before attempting reviewed, board-specific hardware work.

The first candidate is the empty-input initialization-equivalence false positive observed in aleferri's tooling. Refresh upstream and confirm it still exists before preparing a patch. Equality of two empty dictionaries is not automatically a comparator bug. The authoritative initialization gate must refuse to claim successful initialization without sufficient evidence.

## Repository boundaries

| Committed here | Kept outside Git |
|---|---|
| Source-cited research notes and revision pins | Proprietary vendor objects and extracted firmware |
| Independently authored synthetic tests and specifications | Raw MMIO, packet, and network captures |
| Reviewed experiment records with sanitized findings | Private logs, credentials, machine identifiers, and board dumps |
| Patch descriptions and, after review, appropriately licensed patches | Upstream clones, build products, and VM/disk images |

The GitHub repository starts **private**. Private visibility is not permission to upload confidential or proprietary artifacts. Publication and licensing decisions require a separate review.

## Local checks

Git, Python 3, and optionally Make are enough. No radio, sudo, network access, or vendor input is required.

```sh
make check
make test
```

Without Make:

```sh
python3 -B tools/check_repository.py
python3 -B -m unittest discover -s tests -v
```

The checker covers tracked and non-ignored working files, local Markdown file targets, prohibited artifact paths, and a small set of credential markers. It is not a comprehensive secret scanner, license audit, or hardware test. Review the staged diff before every commit and push.

## Working on upstream code

Keep upstream checkouts outside this repository. Record their remote, exact commit, board target, file licenses, commands, and test results here. Changes intended for an upstream project belong in a focused contribution against that project, not an unreviewed amalgamation of several drivers.

Do not infer current project status from this historical snapshot. Do not turn a passing model into a physical-radio claim.
