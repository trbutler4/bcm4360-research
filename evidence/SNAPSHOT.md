# BCM4360 research snapshot

> Historical userspace research at frozen commits. Raw inputs and outputs are intentionally not bundled. Replace absolute path placeholders in recorded commands before use. This document does not imply hardware validation.

Captured beginning 2026-10-02 14:52 UTC. This is a read-only assessment, not a hardware validation. No experimental driver was loaded and the user's NixOS configuration was not changed.

| Repository | Frozen commit | Commit timestamp | Scope |
|---|---|---|---|
| gonsolo/bcm4360-acphy | 1493b8de401ddefef05916ce8b354f6d99d97797 | 2026-10-01T22:09:44+02:00 | Air6,1 b43 prototype and live experiments |
| aleferri/b43-ac-wip | a68a838d8793086ea980b6b71603a6a95623eebd | 2026-10-02T13:12:35+02:00 | Algorithmic b43 AC-PHY, BCMA, core and trace harness |
| aleferri/b43-add-bcm43xx-ac | fee3317cc7936dd2bfdf25e7f7ca6eae3601afb5 | 2026-09-22T14:13:09+02:00 | Redirect to b43-ac-wip |
| massimomazzariol/b43-bcm4360 | d8d8d7751773413beedab4b3105f319651d87ddc | 2026-09-27T15:56:21+02:00 | Board-gated ASUS RT-AC68U passive receiver |
| 0x00000109/OpenBRCM | 06d60d610f4e1cba1f20a188453c8f3ba69357fb | 2026-09-25T02:39:21+02:00 | From-scratch mac80211 BCM4352, isolated DMA/D11 tests |
| kimptoc/bcm4360-re | 7f822c789c7f3fda1aab001f79afb5df81642681 | 2026-05-12T23:09:01+01:00 | Earlier brcmfmac/offload-firmware campaign |
| xZinio/bcm4360 | eb271ace1c609a604202df7e3f8956856514a46f | 2026-09-30T10:28:42+02:00 | Proprietary wl wrapper plus separate open PHY RE work |
| aleferri/b43-tools | 2361e9e8aad9f2912877b82be5cc529b3dd390a1 | 2026-10-02T13:57:23+02:00 | Public D11 instruction interpreter and partial co-simulator, safe local-firmware smoke test |
| torvalds/linux | ce1e0223d8ad4211275c82a17ed6d43ab81e13d9 | 2026-10-01T12:47:16-07:00 | Current mainline support and history, 7.3 development cycle |

The original four discussed repositories were frozen first. OpenBRCM, kimptoc and xZinio were added to avoid missing relevant approaches. GitHub default-branch labels and author README status dates are not used as evidence that all current implementation paths work.

## Additional frozen development branches

- OpenBRCM `m34d3b-band-init-test`: `22e77166f73c39dbf3d827c949403fda26e93bc8`, 2026-09-28. Draft PR #17's body understates the much larger branch contents, including diagnostic source and crash postmortems. Audited separately from default `main`.
- kimptoc `session/agent_c8549f15-1b90-4e62-8756-1d2e77d19740`: `0ba568addc0c2d167938da8d5ddeb7cb9b91ac35`, 2026-06-03, healthy-device MMIO trace ingestion. Audited separately from default `main`.
- gonsolo `wip-5ghz-tx`: `a920890b458d3fc79671b1047c7a687ea2cff777`, 2026-09-27. Historical unmerged work, older than the October 1 default-branch negative 5 GHz results.

## Read-only vendor input

The user's existing Nix source archive, `hybrid-v35_64-nodebug-pcoem-6_30_223_271.tar.gz`, supplied a local `wlc_hybrid.o_shipped` with SHA-256 `352a6e349f74c69b78e76f68c63752c99b8f6b22dc942af531b754211d7f4743`, matching OpenBRCM's pin. Only local research use, no module linking/loading or redistribution. It is kept under `vendor-input/`, outside the user's configuration repository. pyelftools 0.32 was provided in a temporary Nix environment to rerun initially skipped vendor-table tests.

## Evidence levels

- **Reproduced:** safe host-side commands executed in this research workspace, with preserved logs.
- **Code verified:** implementation, tests, patches or current upstream source inspected at the frozen revision.
- **Author hardware evidence:** a maintainer's logs/measurements on their hardware. Not independently reproduced here.
- **Author claim:** narrative without a reproducible public artifact, or incomplete evidence.
- **Inference/recommendation:** assessment of the evidence, not an observed hardware result.

## Workspace

Repositories: `repos/<owner>--<repository>`.
Detailed audits and test logs: `evidence/`.
The Linux source history is available in `/path/to/linux-source`.

Reproduce a baseline identity with:

```sh
git -C repos/gonsolo--bcm4360-acphy rev-parse HEAD
git -C repos/aleferri--b43-ac-wip rev-parse HEAD
git -C repos/0x00000109--OpenBRCM rev-parse HEAD
```

Hardware-derived traces can contain MAC addresses and local network data. The final report must not reproduce those private identifiers.
