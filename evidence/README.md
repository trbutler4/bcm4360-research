# Evidence index

These Markdown documents preserve the completed 2 October 2026 survey and its exact source pins. They are historical assessments, not current status guarantees or new hardware tests.

- [Frozen manifest and evidence levels](SNAPSHOT.md)
- [Gonsolo](gonsolo-audit.md)
- [Aleferri](aleferri-audit.md)
- [Separate public D11 interpreter](d11-interpreter-audit.md)
- [Massimomazzariol's receive-only effort](massimom-audit.md)
- [OpenBRCM main](openbrcm-main-audit.md)
- [OpenBRCM newer development branch](openbrcm-branch-audit.md)
- [XZinio](xzinio-audit.md)
- [Kimptoc, including the June branch](kimptoc-audit.md)
- [Independent synthesis challenge](synthesis-challenge.md)
- [Independent architecture and safety review](report-review-openbrcm.md)
- [Original report validation summary](FINAL-CHECKS.md)

Some documents retain an initial limitation followed by an explicit superseding addendum. Read the complete audit, not just its opening status. The validation summary describes checks on the original research workspace, not checks that the curated Git repository contains all of those artifacts.

## Omitted local artifacts

Raw logs, test exports, helper probes, vendor objects, derived firmware, build products, captures, and upstream clones remain outside this repository. In particular, the report's references to these logs are documentary references, not included downloads:

- `xzinio-oracle-iq.log`
- `xzinio-host-numeric.log`
- `xzinio-all.log`
- `openbrcm-real-firmware-probe.log`

Recorded commands use `/path/to/research-workspace`, `/path/to/linux-source`, and `/path/to/nixos-config` in place of original workstation paths. Substitute an appropriate local environment and review the referenced script before attempting any reproduction. The historical workspace and its helper files are not reconstructed automatically by these notes.

The source object SHA-256 and public source links can identify inputs without granting permission to redistribute them. Any future evidence release must review licensing and sanitize machine, account, and network identifiers first.
