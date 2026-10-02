# Evidence audit: xZinio/bcm4360

Audit date: 2026-10-02. Pinned tree: `eb271ace1c609a604202df7e3f8956856514a46f` (HEAD verified locally). Working tree was clean before and after host checks. No modules loaded, PCI/MMIO accessed, network settings modified, commits made, vendor downloads performed, or child agents created. Output and the isolated numeric probe are outside the repository.

## Executive conclusion

**This is substantial open AC-PHY research and implementation, not an available open replacement driver.** The top-level README accurately describes the shipped hybrid module, but its categorical claim that no open implementation exists, and the pessimistic OPEN-DRIVER-NOTES, do not describe the newer `open/` subtree. That subtree contains genuine register-access, radio, PMU, attach, initialization, channel, gain/desense, TX-power and calibration code. It is useful as an independently structured, specification-oriented reference and an executable vendor-object comparison framework.

**The September 30 claim of all 21 scenarios matching was independently reproduced in this audit's follow-up: 21 passed, 0 failed, 0 skipped.** Initial attempts were blocked by missing dependencies, then a temporary Nix shell and the coordinator-supplied object with the exact expected SHA256 resolved them. Strict Zig compilation and three harness/toolchain selftests passed. Most importantly, source inspection finds a stronger limitation than the status document acknowledges: **RX IQ coefficient arithmetic for every nonzero measurement is explicitly unimplemented**. Safe standalone native and vendor-oracle numeric probes confirmed large discrepancies for nonzero measured powers despite the complete modeled scenario suite passing. Therefore “whole AC-PHY reimplemented” and “calibration complete” are not justified as general functional claims, even though the reported traces genuinely match for the supplied scenarios.

There is also a concrete firmware-packaging mismatch: the open PHY requests `rx_farrow_tbl` and `tx_farrow_dac1_tbl`, while `fwcut.py`'s extraction selection does not include those names. The emulator provides any named object symbol directly, which hides this deployment boundary.

## 1. Which project is being audited?

All xZinio links below are immutable links to the audited tree. Source line numbers are from `nl -ba` at that pin.

