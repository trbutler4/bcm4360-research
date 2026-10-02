# Research roadmap

## 0. Repository and access foundation

Preserve the 2 October survey with frozen source pins, make the evidence boundaries explicit, and establish Ethernet SSH. The initial repository contains no driver loader, register-dump script, or deployed laptop change.

## 1. First bounded host-only contribution

Candidate: the empty-input `IDENTICAL` success observed in aleferri's initialization-equivalence tooling at `a68a838d8793086ea980b6b71603a6a95623eebd`.

### Acceptance

- Refresh upstream and determine whether the finding is still present.
- Verify file-level licensing and the intended comparator/gate contract.
- Add a reproduced failing synthetic witness to the correct boundary.
- A meaningful nonempty equal state remains successful.
- A real mismatch fails.
- Missing or empty initialization evidence cannot imply a successful initialization run.
- Both-empty and one-sided-empty cases are explicitly tested.
- The destination project's real host-test interface and regression tests are exercised, with observed results recorded.
- Prepare a small reviewable patch without vendor data or an agent-generated DCO.

A generic mapping comparator can correctly regard two empty mappings as equal. Fix the authoritative gate rather than imposing an unrelated semantic rule everywhere. If upstream already fixed this finding, select another reproduced narrow defect instead.

## 2. Improve the evidence pipeline

Prioritize selector preservation, correct A/B overlay ownership, widths derived from explicit bus metadata, unknown-window accounting, and coverage that fails closed. Do not call partial comparisons raw or comprehensive without specifying exclusions and tolerance.

Then test the actual revision-11 SPROM extractor rather than only a duplicate harness copy. Nonzero RX-IQ coefficient arithmetic is a separate bounded numerical project, not an established fix for the Air's managed-TX initialization failures.

## 3. Read-only laptop baseline

Once reachable, record safely obtained board/chip identity, kernel, active driver, recovery generation, and Ethernet routing. Check what works with the vendor driver without performing intrusive register probes.

## 4. Reviewed hardware questions

Choose a single experiment justified by the baseline and host tests. Obtain initial test-scope approval and follow the safety policy. Start with board-specific provisioning and conservative observation, then passive RX or managed legacy operation only when justified by the selected implementation.

Measure actual reception, association, authenticated traffic, throughput, and repeated lifecycle behavior separately. No model score or register readback substitutes for these outcomes.

## 5. Collaboration and upstreaming

Contribute narrow, properly licensed changes to existing projects. Five GHz, HT/VHT, calibration completeness, regulatory behavior, failure containment, and upstream readiness remain distinct milestones. Do not advertise a dependable open driver until the real acceptance paths support that claim.
