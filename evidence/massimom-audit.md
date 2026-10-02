# Audit: `massimomazzariol/b43-bcm4360` at `d8d8d7751773413beedab4b3105f319651d87ddc`

Date: 2026-10-02
Repository URL: https://github.com/massimomazzariol/b43-bcm4360
Pinned commit: https://github.com/massimomazzariol/b43-bcm4360/commit/d8d8d7751773413beedab4b3105f319651d87ddc

## Executive conclusion

This is a narrowly scoped, experimental BCM4360 receive-only bring-up, not a complete BCM4360 driver. The public checkout documents a real hardware result on an ASUS RT-AC68U: the 2.4 GHz BCM4360 path attaches, registers a wiphy, receives real BSS advertisements through b43/mac80211, and supports passive scans. The repository does not contain the two required hardware-data packages, so cloning and building the checkout alone cannot produce a functioning BCM4360 radio. The claimed hardware result depends on locally supplied, unpublished data files and a very specific OpenWrt/backports environment.

No kernel module was built or loaded here, and no hardware was accessed. Only the repository's userspace loader tests and safe syntax/static checks were run.

## What real hardware achieved

The repository claims validation on a physical ASUS RT-AC68U, not emulation. README lines 15-26 state that the tested 2.4 GHz radio comes up under b43, registers with mac80211/cfg80211, and performs passive scans, while TX, association, and 5 GHz remain disabled: [README.md#L15-L26](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L15-L26).

The stated tested identity is BCM4360 D11 core rev 42, AC-PHY rev 1, BCM2069 rev 4, on the ASUS RT-AC68U, using OpenWrt 25.12.5, Linux 6.12.94, backports 6.18.26, and b43 microcode 784.2: [README.md#L41-L50](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L41-L50).

The detailed validation record reports the following claimed result: probe, AC-PHY detection, and BCM2069 detection passed; 14 2.4 GHz channels were exposed, all 14 marked `NO_IR`; zero 5 GHz channels; five of five direct passive scans; five of five helper scans; 50 of 50 BSS/channel matches; zero mismatches; TX packet counters remained 0 to 0; microcode TX counter remained `0x0000`; no stations were associated: [docs/VALIDATION.md#L56-L78](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L56-L78).

The sanitized helper output repeats five successful scans, 10 BSS entries per scan, 50 matches, zero mismatches, and unchanged TX counters: [docs/VALIDATION.md#L94-L110](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L94-L110). The project explicitly says sensitivity and throughput were not characterized: [README.md#L240-L263](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L240-L263).

These are repository-published claims and sanitized records. Raw logs, scan captures, network identities, and the hardware-data payloads are not included: [docs/VALIDATION.md#L10-L11](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L10-L11), [docs/VALIDATION.md#L31-L37](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L31-L37).

## Public-checkout reproducibility

### What is reproducible from the checkout

The documented source build is intended for OpenWrt 25.12.5, target `bcm53xx/generic`, ASUS RT-AC68U, Linux 6.12.94, and mac80211 backports 6.18.26. The patches are not stated to be tested against other OpenWrt releases or mainline: [docs/REPRODUCING.md#L9-L20](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/REPRODUCING.md#L9-L20).

The host data-loader test is reproducible without a kernel tree or hardware data. It extracts the loader source from patch 905, compiles it with a userspace shim and AddressSanitizer/UBSan, then loads synthetic packages: [tests/data-loader/run.sh#L1-L19](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/tests/data-loader/run.sh#L1-L19). The test identity is deliberately synthetic and does not match real hardware: [tests/data-loader/run-tests.py#L3-L9](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/tests/data-loader/run-tests.py#L3-L9).

### What is not reproducible from the checkout alone

The chip/radio and board packages are absent and the repository says it provides no generator for them: [docs/HARDWARE-DATA.md#L1-L13](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/HARDWARE-DATA.md#L1-L13). The required paths are:

```text
/lib/firmware/b43/bcm4360-ac1-2069r4.bin
/lib/firmware/b43/bcm4360-board-asus-rt-ac68u.bin
```

See [docs/HARDWARE-DATA.md#L15-L24](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/HARDWARE-DATA.md#L15-L24) and [README.md#L358-L384](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L358-L384).

Therefore:

* source patch application and host loader tests are publicly reproducible;
* a complete fresh OpenWrt image build was not performed even in the project's own validation, which says its compile check used an already configured OpenWrt build environment: [docs/VALIDATION.md#L13-L29](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L13-L29);
* hardware functional validation is not independently reproducible from the public checkout unless the exact external data packages are obtained by other means.

## Safety and bounds gates

The loader has meaningful defensive checks before device programming. The parser rejects files shorter than 32 bytes or larger than 1 MiB, checks magic, ABI, kind, total length, and CRC, validates identity, limits sections to 1..32, checks the table fits, rejects nonzero reserved bytes and unsupported flags, accepts only 8/16/32-bit elements, checks nonzero counts, 4-byte alignment, payload bounds, mandatory unknown sections, duplicate IDs, and overlapping payloads: [905 patch#L165-L247](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L165-L247).

Section-specific checks include RF-sequencer record limits and overruns, exact channel row counts and channel numbering 1..14, exact phase/Farrow/gain shapes, board FEM core count, and eLNA/T/R loss ranges: [905 patch#L276-L391](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L276-L391), [905 patch#L394-L431](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L394-L431).

The loader requests and validates both packages before success, with no partial/default/zero-filled fallback. The documented intent is to reject before PMU, PHY, or radio access: [905 patch#L434-L470](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L434-L470), [docs/HARDWARE-DATA.md#L26-L37](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/HARDWARE-DATA.md#L26-L37).

There is also an unrelated but important safety backport for a firmware-controlled key index. Instead of merely warning, invalid indexes are now dropped before indexing `dev->key[]`: [820 patch#L1-L29](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/820-b43-enforce-bounds-check-on-firmware-key-index.patch#L1-L29).

Receive-only gating is explicit: only the RX DMA ring is set up, channels are `NO_IR`, station/monitor receive modes are constrained, and frames handed to `op_tx` are dropped: [904 patch#L1-L15](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/904-b43-bcm4360-receive-only-device.patch#L1-L15). The validation document also states that no TX DMA ring is created and active scanning is disabled: [docs/VALIDATION.md#L114-L126](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L114-L126).

### Obvious parser correctness gaps

I did not find an obvious exploitable arithmetic bounds gap in the inspected parser. The multiplication is widened to `u64`, and payload bounds and overlap checks are performed before pointers are retained. The tests exercise the main malformed-package cases.

There are still limitations worth recording:

1. The parser validates generic section metadata, but semantic validation is intentionally narrow and tied to the known section IDs and expected shapes. It does not validate the electrical or RF correctness of the values beyond the explicit range checks. A syntactically valid package can therefore still contain physically wrong tables.
2. The host tests use synthetic data and a synthetic identity, so they verify parser behavior and round-trip conversion, not the correctness of the unpublished real data or hardware behavior.
3. The `b43_bdata_known()` check treats the contiguous chip ID range `0x0101` through `0x0107` as known. Current IDs occupy that range, so this is not a present bug, but it is a maintenance hazard if an ID is added without corresponding build-time handling.
4. The loader's global cache permits one board package per module lifetime and returns `-EBUSY` for a different board profile: [905 patch#L473-L526](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L473-L526). This is a deliberate single-system constraint, not a parser memory-safety defect.

## Chip versus board differentiation

The split is technically clear and enforced. The chip/radio package contains BCM4360/AC-PHY/BCM2069 tables, channel rows, Farrow data, phase tracking, RX gain tables, and optional RX EVM. The board package contains FEM control data and board-dependent RX gain values: [docs/HARDWARE-DATA.md#L78-L99](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/HARDWARE-DATA.md#L78-L99).

The board profile is not selected from chip ID alone. It checks machine compatible, chip ID, SPROM device ID/radio slot, NVRAM values, PHY revision, radio version/revision, board flags, and Bluetooth coexistence state. Only one profile exists, for the ASUS RT-AC68U 2.4 GHz radio: [904 patch#L48-L95](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/904-b43-bcm4360-receive-only-device.patch#L48-L95), [904 patch#L132-L213](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/904-b43-bcm4360-receive-only-device.patch#L132-L213).

The chip package requires the chip/radio identity, while the board package additionally requires the exact `rt-ac68u` tag. The parser initializes the expected chip-package tag as all zero and compares the board tag against the selected profile: [905 patch#L186-L197](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/905-b43-bcm4360-hardware-data-loader.patch#L186-L197).

The second BCM4360 in the RT-AC68U, corresponding to the 5 GHz radio, is intentionally rejected. This is a board/radio-profile gate, not evidence that all BCM4360 devices are supported: [README.md#L178-L206](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L178-L206).

## Relationship to earlier Alessio Ferri work

The README acknowledges Alessio Ferri's `b43-ac-wip` as a technical reference and explicitly says no code from it is included: [README.md#L267-L286](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L267-L286). The cited project is https://github.com/AlessioFerri/b43-ac-wip. The licensing document characterizes that project as GPL-3.0 prior work used only as a technical reference and says no code was included: [docs/LICENSING.md#L97-L105](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/LICENSING.md#L97-L105).

The repository's own patch provenance instead identifies Linux b43/OpenWrt as the inherited bases, with original additions attributed to Massimo Mazzariol and retained upstream notices for modified b43 files: [docs/LICENSING.md#L25-L62](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/LICENSING.md#L25-L62).

## License and provenance

The repository default is GPL-2.0-only for files without their own SPDX tag. Patched b43 files retain their original GPL-2.0-only or GPL-2.0-or-later terms, and tools/tests are GPL-2.0-only: [docs/LICENSING.md#L1-L21](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/LICENSING.md#L1-L21). Patch 820 identifies itself as a backport of upstream Linux commit `1f4f78bf8549e6ac4f04fba4176854f3a6e0c332`: [820 patch#L1-L17](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/patches/mac80211/brcm/820-b43-enforce-bounds-check-on-firmware-key-index.patch#L1-L17).

No hardware data or b43 microcode is included. The microcode is expected from OpenWrt's b43 firmware packaging: [docs/LICENSING.md#L97-L105](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/LICENSING.md#L97-L105).

The router product photograph is a cropped Wikimedia Commons derivative, credited to Kenming Wang and retained under CC BY-SA 2.0, not relicensed under GPL: [docs/images/README.md#L27-L43](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/images/README.md#L27-L43).

## Radio limitations

* **2.4 GHz:** receive-only operation on channels 1 through 14, passive scanning and monitor reception. All exposed channels are `NO_IR`.
* **5 GHz:** no channels are exposed; the second BCM4360 is rejected with error `-95`.
* **TX:** disabled by design. No TX DMA ring is created, frames handed to TX are dropped, and the published validation counters stayed at zero.
* **Association/connectivity:** disabled and not demonstrated. The test interface remained unassociated, with zero associated stations.
* **Scanning:** passive scanning only. Active scanning is disabled.
* **Channel width:** 40 MHz and 80 MHz are not supported.
* **Other hardware:** other BCM4360 boards, BCM4352 and other AC-PHY chips, and other BCM2069 revisions are explicitly unsupported.

Primary evidence: [README.md#L240-L259](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/README.md#L240-L259), [docs/VALIDATION.md#L114-L126](https://github.com/massimomazzariol/b43-bcm4360/blob/d8d8d7751773413beedab4b3105f319651d87ddc/docs/VALIDATION.md#L114-L126).

## Tests run during this audit

Working tree was clean before and after testing. No repository files were edited, no user configuration was touched, and no kernel module or hardware operation was attempted.

1. `tests/data-loader/run.sh`
   * Result: exit code 0.
   * Exact result: `31/31 passed`.
   * All listed round-trip and rejection cases passed, including missing packages, CRC/length errors, ABI/kind/identity errors, truncation, alignment and bounds failures, overlap and duplicate sections, reserved bytes, mandatory/optional unknown sections, missing/malformed sections, channel ordering, RF-sequencer errors, RX EVM shape, FEM core count, and eLNA range.
2. `sh -n tests/data-loader/run.sh tools/apply-to-openwrt.sh tools/passive-scan-check.sh`
   * Result: exit code 0, no output.
3. `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile tests/data-loader/bdata_write.py tests/data-loader/new-files-from-patch.py tests/data-loader/run-tests.py`
   * Result: exit code 0, no output.
4. `git diff --check`
   * Result: exit code 0, no output.
5. `git status --short`
   * Result: empty output after tests.

These tests validate the userspace extraction/parser harness only. They do not validate kernel integration, the absent real data, RF correctness, association, TX, or 5 GHz operation.
