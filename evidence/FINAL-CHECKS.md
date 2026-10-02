# Final research integrity checks

Checked 2026-10-02 at approximately 15:37 UTC. Research began at 14:52 UTC.

- Final synthesis: `REPORT.md`, 615 lines, 8,765 words, 69,767 bytes at this check.
- `python3 -B evidence/check_report.py`: PASS.
- All 56 Markdown reference definitions resolve and are used.
- All 45 linked pinned GitHub source objects exist in the inspected repositories. Cited line anchors are within their files.
- All 19 local report links resolve.
- No draft placeholders, em dashes, hardware MAC addresses or detected private network addresses in the synthesis.
- `/path/to/nixos-config`: `git status --porcelain` returned no output.
- No experimental kernel module was built/loaded, no PCI/MMIO/radio access occurred, and no Air/network configuration was changed.

These are document/input-integrity checks, not proof of physical driver functionality or legal clearance. Host execution, synthetic falsification witnesses, vendor-object comparisons and other people's hardware reports are separately labeled in the report.

Independent review led to stronger pre-RF DMA/IRQ containment gates, explicit reboot-only retention semantics after device loss, narrower OpenBRCM milestone claims, per-file licensing qualifications, and revised contribution priorities. The public D11 interpreter was subsequently pinned and exercised against already-local, correctly encoded firmware, closing the earlier dependency-inspection gap without claiming full reset/packet/RF execution.

The workspace contains proprietary firmware/object inputs, derived bytes and raw hardware traces. Do not publish the entire directory as a freely licensed bundle. The synthesis itself avoids reproducing those bytes and private network/device identifiers.
