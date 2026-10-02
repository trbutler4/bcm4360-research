# Provenance and licensing

## Initial contents

The initial report and text audits were prepared with Jcode during the 2 October 2026 research session. They preserve the distinction between locally reproduced userspace tests, inspected source, other authors' hardware evidence, and recommendations.

Copies in this repository replace workstation-specific paths with `/path/to/...` placeholders. Raw output, vendor inputs, extracted firmware, and upstream source trees are intentionally absent. This is a curated notebook, not a complete independently reproducible artifact bundle.

Short quotations, numeric findings, file locators, and pinned links refer to third-party projects. Their presence is not a license grant for the underlying implementation, capture, or firmware. The original survey also contains later addenda that supersede earlier limitations. Read each audit through its final addendum before drawing conclusions.

## No blanket license yet

No repository-wide license has been assigned. This avoids granting rights over material whose code, documentation, trace, and firmware provenance need different treatment. Choose an appropriate license for independently authored contributions before distributing them, with the owner's approval.

For future kernel patches, examine the relevant files and upstream rules. Linux accepts GPL-2.0-compatible code. A root license label alone does not establish the license of every inherited file. An SPDX tag alone does not establish clean provenance for copied vendor-derived material.

## Record for every imported or contributed item

1. Public source URL and exact revision, or a clear statement that the item was independently authored.
2. File-level license and the scope of any notices or copyright statements.
3. Source of the behavioral specification, including any contact with proprietary code or firmware.
4. Whether permission is needed to redistribute a trace, capture, dataset, or excerpt, and evidence that it was obtained.
5. Test commands, observed results, target board/chip, and the limits of those results.
6. Human review and the intended upstream destination.

Do not copy large portions of source here merely because they were accessible online. Keep upstream development in its own checkout or fork and link to the reviewed contribution.

## Firmware and reverse engineering

- Proprietary `wlc_hybrid.o_shipped` and derived D11/ARM images stay outside Git.
- Existing possession, local research use, a checksum, or private GitHub visibility is not redistribution permission.
- Contract terms, copyright, reverse-engineering exemptions, and code licensing are separate questions. This notebook is not legal clearance.
- Do not claim clean-room development because agents were given different role names. Real clean-room separation needs enforced access and information-flow boundaries.

## Submission and AI assistance

Only humans sign a DCO on their own behalf. The agent must not add a fabricated `Signed-off-by`, imply human review occurred, or submit a contribution without authorization. Follow the destination project's AI-assistance disclosure rules.

Primary guidance:

- [Linux licensing rules](https://docs.kernel.org/process/license-rules.html)
- [Linux coding assistants guidance](https://docs.kernel.org/process/coding-assistants.html)
- [Historical b43 reverse-engineering process](https://bcm-v4.sipsolutions.net/ReverseEngineeringProcess/)