* [README.md L1-L22](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/README.md#L1-L22): DKMS packaging of Broadcom hybrid `wl`, PCI `14e4:43a0`, MacBook Air 2013-2017. Claims kernel 7.2 testing on MacBookAir7,2, revision 03, Apple subsystem `106b:0117`. Its real connection, throughput and suspend results belong to the **hybrid driver**, not the open PHY.
* [Makefile L1-L31](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/Makefile#L1-L31): module objects are Linux glue under `src/`; link flags include `lib/wlc_hybrid.o_shipped`. No `open/` file is a module build input.
* [open/README.md L1-L15, L28-L49](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/README.md#L1-L49): describes specification-based code, emulator A/B comparison, and explicitly says “hardware layer under construction, not a driver” and nothing is built into `bcm4360.ko` yet.
* [OPEN-DRIVER-NOTES.md L3-L46, L61-L75](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/OPEN-DRIVER-NOTES.md#L3-L75): says replacement is not realistic, radio implementation does not exist, and no path exists to a working in-repository-only driver. Read this as older framing of the hybrid product, not a reliable inventory of current research. Its firmware and license concerns remain relevant, but blanket dismissal is contradicted by the source now present.

Local history provides the dating distinction: `0d8535c` at 2026-09-30 10:28:33 +0200 is titled “AC-PHY calibrations complete: all 21 A/B scenarios match the object”; the audited merge follows at 10:28:42. `docs/re/05-status.md` still labels itself state of September 28 despite including calibration completion and stale next steps. Treat dates and narrative summaries cautiously.

## 2. Functionality actually present and major missing core

[Status L26-L44](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L26-L44) maps the implementations and gives the following reported results. The actual follow-up run reproduced every scenario with zero differences, but found a stale aggregate radio count: all nine current radio scenarios total 7,220 accesses, not 5,727. See section 7a for the exact observed rows.

| Area | Actual implementation | Reported comparison |
|---|---|---|
| PHY/radio/table/shared-memory access | `open/hw/access.c` | 422 accesses |
| 2069 radio power, RCAL/RCCAL, tuning, VCO/AFE | `open/phy/radio2069.c` | 9 scenarios, 5,727 accesses |
| PMU/clocks | `open/chip/pmu.c` | 6 scenarios, 2,838 accesses |
| Attach/state/SROM-derived variables | `open/phy/phy_attach.c` | 206 accesses and 1,260 values |
| Initialization | `open/phy/phy_init.c` | 47,078 accesses |
| Channel switching | `open/phy/phy_chanspec.c` | 26,593 accesses, nine channels |
| Front end/filters/RX gain, desense, TX power | `phy_rxgain.c`, `phy_desense.c`, `phy_txpower.c` | Included in init/channel scenarios |
| Calibration/scheduler/tone/temperature | `open/phy/phy_cal.c` | 141,130 accesses |

These are real implementations, not merely Markdown or renamed Broadcom glue. Eleven C translation units and seven headers exist in `open/`. `phy_cal.c` is 2,000 lines; attach is 1,800, RX gain 1,511, desense 1,476. Line count is not correctness evidence, but the source contains substantive state machines, loops and arithmetic. The formerly stubbed front-end/TX-power groups are no longer excluded: [phy_scenarios.py L522-L606](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L522-L606) has `STUBBED_AREAS = []`, and calibration explicitly uses `without=[]`. [phy_todo.c L1-L36](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_todo.c#L1-L36) now contains comments, not empty implementation bodies. Old “stubbed” docstrings and file comments alone are not evidence the active exclusion remains.

However the Linux platform backend is absent: [hw.h L3-L9 and L140-L142](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/include/bcm4360/hw.h#L140-L142) explicitly emits `#error` without `BCM4360_EMU`. Missing deliverables include backplane/PCIe integration, actual SROM/OTP acquisition and board-variable provisioning, MAC firmware/init/buffer bring-up implementation, DMA/FIFOs/interrupts, packet/status formats, aggregation and hardware key handling, mac80211 glue and lifecycle/concurrency/power-management integration. The status proposes bcma + mac80211 or adding the PHY to b43, but says the suitability of b43 MAC core rev 42 has not been checked: [status L178-L194](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L178-L194).

Reimplementing the vendor's full 802.11 station stack is not planned, appropriately: management/scanning/WPA/rate-control should come from mac80211 ([status L100-L104](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L100-L104)). That architectural economy does not make the outstanding hardware datapath small.

## 3. What the oracle and “100% matching” mean

This is **userspace emulated execution of a vendor relocatable object**, not loading the proprietary module or touching the real adapter. [emu.py L4-L23, L65-L88](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/emu.py#L4-L88) loads the object into Unicorn x86-64, provides Python imports and maps an emulated address space. [03-tools L32-L59](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/03-tools.md#L32-L59) explains Python OS and chip models. Safe host execution still involves trusting Python/emulator inputs and dependencies, but no card or elevated privileges are intrinsically required.

The comparison is meaningful but carefully bounded:

1. [ab.py L4-L20 and L143-L168](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/ab.py#L143-L168) compares **logical** operations `(op, space, address, size, value)`, including delays. It drops indirect PHY/radio/shared-memory address/data mechanics and selected table-carrier register operations. “Access-for-access” is not literal equality of every bus transaction.
2. [phy_scenarios.py L377-L449](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L377-L449) calls the open PHY in order, retaining its own software state, but restores **vendor reference hardware-model state before each stage**. This is stronger than testing each function from arbitrary defaults, weaker than an uninterrupted open-only hardware session with all prior effects carried forward.
3. MAC/chip/timer/OTP services are recorded and their results/output buffers replayed to open code instead of executing an independent layer ([phy_scenarios.py L29-L60](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L29-L60), [ab.py L489-L520](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/ab.py#L489-L520)). Logical service arguments and placement can be compared, but successful service behavior is supplied by the oracle. Replay searches by service name; the trace comparison supplies additional ordering/argument checks.
4. Only selected top-level APIs are scored in each scenario. Init/channel/calibration use explicit API lists. Other available APIs may run to maintain state without contributing a scored comparison. Calibration specifically scores temperature sense and `phy_cals`, not an exhaustive scheduler/state matrix.
5. [PHY_MODELS and channels L112-L118](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L112-L118): two model combinations (PHY1/radio4 and PHY0/radio3), nine channel selections covering 2.4/5 GHz and 20/40/80 MHz. Attach-state also varies synthetic variables. Calibration is directly triggered single-shot phase 0 after up ([L232-L305](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L232-L305)), not real association. Its reported four stages are temperature + calibration on the two models, not 21 distinct calibration tests.
6. [03-tools L103-L130](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/03-tools.md#L103-L130): readback is previous writes or zero; no RF signal simulation; status loops can time out; `radio_done` returns fixed completion/results; broadcast-core write aliasing is not modeled as real hardware might perform it. Restricted regulatory channels are reached by direct PHY calls, not demonstrated as legal usable channels.

The 21 entries are 1 access + 9 radio + 6 PMU + 5 PHY (`attach`, `init`, `chanspec`, `cal`, `attach-state`), verified statically from decorators in `scenarios.py` and `phy_scenarios.py`. No percentage can be extrapolated from these to total PHY code coverage, radio quality, association reliability or usable packet traffic. Matching both implementations against the same simplified model may reproduce the same wrong assumptions.

## 4. Calibration: real algorithms, explicit incomplete measured-data path

### Genuine useful content

[phy_cal.c L458-L520](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_cal.c#L458-L520) implements an 18-iteration fixed-point CORDIC with angle reduction and a mathematically derived arctangent table. The comments and [questions/phy-cal L86-L101](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/questions/phy-cal.md#L86-L101) explain the independently derived table, I=sine/Q=cosine convention, scaling and interleaved gain/LOFT writes. The audit numeric probe produced near-ideal quadrature outputs. Tone generation, sample playing, TX IQ/LO command/coefficients orchestration, save/override/restore, RX gain search, IQ accumulators and temperature sensing have actual procedural implementations. [phy_cal.c L1450-L1558](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_cal.c#L1450-L1558) contains an adaptive power-based gain-search loop. These should not be dismissed because the oracle is proprietary or because RF measurements are synthetic.

### Critical source-level contradiction

[phy_cal.c L1233-L1250](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_cal.c#L1233-L1250) says explicitly:

> non-zero measurements do not occur in the model; left unimplemented

`phy_calc_iqcc()` returns `{angle=0, gainratio=0x400, sinterm=0}` for **both zero and all nonzero inputs**. This is not merely a complete coefficient algorithm that needs real-card validation. It is an absent measured-data arithmetic implementation. It contradicts the impression in [status L66-L79](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L66-L79) that coefficients are computed generally from measured powers, and the “whole calibration path ... complete” statement in [questions L15-L23](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/questions/phy-cal.md#L15-L23).

Additional scope restrictions: [phy_cal.c L1561-L1659](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_cal.c#L1561-L1659) averages angles/gain ratios while discarding `amp`, hardcodes two tones at +/-1000, and computes a second image estimate whose converted result is discarded. Broader regression/tone/image behavior is therefore not established. [L1202-L1213](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_cal.c#L1202-L1213) labels 5 GHz loopback unverified. Questions L159-L200 acknowledge unobserved 5 GHz gain tables and a discarded 48-bit default gain word. Scheduler phase-by-phase execution, scan/roam cache variants, channel/bandwidth calibration matrix, signal saturation and signed arithmetic corner cases need distinct tests.

The temperature scenario was changed to call with MAC already suspended because service replay does not apply real MAC register effects ([questions L25-L45](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/questions/phy-cal.md#L25-L45)). That is a documented harness-boundary workaround, not proof the missing MAC effects work independently.

## 5. MacBookAir7,2 applicability

The hybrid module has repository-reported live tests on exactly MacBookAir7,2 / `14e4:43a0` / `106b:0117`. The open specification is aimed at that Apple board and two chains ([acphy-cal-rx L3-L9](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/spec/acphy-cal-rx.md#L3-L9)). This is stronger target intent than a generic chip label.

But [status L127-L143](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L127-L143) explicitly identifies chip revision/package, crystal selection, PMU capabilities, PHY/radio revision and calibration results as assumptions, and SROM as synthetic. PCI revision 03 does not independently establish every internal revision. Actual FEM, boardflags, gains, PA parameters, oscillator and chain configuration must come from the target board. “Nothing tried on a real card” in status L16 means the open research/model, not the whole repository's hybrid product. Open code is not installation-ready on the target.

The target peek and capture scripts are explicitly untested and hardware-interacting; capture unloads/reloads the driver and disrupts networking ([status L155-L165](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L155-L165)). Neither was executed here.

## 6. License, clean-room evidence and extracted-table provenance

All inspected open C/header first lines use `SPDX-License-Identifier: ISC` (11 C, 7 headers). [LICENSE L3-L30](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/LICENSE#L3-L30) asserts ISC for repository content, describes Broadcom glue provenance, and explicitly excludes the proprietary object. SPDX is author-provided licensing metadata, not independent proof that every implementation/table is free of third-party rights.

[implementing.md L8-L22](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/implementing.md#L8-L22) instructs implementers to use specs/open code/comparison results, forbids object/disassembly/decompilation and extraction tools. [04-method L39-L61](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/04-method.md#L39-L61) says AI analyst/implementer instances were separated by instructions, not technical enforcement; coordinator had decompiler exposure and contributed the platform header. This is a disclosed process, not externally audited clean-room certification. [status L81-L95](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/05-status.md#L81-L95) acknowledges direct vendor execution trace observation by the RX calibration implementer beyond the intended analyst/spec split. Do not conflate register-behavior observation with copying code, but do not repeat “from specifications and nothing else” without this qualification.

[04-method L75-L114](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/04-method.md#L75-L114) discusses contractual reverse-engineering restrictions and EU interoperability exceptions. This report does not adjudicate applicability or provide legal clearance. The broad pessimistic legal sentence in OPEN-DRIVER-NOTES is not the project's only legal analysis.

Bulk radio/PHY tables and MAC microcode are **not recreated under ISC**. [hw.h L123-L131](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/include/bcm4360/hw.h#L123-L131) describes vendor data supplied by the platform. [fwcut.py L4-L17 and L85-L113](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/fwcut.py#L85-L113) extracts named symbols, identifies source version/core revision and writes per-output SHA256, section, offset and size to a manifest; it explicitly says extracted files are Broadcom's and must not be redistributed. `.gitignore` excludes `lib/` and `re-out/`.

**Packaging gap:** `fw_env` returns the address of any matching vendor symbol directly ([phy_scenarios.py L326-L335](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/phy_scenarios.py#L326-L335)). The deployed extraction whitelist accepts microcode/initvals and prefixes `acphy_`, `acphytbl_`, `chan_tuning_2069`, `prefregs_2069`, `ovr_regs_2069`, but not the Farrow names requested at [phy_rxgain.c L1155-L1179](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/open/phy/phy_rxgain.c#L1155-L1179). Thus even a supplied fwcut bundle would not automatically replicate the emulator's data service. This is statically established selection mismatch; no blob-dependent extraction was performed. A complete symbol dependency inventory and manifest/loader integration test are needed. The manifest also hashes outputs, not the complete input object, and no Linux firmware loader exists yet.

## 7. Reproducibility and actual safe command results

**Chronology note:** this section preserves the initial dependency-blocked checks. Section 7a below records the successful follow-up and supersedes availability/blocker statements for the final audit outcome.

Pinned source is reproducible to inspect, but full A/B claims need extra licensed inputs and tooling. [scripts/fetch-blob.sh L14-L37](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/scripts/fetch-blob.sh#L14-L37) pins release `hybrid-v35_64-nodebug-pcoem-6_30_223_271.tar.gz` with SHA256 `5f79774d5beec8f7636b59c0fb07a03108eef1e3fd3245638b20858c714144be` and BLAKE2b verification. It accepts a local tarball, extracts object/license and installs them under `lib/`. This is good provenance control but neither object nor tarball was present/fetched here. The canonical tools need Python `unicorn`, `capstone`, `pyelftools`; Zig builds freestanding x86-64 with GNU11 and `BCM4360_EMU` ([03-tools L3-L6](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/03-tools.md#L3-L6), [ab.py L45-L107](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/ab.py#L45-L107)). Tool versions are not locked by these instructions. Ghidra is needed for decompilation, not ordinary A/B replay.

Commands ran from the checkout:

```sh
git rev-parse HEAD
git status --short
python3 -B tools/re/ab.py list
python3 -B tools/re/ab.py all
python3 -B tools/re/selftest.py
python3 -B tools/re/mmiotrace.py selftest
```

HEAD matched the requested pin. Both status checks had no output. All four Python entry points exited 1 at import with `ModuleNotFoundError: No module named 'unicorn'`. `command -v zig` found no executable. `lib/` and `re-out/` were absent in the checkout inventory. No A/B test reached vendor execution. The test command does **not** report 21 failures or successes, just an environment block. Dependencies were not installed and the blob was not fetched. After the audit tests and initial report were written, the coordinator disclosed an already extracted read-only object and license in `/path/to/research-workspace/vendor-input/lib`. This changes the availability of a potential external oracle, not the observed failed runs or the absence of the object in this checkout. No oracle comparison was rerun with that input, and matching it to the pinned archive checksum has not been established by this audit. A Python environment with only pyelftools, as mentioned by the coordinator, still would not satisfy Unicorn/Capstone or Zig requirements.

Safe host compilation/syntax checks after inspection:

```sh
for f in open/hw/*.c open/chip/*.c open/phy/*.c; do
  cc -std=gnu11 -ffreestanding -fno-strict-aliasing -Wall -Wextra \
    -Wno-unused-parameter -Werror=implicit-function-declaration \
    -DBCM4360_EMU=1 -Iopen/include -fsyntax-only "$f"
done
python3 -B -c 'import ast,pathlib; fs=list(pathlib.Path("tools/re").glob("*.py")); [ast.parse(f.read_text(),filename=str(f)) for f in fs]; print("AST parsed",len(fs),"Python files")'
```

Results: all 11 C units returned 0, no diagnostics. All 21 top-level Python files parsed successfully. Compiler: GCC 15.3.0. These are syntax checks, **not** a Zig build, link check, kernel build or semantic verification.

An isolated probe at `evidence/xzinio-host-numeric.c` includes the actual pinned `phy_cal.c`, calls only pure static numeric functions, and uses linker section garbage collection to discard unused hardware functions. It contains no vendor code/data and performs no I/O except printing:

```sh
cc -std=gnu11 -O1 -DBCM4360_EMU=1 -Iopen/include \
  -ffunction-sections -fdata-sections \
  /path/to/research-workspace/evidence/xzinio-host-numeric.c \
  -Wl,--gc-sections \
  -o /path/to/research-workspace/evidence/xzinio-host-numeric
/path/to/research-workspace/evidence/xzinio-host-numeric
```

Successful output:

```text
iqcc {0,0,0} -> {0,1024,0}
iqcc {100,1000,2000} -> {0,1024,0}
iqcc {-100,2000,1000} -> {0,1024,0}
cordic(0) = {3,65536}
cordic(90deg) = {65536,3}
```

An initial compile without `-std=gnu11` failed because GCC's default C23 conflicts with this tree's `typedef _Bool bool`; explicitly using the documented GNU11 dialect fixed it. This was a test invocation issue, not a supported-build failure. The probe is synthetic targeted validation, not a physical IQ-quality test or exhaustive numerical proof.

For an authorized future host reproduction, provision a licensed, checksum-verified object and isolated dependencies, then use `ab.py build`, `ab.py selftest`, `selftest.py`, `mmiotrace.py selftest`, `ab.py list`, `ab.py all`. The tool's `all` path uses a non-strict build that can omit failed units ([ab.py L625-L665](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/ab.py#L625-L665)), so retain a separate strict build result and diagnostics. No automatic download or hardware capture is necessary for pure model tests. Physical acceptance remains a separate, explicitly authorized workflow.

## 7a. Successful follow-up: actual 21-scenario reproduction

At the coordinator's request, the initial environment blocker was resolved without persistent user/system installation or configuration edits. An ignored `lib/wlc_hybrid.o_shipped` symlink was created in the research clone pointing to the existing read-only input. The clone's tracked files remain unchanged (`git status --short` empty). Tests generated ignored `re-out/open/` objects. The input SHA256 is `352a6e349f74c69b78e76f68c63752c99b8f6b22dc942af531b754211d7f4743`, exactly matching [selftest.py L18 and L84-L87](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/tools/re/selftest.py#L18-L87). This validates the object against the repository's explicit expected digest, independently of the fetch script's archive digest.

Temporary environment command:

```sh
nix shell --impure --expr 'let flake = builtins.getFlake "/path/to/nixos-config"; pkgs = import flake.inputs.nixpkgs { system = "x86_64-linux"; }; in [ pkgs.zig (pkgs.python3.withPackages (ps: [ ps.pyelftools ps.unicorn ps.capstone ])) ]' \
  --command sh /path/to/research-workspace/evidence/xzinio-run-tests.sh
```

The external runner performs `ab.py build`, `ab.py list`, `selftest.py`, `ab.py selftest`, `mmiotrace.py selftest`, then `ab.py all`, saving each command's complete stdout/stderr separately with exact exit codes. Environment: Python 3.14.7, pyelftools 0.32, Unicorn 2.1.4, Capstone Python-reported 5.0.7 (Nix package derivation label 5.0.9), Zig 0.16.0. Nix downloaded cache packages and built a temporary Python environment, without changing user configuration. Total suite runner wall time approximately 158.5 seconds.

| Command | Actual outcome | Saved log in evidence/ |
|---|---|---|
| `python3 -u tools/re/ab.py build` | Exit 0, all 11 objects compiled, no diagnostics | `xzinio-build.log` |
| `python3 -u tools/re/ab.py list` | Exit 0, 21 scenario entries | `xzinio-list.log` |
| `python3 -u tools/re/selftest.py` | Exit 0, 18 checks, 0 failed | `xzinio-selftest.log` |
| `python3 -u tools/re/ab.py selftest` | Exit 0, `selftest ok` | `xzinio-ab-selftest.log` |
| `python3 -u tools/re/mmiotrace.py selftest` | Exit 0, 28,456 accesses recorded/replayed, 55,804/55,804 trace records identical | `xzinio-mmiotrace-selftest.log` |
| `python3 -u tools/re/ab.py all` | Exit 0, **21 passed, 0 failed, 0 skipped** | `xzinio-all.log` |

Exact observed scenario rows (object/open counts equal in each row, differences zero):

| Scenario | Stages | Object count | Open count | Differences |
|---|---:|---:|---:|---:|
| access | 1 | 422 | 422 | 0 |
| radio-pwron | 3 | 271 | 271 | 0 |
| radio-off | 9 | 108 | 108 | 0 |
| radio-rcal | 3 | 303 | 303 | 0 |
| radio-rccal | 3 | 857 | 857 | 0 |
| radio-tune | 24 | 1821 | 1821 | 0 |
| radio-vcocal-wait | 24 | 1632 | 1632 | 0 |
| radio-afecal | 18 | 1560 | 1560 | 0 |
| radio-band | 5 | 20 | 20 | 0 |
| radio-tssi | 18 | 648 | 648 | 0 |
| pmu-indirect | 19 | 99 | 99 | 0 |
| pmu-init | 4 | 8 | 8 | 0 |
| pmu-pll-init | 16 | 76 | 76 | 0 |
| pmu-res-init | 4 | 95 | 95 | 0 |
| pmu-clocks | 20 | 60 | 60 | 0 |
| pmu-power | 20 | 2500 | 2500 | 0 |
| phy-attach | 88 | 206 | 206 | 0 |
| phy-init | 78 | 47078 | 47078 | 0 |
| phy-chanspec | 18 | 26593 | 26593 | 0 |
| phy-cal | 4 | 141130 | 141130 | 0 |
| phy-attach-state | 1260 | 1260 | 1260 | 0 |

`phy-attach-state` counts are state values rather than MMIO accesses despite the generic output label. The strict build result eliminates concern that this run quietly omitted uncompilable files. Radio total is 7,220 accesses and 107 stages, differing from the stale status summary of 5,727 and 85. The complete suite result supports the narrow modeled-behavior claim, not physical-radio correctness.

### Additional oracle vectors expose behavior omitted by the green suite

The specification documents `sub_097809` as a pure two-pointer helper taking `int[3] = {IQ,I2,Q2}` and returning `{angle,gainratio,sinterm}` ([acphy-cal-rx L276-L296](https://github.com/xZinio/bcm4360/blob/eb271ace1c609a604202df7e3f8956856514a46f/docs/re/spec/acphy-cal-rx.md#L276-L296)). The external script `xzinio-oracle-iq.py` uses that documented signature, calls the actual vendor helper under Unicorn, and reads its three signed output words. It does not inspect vendor code or use a card. The native `xzinio-host-numeric.c` was expanded and recompiled to execute the actual open helper on all the same inputs.

```sh
nix shell --impure --expr 'let flake = builtins.getFlake "/path/to/nixos-config"; pkgs = import flake.inputs.nixpkgs { system = "x86_64-linux"; }; in pkgs.python3.withPackages (ps: [ ps.pyelftools ps.unicorn ps.capstone ])' \
  --command python3 -B -u /path/to/research-workspace/evidence/xzinio-oracle-iq.py
```

Both probes executed successfully. The vendor-helper script labels equality against the neutral triple, and that triple is independently confirmed by actual native open execution for all six inputs. These are deliberately additional **helper-output** comparisons, not additional shipped trace scenarios. They all disagree:

| `{IQ,I2,Q2}` | Actual vendor `{angle,gainratio,sinterm}` | Actual open result | Equality |
|---|---|---|---|
| `{0,0,0}` | `{20,1024,0}` | `{0,1024,0}` | No |
| `{100,1000,2000}` | `{-265738,1448,-4634}` | `{0,1024,0}` | No |
| `{-100,2000,1000}` | `{265738,724,4634}` | `{0,1024,0}` | No |
| `{0,1000,2000}` | `{20,1448,0}` | `{0,1024,0}` | No |
| `{0,2000,1000}` | `{20,724,0}` | `{0,1024,0}` | No |
| `{100,1000,1000}` | `{-376068,1024,-6553}` | `{0,1024,0}` | No |

Saved logs: `xzinio-oracle-iq.log`, `xzinio-host-numeric.log`. Six comparisons mismatch, including all five nonzero vectors. Unequal powers alter vendor gain from unity to approximately sqrt(2) or 1/sqrt(2); changing IQ sign reverses phase/quadrature as expected. The open helper does neither. Even the zero-input helper angle differs by 20 Q16-degree units, showing that matching register traces does not guarantee exact intermediate arithmetic. Such tiny zero-input differences can disappear in downstream rounding; the much larger nonzero differences are precisely what the shipped zero-signal model never tests. This quantifies the original source-level stub finding without retracting the genuinely passing 21-scenario result.

## 8. Usefulness relative to aleferri and gonsolo

Comparison is scoped to locally inspected pinned README claims, not a full re-audit of those projects:

* [aleferri/b43-ac-wip at a68a838d8793086ea980b6b71603a6a95623eebd, README](https://github.com/aleferri/b43-ac-wip/blob/a68a838d8793086ea980b6b71603a6a95623eebd/README.md): b43-integrated BCM4352-family bring-up, dispatching 4352/4360, real traces from multiple routers including 3x3 BCM4360 and x86 captures. Primary port target is DSL-3580L BCM4352, FEM6, 5 GHz only; stated MVP includes beacon-on-air with data TX/RX and 2.4 GHz later. Reported September 30/October 1 gates are around 99.8-99.9% for reference cold segments, with lower transfer to other boards. Those percentages measure different trace sets, hardware inputs, granularity and scope, so comparing numerically with xZinio's zero differences is invalid.
* [gonsolo/bcm4360-acphy at 1493b8de401ddefef05916ce8b354f6d99d97797, README](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/README.md): b43 implementation targeted at MacBookAir6,1, core42/radio2069rev4, real hardware traces/decompilation, with repository-reported WPA2 handshake, DHCP and IP traffic on kernel 6.18.53 and ongoing 7.2.7 suspend-poll/scanning/regression investigation. This is materially closer to usable open-driver integration than xZinio's emulator-only hardware layer, but not a certification for MacBookAir7,2 or stable upstream quality. Its extensive decompiled artifacts also require separate provenance/licensing consideration before transplanting content.

xZinio's comparative strength is a readable specification corpus, explicitly separated implementation narrative, freestanding code, vendor-object execution and granular A/B service/state checks. Aleferri supplies b43 integration and measured multi-board/channel trace discipline. Gonsolo supplies live MacBook reception/association/data-path experience and concrete MAC/SHM/firmware/timing failures that xZinio's model cannot expose. Best use is cross-checking algorithms, register sequencing and hardware identities across these independent approaches, not replacing the others because a synthetic score is higher. Even xZinio's statement “the part no open driver has” is not a credible exclusive-priority claim given these contemporary implementations.

## 9. Prioritized follow-through, not performed here

1. Correct status language to separate deterministic modeled calibration orchestration from unimplemented nonzero IQ mathematics; resolve stale September 28 dating and next-step calibration text.
2. Implement and test `phy_calc_iqcc` on nonzero signed cross-power, unequal powers, degenerate/near-zero/saturated measurements; validate coefficient/regression/image arithmetic and fixed-point rounding with independent expected vectors plus oracle comparisons.
3. Extend calibration across both bands, all widths, both revisions, chain masks, multiphase scheduling, scan/roam restoration, error/timeout paths and changing temperature/interference inputs. Count branches/functions and scenarios separately from trace operations.
4. Enumerate every `hw_fw_data` dependency, fix Farrow extraction, tie source-object checksum to manifests, and test using only an extracted bundle rather than live vendor memory. Build an actual firmware-loader/platform boundary.
5. Obtain target-specific identity/SROM and real traces only under a separate hardware authorization. Avoid assuming the synthetic Apple-board configuration equals MacBookAir7,2 internals.
6. Integrate the hardware layer with b43 or bcma/mac80211 and existing core42 support where feasible; validate beacons, receive status, ACK/TX, DMA/IRQ/keys, networking, scanning, suspend and recovery before claiming a working open driver.

**Bottom line:** keep this repository in the research set. It is significantly more than a proprietary wrapper, and its deterministic algorithms and oracle tooling are valuable. Its “all21” claim was reproduced, but is narrowly meaningful: additional pure vendor-oracle vectors demonstrate the unimplemented nonzero IQ path, and the source disproves general calibration completeness. It does not yet provide an open Wi-Fi driver for the target MacBook.
