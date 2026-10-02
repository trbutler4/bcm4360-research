# gonsolo/bcm4360-acphy: pinned evidence and viability audit

Audit date: 2026-10-02. Repository HEAD verified as `1493b8de401ddefef05916ce8b354f6d99d97797` (2026-10-01 22:09:44 +0200). Read-only inspection of repository and archived evidence. No modules loaded, hardware/debugfs accessed, user configuration changed, or commits made. The only executed project test was an isolated, fully mocked userspace wrapper test. This report is outside the repository.

All file references below are relative to the pinned repository. Permanent source URL prefix:
`https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/`.
A reference `path:Lx-Ly` is therefore a commit-pinned evidence locator, not a reference to moving master.

## 1. Executive judgment

**This is credible real-hardware reverse-engineering progress on exactly a MacBookAir6,1 BCM4360, but not a reliable, complete, portable or upstream-ready open driver.** It demonstrates that an open host driver plus proprietary D11 firmware can achieve WPA2 association, DHCP and meaningful legacy-rate IP traffic on the author's laptop. It is more than an emulator or a trace replay passing its own test. However, the RF/PHY bring-up still depends heavily on snapshots of the author's `wl` state, and the newest evidence reports only about **21% clean fresh initializations**, with reload-until-connected as the operating workaround. Its advertised 5 GHz receive functionality is explicitly retracted by later notes. HT/802.11n and VHT/802.11ac are missing end to end.

For a MacBookAir with the same chip, radio revision, PHY revision and board/FEM configuration, this is an unusually relevant research specimen. It is not evidence that any BCM4360-equipped MacBookAir will work, and it is not a sensible drop-in replacement for the user's only network path. No independent hardware reproduction was performed in this audit.

**Most important correction:** the README is dated 2026-09-29 and points to note102, but HEAD contains notes through113 dated 2026-10-01. Do not summarize current viability from README alone.

| Capability | Latest defensible state | Evidence class and locator |
|---|---|---|
| 2.4 GHz, 20 MHz legacy station | Real WPA2, DHCP and IP traffic reported, including a functioning main link after retries | Author hardware report, note33:L1-L16, L117 onward, note106:L46-L53, note110:L15-L20 |
| Fresh initialization reliability | Approximately 21% clean per try in latest wrapper campaign, many failed authentication attempts and suspend timeouts | Retained hardware logs plus author aggregation, note106:L20-L31, note105:L14-L24 |
| Long-lived connection | Clean init reportedly remains usable for hours, but no comprehensive controlled soak or broad AP matrix established | Author synthesis, spec:L643-L658, not an independent acceptance test |
| 5 GHz RX | Latest monitor test receives zero frames on 5180 and 5580 MHz, including after partial ch116 replay | Author hardware negative result, note111:L34-L52 |
| 5 GHz association/TX | No successful association established, six attempts confounded by both-band bad init | note111:L28-L32 |
| HT/n, VHT/ac, MIMO throughput, aggregation | Not implemented as a complete data path, not merely disabled by a flag | Source plus note113:L3-L16 |
| Legacy rate/performance | TX PHY 54 Mb/s, author-reported upload18.2 Mb/s and download10.5 Mb/s after TX-status fix | note110:L15-L32, source main.c:L1435-L1446 |
| Host suspend/resume | A NixOS post-resume reload hook exists, not a demonstrated robust native resume implementation | tools/install_b43_resume_hook.sh:L1-L26, commit message says tested on a copy |
| Power/RF correctness | Runtime calibration and TX power callbacks missing, temperature/voltage and regulatory RF behavior unverified | phy_ac.c:L3131-L3139, spec:L620-L623 |
| Mainline suitability | Author explicitly says non-clean-room code is unsuitable as-is | README:L135-L142, spec:L5-L32 |
| Firmware freedom | Open host code, not an entirely firmware-free stack | README:L144-L157, spec:L64-L70 |

## 2. Correct the historical narrative before judging the project

### 2.1 The kernel regression was measured, but its causal attribution did not survive

Notes76 and90-92 contain genuine-looking archived comparison results, not merely guesses. Note76:L64-L91 reports 5/5 successful reference-kernel connections versus 0/5 on7.2.7. Note90:L42-L62 reports clean connect captures and 38/38 near-instant steady-state suspend samples on6.18.53. Note91:L65-L69 reports15/15 samples with psctl0 ms and wait0-3 ms. Note92:L15-L32 reports16/16 initial-connect samples with wait79-86 ms on7.2.7.

The retained logs corroborate the **observed difference in those sessions**: `test-logs/dmesg_618_suspendtiming_185619.txt:L2-L20` contains near-zero waits and channel switches, while `test-logs/dmesg_727_suspendtiming_final_190812.txt:L1-L28` contains suspend failure, PHY debug0x5, MacBookAir6,1 identification and wait85 ms. This is stronger than a bare README claim.

But the claim that this conclusively proves a kernel logic regression is too strong:

* The notes' repeated phrase "identical driver binary" actually means the same driver source/logic **rebuilt against each kernel**, not an identical module file. Note90:L25-L29 and L135-L139 describes per-kernel binaries and vermagic differences. Module layout, dependencies, kernel config, userspace generation and hardware history are not magically controlled away by identical source.
* **80 ms is predominantly a failed poll's elapsed timeout, not a measured late successful hardware acknowledgment.** `b43-src/main.c:L3185-L3212` performs35 short polls then up to40 `msleep(1)` iterations, prints failure and continues. Sleep rounding can make this near80 ms. Saying the ucode takes80x longer *to set the bit* is misleading when it never sets the bit in the measured interval.
* The timestamp called psctl ends **before** the MACCTL masked write/readback (`main.c:L3186-L3190`). Thus the logged wait includes that write and flush, not only the single-register read loop. This contradicts note92:L36-L42's assertion that everything up to the flush is already accounted for in psctl. The measured bottleneck remains useful, but instrumentation is not as sharply partitioned as claimed.
* Note103:L44-L70 describes first-parent bisect ending on a KVM merge with **both parents good**, `CONFIG_KVM=n` still bad, and a filemap/mempolicy restoration flipping the result. Note103:L86-L92 interprets it as indirect timing/layout, not a single revertable logical culprit.
* **Note104:L23-L32 explicitly revises that again:** one initialization per boot mostly measured a good/bad init coin flip. Note105:L7-L24 localizes the proximate problem to PHY TX errors and ucode busy mid-TX, not NAP or the host kernel. Latest spec:L715-L719 even lists kernel version/commit as ruled out.

The defensible audit conclusion is narrower than either absolute narrative: **earlier version-correlated failures were observed, but a reproducible causal kernel regression is not established at HEAD.** The one-init-per-boot bisect is not trustworthy under a roughly20-30% successful-init process. Nor do the latest negative tests rigorously rule out every kernel timing effect. Repeat adequately powered, randomized hardware A/B campaigns before calling it kernel-independent. The stable finding is that suspend waits fail after managed TX/PHY malfunction.

[Core timeout source permalink](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/b43-src/main.c#L3175-L3224)

### 2.2 Notes93-102 are mostly test infrastructure progress, not improved Wi-Fi reliability

These notes document a remote builder and many bespoke bisect boot problems: storage/VFAT, HID dependencies, absent getty, clean shell exit, VT/graphics, missing i915, replacing minimal config with the real NixOS config and a generic initrd, missing `/run/current-system`, and USB firmware search-path ordering. Note102:L1-L11's "desktop fully worked" is a desktop/bootstrap success, not a successful BCM4360 reliability campaign. Note103 later reports actual candidate results. Treating note102 as the current radio status obscures the October1 findings.

### 2.3 "5 GHz receive works" is false for the latest tested implementation

README:L65-L69 and L115-L118 claim 5 GHz tuning/RX works. Note53:L25-L43 actually validates **register readback**, not received packets or an association. Latest note111:L34-L38 explicitly corrects this: 32 frames over8 s at2462 MHz, zero at5580 and5180 MHz, scans showing only2.4 GHz BSSs despite advertising38 five-GHz channels.

Note111:L40-L52 explains a plausible mechanism: the code applies wl's **80 MHz channel112 first-load snapshot**, but then retunes selected radio/BW/Farrow values while keeping the core at20 MHz. It does not reproduce the extensive per-band/per-core PHY, table, SHM and MMIO switch state. A797-operation ch116 partial ordered replay still yielded zero five-GHz RX frames, versus96 on2.4 GHz. That negative does not prove all replay-based five-GHz experiments impossible, only that this implementation and extracted window do not work.

[Latest five-GHz evidence permalink](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/notes/111-txphyerr-shm-record.md#L28-L52)

## 3. What networking evidence really demonstrates

### 3.1 Real traffic milestone

Note33:L1-L7 describes WPA2 four-way handshake, DHCP and actual AP/gateway ICMP replies seen in tcpdump on the b43 interface. The note explains four concrete replay/SHM bugs: accidental legacy key-table clearing, stale MAC filters after restart, replaying a one-shot CTS command, and zeroing per-rate autonomous ACK PLCP templates. This is not merely a simulated handshake. Source contains explicit AC key handling, AC address-match/template setup, TX header generation and status parsing. The overall hardware milestone is plausible and technically specific.

However, it is author-generated evidence from one machine. Routing can confound naive traffic checks when the USB backup and b43 share a subnet/default routes. Note76:L75-L81 explicitly found that problem and used tcpdump to resolve it. It matters when interpreting later speed or ping claims without interface-isolated raw captures.

### 3.2 Reliability has deteriorated from short historical streaks to a measured retry process

The newest useful campaign is note106:L20-L31:43 wrapper tries,9 judged clean, three of12 runs giving up with six tries. Default raised to12. Under an **independent constant p=9/43 model**, failure after12 tries is about6%. That is only a heuristic: correlated bad-init streaks, parameter changes and false judgments invalidate a guaranteed reliability number. Note111:L30-L31 reports18 bad in a row and wonders whether five-GHz scans worsen state. Each reload may take a minute or more and affects shared supplicant links.

The boot workaround was actually enabled and tested once on7.2.7 (note106:L46-L53): first try rejected, second connected and held25 s, total52 s. This establishes one recovered boot, not robust first-try connectivity. Successful wrapper runs were still connected40 s later. No multi-day acceptance result follows from this.

Retained `test-logs/wrapper-live-102514.log:L1-L24` corroborates retry behavior, **and supplies a useful contradiction**: run3 exited1 after six bad judgments, but was `connected`40 s later (L18-L19). A connection can succeed late after being classified bad. The wrapper is a practical heuristic, not an oracle labeling physical initializations.

Latest source `tools/b43_load_until_connected.sh:L25-L31` has12 tries, WAIT70 s and SETTLE25 s, not the earlier note's30 s/six-try settings or source comment's45 s. Successful state is checked twice25 s apart (L61-L69), not monitored continuously throughout. It does not prove traffic throughput, WPA rekeying, AP-side ACK health or continuous connectivity. A silent interface mismatch is returned as success/quiet (L88-L90). Note107:L20-L23 already observes a wlan0 rename race against the hardcoded expected name.

### 3.3 Managed unicast TX is more discriminating than scan or injected frames

Note105:L14-L24's118-attempt aggregation reports90 not-connected attempts, median11 PHY TX errors, versus28 connected with almost none. Scans cannot detect bad init:23/24 scan phases have no errors even when connection later fails (L62-L67). Fixed-channel monitor injection of20 directed probe requests at6 Mb/s over40 inits produced only two error-bearing inits and no suspend failures (L50-L60). Therefore "it injects packets" or "scan works" is not an acceptance test for managed networking.

The PHY errors correlate strongly with failure, but not perfectly: seven of90 failed attempts had zero logged PHY errors. Also errors are masked at lower debug verbosity (note106:L21-L23). A good/bad analog calibration explanation is a leading hypothesis, not established causality. Static snapshots over50 inits did not identify a causal separating register. Mid-connect snapshots were confounded by different scan/association channels (note104:L47-L52, note105:L45-L49).

### 3.4 Rates, n/ac and performance

`b43-src/xmit.c:L244-L307` creates a real AC-specific descriptor from the actual outgoing skb, with12 legacy rates, software-crypto fallback, per-packet ACK expectation, channel spec and PLCP. It is not replaying wl's actual network frames. A fixed hardware rate entry is generated from mac80211's chosen rate. The lack of HT is visible in PLCP's dead FIXME:MIMO branch (L179), legacy RX decoding (L876-L879), lack of HT caps and aggregation feature setup, and note113:L3-L16. VHT and40/80 MHz networking are likewise absent. Firmware/constant tables containing MCS names do **not** mean usable MCS networking.

Note110 identifies a convincing TX-status bookkeeping error: the driver summed a constant ACK byte as an additional transmit attempt. Current `main.c:L1435-L1446` uses `v2 & 0xff`, capped15, with a knob restoring the wrong old sum. The author reports54 Mb/s TX PHY,24 MB upload in11 s (18.2 Mb/s),10.5 Mb/s download and fewer reported retries. These are author live measurements, not this auditor's replayed results. No standalone reproducible iperf run/environment manifest was located for that measurement. The improvement is plausible because rate control previously interpreted near50% failure at every rate.

Autonomous ACKs are **not completely solved**: note110:L18-L32 reports ~9% duplicates/retransmissions and AP downlink at24 Mb/s, attributing this to firmware-generated SIFS response PHY TX errors. Thus README's "original ACK blocker long since resolved" is true for a historical catastrophic SHM bug, false if read as all autonomous ACK reliability fixed. Spec:L630-L635 attributes a different residual5-10% loss to background scanning while L721-L724 attributes duplicate frames to ACK malfunction. Do not collapse those different metrics into one harmless scan loss statistic.

## 4. How much is algorithm versus replay?

The best characterization is **an actual b43 networking/MAC implementation whose usable PHY operating state is largely wl snapshot scaffolding**, with a partial port of low-level radio sequences and a substantial body of diagnostic/untested calibration helpers.

### Implemented behavior, not just an opaque replay engine

* Generic b43/mac80211/BCMA/DMA foundations remain actual code. AC DMA/status changes, AC RX format handling, AC TX descriptor construction, address-match table, FIFO geometry and beacon templates operate on actual current traffic/state.
* Radio register access uses the core revision to select the right pair (`phy_ac.c:L421-L461`). Two cores are special-cased for4360 boards0117/0137 (L463-L470).
* Radio2069r4 power-up/init is implemented (L489-L547, L659-L668). **There are real RCAL and RCCAL procedures** with reads/polls and per-core writes (L549-L657), plus VCO calibration kick (L1042-L1054). Saying "no calibration at all" would overstate the gap. These are not the missing complete RX IQ/TX IQ/LO/TSSI/temperature/watchdog chain.
* Per-channel radio lookup/tuning, band-control, BW register programming, Farrow values and resetCCA are present (`phy_ac.c:L1016-L1068`, L1128-L1159, L1214-L1305). They still use directly extracted tables and omit much surrounding vendor logic.

### Replay dependence

The operating setup in the author's boot service is `ac_replay=1 dma32=1 ac_por=63 nohwcrypt=1` (note106:L14-L16,L40). `phy_ac_replay.h` has1550 lines, `phy_ac_por.h`4346, `phy_ac_por5g.h`4464, and `phy_ac_win116.h`801. These line counts are size indicators, **not percent implementation completeness**. `phy_ac.c` itself is3161 lines, including extensive experiments/debugfs and untested TX-calibration helper code.

* ch6 replay writes final radio/PHY/table/SHM state and fixed AGC lookup arrays (`phy_ac.c:L2816-L2880`). It can rerun on each return to ch6 unless state-once/init-state knobs suppress it (L1256-L1267). Later note104:L53-L57 warns that rate-limited replay log lines cannot count executions accurately.
* POR application writes captured final radio/PHY/table/SHM/ChipCommon/PMU state by bitmask, including whole-register PMU masksets (L951-L1013). It skips invalidated entries and the ACK template SHM range precisely because replaying a final vendor state was not semantically safe (L984-L992).
* The decoded first-load summary contains267261 parsed events and132678 PHY writes, reduced to295 final PHY registers,163 radio registers,3022 table entries and1093 SHM words (`traces/decoded-firstload/summary.txt:L1-L12`). These are **final values**, not an equivalent ordered initialization algorithm.
* `tools/decode_trace.py:L10-L17` explicitly produces both final-state files and an ordered seq. `gen_replay.py:L29-L39,L51-L64` consumes the final-state files, groups writes by device category, excludes table-port registers, includes only shared SHM and chip/reg control PMU, not the complete trace order/branch decisions/calibration execution. It does not replay reads or adapt to analog measurements. Reproducing snapshot values cannot certify the correct transient RF sequencing.
* The ch116 experiment is a genuinely ordered but **partial** replay: `gen_switch_window.py:L39-L49` retains PHY/radio/table/delay and drops SHM/MMIO/wrapper events. Its negative hardware result cannot rule out those omitted components.

### Exact missing algorithm families

1. Reliable complete initialization including runtime **RX IQ + RX AFE + TX IQ/LO/LOFT** and correct measurement tone/radio loopback context.
2. Idle TSSI, temperature sensing/compensation, actual TX power target/gain programming and per-band/per-board RF policy. `recalc_txpower` returnsDONE and `adjust_txpower` is empty (`phy_ac.c:L3131-L3139`).
3. Dynamic AGC/noise/desense/ACI/CRS threshold updates and the real vendor periodic PHY watchdog. The15-second hook does diagnostics and RX poison-buffer retry, not equivalent RF adaptation (`phy_ac.c:L2964-L2990,L3084-L3121`).
4. Correct band transition, five-GHz RX/TX gain/FEM/bandwidth/clock/table state, not80 MHz snapshot plus20 MHz retuning.
5. Actual rev11 SROM consumption and board-specific FEM support, not debug-only prints.
6. HT/VHT descriptor/control/MCS feedback, RX encoding/BW/NSS parsing, capability advertisement, rate adaptation and A-MPDU mechanisms.
7. Validated power-saving, suspend/resume and coexistence behavior.

Note108:L20-L34's RX AFE attempt is an instructive failure: without proper context the engine timed out, with a partial window it measured zeros, and applying those values would corrupt LOFT tables. The patch is saved but **reverted**, not a working calibration feature. A faithful port needs the full preceding RX IQ/loopback/DDS chain, state tracking and2.4 GHz validation. The author's proposed dependency on the independent port's future2.4 GHz support is a follow-up, not existing functionality.

## 5. Portability to a MacBookAir

Strongest match: author's actual machine is **MacBookAir6,1**, PCI14e4:43a0, chip4360 revision3, D11 core42, **AC-PHY revision1**, radio2069 revision4, board0117. Hardware identity is retained in `test-logs/dmesg_727_suspendtiming_final_190812.txt:L4-L6` and spec:L639-L641. The spec's introductory "PHY core revision42" wording (L72-L74) conflates D11 core revision with AC-PHY revision. Do not compare42 to the driver's `dev->phy.rev <= 1` condition and conclude mismatch.

The newest SROM result is particularly important: stock BCMA uses wrong rev8 offsets on a rev11 image. Debug-only decoding finds **txchain3/rxchain3, two antennas, FEMctrl2**, not earlier sprom txchain6/rxchain0/garbage FEM values (note112:L3-L18). Other collaborator boards reportedly have FEMctrl6. Current driver does not consume the decoded values. Source only prints them (`phy_ac.c:L166-L181`). The clean-room spec still claims txchain6 atL689-L691, demonstrating it too is stale in places.

Radio lookup rejects anything other than2069r4 (`phy_ac.c:L1034-L1035`), power-up likewise rejects other radios (L716-L719), tables/init only coverPHY rev0/1 (L2898-L2910), RCAL assumes unparsed boardflags3 zero (L549-L552), and additional board flags remain unidentified (L485-L487). These are not broad BCM4360-family compatibility guarantees. A matching PCI ID is insufficient to guarantee identical board calibration/FEM/antenna and radio-revision conditions.

Harness portability is also poor: `tools/b43_boot.sh:L10-L29` hardcodes `/home/gonsolo`, PCI0000:03:00.0 andbcma0:1. The connect test hardcodes interface/AP profile and uses local tool paths. `b43-src/Makefile` has a specific Nix-store6.18.53 development path and forces CONFIG_B43_PHY_AC despite Kconfig:L151-L158 still labeling itBROKEN. NixOS snippets import the author's `/etc/nixos/configuration.nix`, not a self-contained portable system definition. Per-kernel recompilation and firmware deployment are necessary.

**Implication for the user's MacBookAir:** if exact model/card/board identity is not yet established, the coordinator should keep compatibility conditional. Read-only normal PCI/system identity can establish similarity, but even exact matching does not eliminate the author's low-init-success and freeze risk. Do not advise live wl-to-bcma switching on the user's primary link to "see if it works."

## 6. Suspend/resume, recovery and operational danger

Do not confuse **MAC suspend** (microcode stops packet operations while channel configuration occurs) with **laptop suspend-to-RAM**. The kernel-regression notes primarily concern the former. They are not native system sleep/resume validation.

`tools/install_b43_resume_hook.sh:L13-L25` installs a NixOS service after sleep targets that restarts the reload-until-connected service, restricted to kernel7.2.7. Commitbabc351's message says the installer was "tested on a copy". The script's assertion that resume re-initializes into the same coin flip is a rationale, not a logged repeated suspend-resume acceptance campaign. No retained controlled repeated sleep/rekey/link-traffic matrix was identified. Spec:L726-L732 rates power management/suspend/coexistence about5% understood, explicitly an author's subjective estimate.

Specific dangers:

* README:L166-L174 documents a hard freeze from experimental five-GHz bandwidth change with live TX.
* **Latest note112:L20-L24 documents a whole-machine hard hang from merely walking PHY/radio debugfs on five-GHz ch116**, requiring hard reboot and leaving empty logs. Read-only register operations are not hardware-safe just because they do not write a data register. `phy_ac.c:L55-L63` shows PHY reads perform MAC suspend/enable.
* The internal ACK watchdog's counter was semantically wrong: TXACKFRM counts ACKs **sent**, not acknowledgments received for local TX. `phy_ac.c:L2987-L2990` disables it by default and ties restart path to suspected freezes. It is not a working RF watchdog to enable casually.
* `b43_mac_suspend` increments its suspended bookkeeping even after timeout (`main.c:L3210-L3215`). Subsequent channel/RF work may proceed despite no actual hardware suspend acknowledgment. This is a plausible operational hazard visible in source, not a newly confirmed root cause.
* Reloads restart shared wpa_supplicant on this NixOS setup and disconnect even the USB backup (note105:L73-L75, note106:L43-L53). A backup link in the same daemon stack is not fully independent safety isolation.
* wl swap can be one-way until reboot (note90:L22-L24). Firmware-class path overrides and stale module vermagic caused prior failures (note90:L31-L40,L135-L144).
* TX RF power correctness/legality over voltage/temperature is explicitly unverified (spec:L620-L623). Software crypto support and software regulatory channel filtering do not replace calibrated emitted power/spectral validation.

The existing netwatch/autorecovery/reload wrappers reduce inconvenience, not kernel crash probability or RF uncertainty to production levels. They do not turn an experimental driver into a safe primary network dependency.

## 7. Raw evidence, tests and provenance

### Positive evidence assets

This is not a claims-only repository. It retains seven compressed raw wl traces, decoded first-load/ifup and five-GHz directories, final wl dumps, MAC dumps, numerous dmesg/ftrace/functional graph logs, A/B results, snapshot files and SHM error records. `git ls-files test-logs` lists1212 tracked files, approximately32 MB, although many are repetitive diagnostic snapshots rather than independent end-user tests.

The first-load capture harness instruments low-level osl read/write/config/delay entry points (`firstload_trace.sh:L31-L43`). Archived first-load logs report **zero overruns** (`test-logs/firstload-20260926-190438.log:L67-L72`, five-GHz equivalent:L77-L82). That mitigates trace-buffer loss concerns for those captures. All seven `.trace.xz` archives passed `xz -t` in this audit. Compression integrity does not prove trace semantic completeness, instrumentation perturbation absence or missing DMA information.

The hardware-result archive is internally informative: raw failure logs show actual PHY/MAC state and authentication timeouts. Their credibility is stronger than mock tests, but still author-generated and not an independently reproduced chip acceptance test.

### Limits

* MMIO logs do not capture outgoing DMA frame bytes or full HT/VHT TX descriptors. Note110:L31-L32 explicitly identifies this limitation. Source-format correctness can be known for legacy packets without revealing HT rate entry control.
* Snapshot files show final state, not causal analog/internal state. Post-connect snapshots can simply encode selected channel, association status and counters. Notes104-105 expressly admit this confounding.
* Trace decoder is heuristic: most-common PHY select determines BAR0, most-common config window determines D11 target (`decode_trace.py:L83-L96`), and tracefs read-return matching is perCPU/op (`L47-L65`), not a general nested call-identity reconstruction. This is usable research tooling but not a formally verified event decoder. I did not rerun full decode and independently certify all logical operations.
* Multiple traces referenced by note/source are only available asmeta files, not a corresponding raw archive, for example184726 and212541 September27. The exact referenced original raw dataset is not universally present at HEAD.
* `tools/ab_reload_test.sh` is repeatedly cited in notes103-105, but **not tracked/present**. `connect_test.sh` is present, but does not fully substitute for missing higher-level arm orchestration, kernel candidate configuration and all per-run artifacts. `bisect-boot/` is deliberately regenerated/deleted (note103:L42), so the complete booted candidate manifest is not retained.
* No wl binary, extracted table payloads, Ghidra project or firmware are present. Their exclusion is intentional (.gitignore:L16 onward). The inspected documentation does not provide a complete content-hash-pinned binary-to-firmware/tables recipe. README:L152-L157 admits extraction is not packaged into one script. Rebuilding generated tables from scratch is not reproducible with this checkout alone.
* The many A/B arms are small, often6-8 attempts, use differing parameters and contain interface-name/NM errors. They are sufficient to show gross unreliability, not to definitively rule out every hypothesis. `test-logs/ab_reload_awakerel_031325.log:L1-L19` illustrates missingwlan0 errors before a failed auth record. Distinguish invalid harness runs from physical-radio failures before estimating probabilities.
* The spec's70%/25-30% completeness figures (L726-L732) are subjective author estimates, with no formal requirements denominator or coverage map. They are not a measured remaining-work percentage.

### Audit-run safe tests

1. `TMPDIR="$JCODE_SCRATCH_DIR" bash tools/test_b43_load_until_connected.sh`: **10 scenarios passed**, including success first/third try, all-bad give-up, quiet retention, failed-load retry, auth/suspend error thresholds, mild failure, connection after a few suspend failures, and transient link drop. Inspection first established external commands fully mocked viaB43_LOAD/RMMOD/NMCLI/DMESG, B43_KMSG=/dev/null and B43_SLEEP=true (`test_b43_load_until_connected.sh:L1-L3,L14-L52`). No real interface/module/network command ran. This validates wrapper control logic only, not the hardware premise.
2. `xz -t traces/*.trace.xz`: seven archive integrity checks passed.
3. A read-only awk aggregation over all retained `ab_reload_*.log` records with "PHY TX errors during connect" found **152 attempts,35 connected,117 other**,33 connected with zero logged PHY errors and9 other with zero. This differs from note105's118 because HEAD has additional later experimental arms. It supports the general correlation, but must not be presented as a clean152-attempt baseline or independent dataset. The118 report is a historical subset, not necessarily an inconsistency.
4. `git status --porcelain` before/after remained empty. No kernel build was attempted, because it would create repo build artifacts and requires exact development headers. No real radio validation was attempted.

## 8. Clean-room specification: useful bridge, not legal or technical closure

[Specification provenance permalink](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/docs/AC-PHY-CLEAN-ROOM-SPEC.md#L3-L77)

The author is unusually explicit: this driver was written with proprietary decompiled logic visible, is **not clean-room** and is not fit for mainline as-is. The intended two-team boundary is a separate implementer who has never seen wl.ko **or b43-src**, using only a reviewed behavioral specification and independently sourced tables. The spec cautions that legal review is required and firmware licensing remains separate. These are appropriate caveats, not proof that the document itself has legally solved provenance.

Concrete source reinforces the caveat:

* `gen_radio_2069.py:L2-L24` reads literal `chan_tuning_2069rev4` values from fixed wl.ko section offsets. It generates77 entries from8932 bytes.
* `gen_tables_phy_ac.py:L2-L7,L20-L38` consumes Ghidra-dumped binary data fromwl.ko and emits C arrays preserving vendor table order.
* `phy_ac.c` repeatedly names proprietary functions and decompiled branch logic. RCAL/RCCAL/tuning behavior is directly adapted research, not evidence of a separated implementer.
* Decompiled code and D11 microcode disassembly are tracked. README's "no extracted binary material" is reasonably interpreted as **no opaque firmware/binary blobs**. It cannot mean no data derived from binary extraction: literal numeric radio/init arrays clearly are included as C source.

The spec is valuable for AC TX/RX/status/SHM layouts and known failure modes. It is **not self-contained**: generic b43, independent calibration/tuning captures and proprietary firmware are prerequisites (L44-L70). It also includes stale or overconfident statements:

1. Header target confuses core42 with AC-PHYrev1.
2. Radio address selection described as capability-bit-driven (L100-L109), while current source selects based on core revision (phy_ac.c:L421-L436).
3. txchain6 atspecL689-L691 superseded by note112's actual rev11txchain3/rxchain3.
4. Main body promises stable end-to-end operation but appended runtime section says21% clean initialization.
5. "Every transmission" errors on bad init overstates the managed-auth specificity and successful scan/monitor injection evidence in note105.
6. "No64KB alignment needed" and many "ruled out" statements exceed what12 attempts or small negative A/B samples can prove. They mean not supported as the dominant explanation in those tests.
7. Fixed-selection-only legacy rate wording (L627-L629) is less current than note110's corrected mac80211 legacy rate adaptation result.

A prospective clean-room implementer needs a frozen, internally corrected spec, independent table capture/provenance manifest, firmware acquisition/legal review and acceptance tests on multiple boards. Simply copying this tree into a GPL patch or reading the spec after studying decompiled sources does not recreate the stated separation.

## 9. Ranked bottlenecks and realistic next milestones

### 1. Reliable managed-TX/PHY initialization and autonomous response health: blocking every practical use

Evidence: ~21% clean tries, PHY errors at unicast auth, no useful separating static snapshot, stale replay calibration, residual failed ACKs even on a good link. Most likely research direction is the **full context-sensitive calibration/FEM/RF sequence**, but the mechanism is still unknown. Negative isolated AFE experiment does not rule out complete chain. Acceptance: randomized clean/cold/reload/resume cohorts, repeated managed WPA2/DHCP with independent over-air observation, PHY error-free auth and measured AP retry/ACK rates. Do not classify init solely by scan.

### 2. Board-specific SROM/FEM/gain/power and replay elimination: blocking portability, RF assurance and deterministic bring-up

Evidence: rev11 values only printed, unknown flags assumedzero, author's FEMctrl2 differs from collaborator boards, TX power callbacks are stubs, frozen calibration data. Acceptance: actual SROM-driven board parameter consumption, independently captured/derived data with hashes and branch coverage, successful operation withoutac_replay/ac_por, frequency/temperature/power validation. This is a substantial driver implementation, not a short switch fix.

### 3. Five-GHz full mode transition: blocking dual-band

Evidence: latestzero RX,80/20MHz hybrid and negative partial ch116 replay, unsafe register reads. Needs complete PHY/core bandwidth/clock/gain/AGC/FEM/table/SHM transition, calibrated TX chain, non-DFS andDFS AP tests under normal client rules. Register readback is insufficient. Do not propose live debugfs sweep as the next user experiment.

### 4. HT/VHT and aggregation: blocking modern performance

Evidence: missing capabilities, TX MIMO/HT control and PLCP, MCS/NSS/BW RX/status parsing, aggregation, rate-control feedback. Requires new DMA descriptor capture/research and verified data path, not changing an advertisement bit. Legacy54 Mb/s already gives useful low-end networking if reliability is fixed, but AC branding of the chip does not deliver AC rates here.

### 5. Native power management, recovery and production lifetime: blocking dependable laptop service

Evidence: forced AWAKE, resume reload hook rather than native guarantee, wrapper false-negative/quiet behavior, interface rename races, shared supplicant disruption and restart freeze suspicion. Acceptance: repeated sleep/resume, idle power measurements, WPA rekey/roam, long-duration load/scan, no whole-host freezes, predictable module deployment across kernels.

### 6. Clean-room/provenance and integration packaging: blocking upstream or redistribution-ready release

The repository can be useful research even before this is solved. A separated implementation/spec review and deterministic firmware/data sourcing are necessary for upstream readiness. Read-only audit cannot give a legal clearance. Kconfig remainsBROKEN and out-of-tree source with machine-specific scripts is not a distro integration plan.

## 11. Supplemental remote-branch and issue provenance audit

Follow-up requested by the coordinator on 2026-10-02, performed without checking out or modifying the repository. The older remote branch **`origin/wip-5ghz-tx` at `a920890b458d3fc79671b1047c7a687ea2cff777`** is dated **2026-09-27 00:30:32 +0200**, several days before the October 1 master findings. It is not a newer rescue implementation. Its merge base with pinned master is `6b399f0d4cc07d0f3ae599a4742458a403c77b95`; exactly two commits are branch-only: `f987109` (commit subject explicitly says **WIP 5 GHz TX, untested**) and `a920890` (ACK setup/sub-band sweep tools). They modify seven files with 85 insertions and 15 deletions relative to that base. No new notes or test logs are committed in the branch-only delta, and the old branch predates this repository's README.

### Useful unmerged datapath research, but not validated networking

The branch has three genuinely relevant small changes absent from current master:

1. **Full PHY chanspec retained for TX.** `b43-src/phy_ac.h` stores `u16 chanspec`; channel switch sets a normal 20 MHz spec and, when replaying the 80 MHz vendor state, reads the actual chanspec from SHM (`phy_ac.c:L954-L979` at the branch commit). TX then uses that spec instead of always synthesizing a 20 MHz one.
2. **Legacy frame control sub-band in a wider PHY channel.** The TX header sets PhyTxControlWord_1 low bits from chanspec bits8-10, with a runtime `ac_txsb` override for experimental sweeps (`xmit.c:L240-L242,L286-L315` at the branch commit). Master still writes zero to that PHY control word. This is potentially useful future five-GHz/wide-channel descriptor research, but it does not build an HT/VHT PLCP or prove wide-channel data TX works.
3. **RX center-channel to primary/control-channel conversion.** RX derives the primary channel from center-channel plus sub-band for 40/80 MHz encodings (`xmit.c:L766-L785` at the branch commit). This is a metadata decoding improvement, not complete HT/VHT RX MCS/NSS/status support and not evidence that the PHY receives frames.

[Branch TX chanspec/sub-band logic](https://github.com/gonsolo/bcm4360-acphy/blob/a920890b458d3fc79671b1047c7a687ea2cff777/b43-src/xmit.c#L286-L315)

[Branch RX control-channel metadata](https://github.com/gonsolo/bcm4360-acphy/blob/a920890b458d3fc79671b1047c7a687ea2cff777/b43-src/xmit.c#L766-L785)

The branch also changes `ac_5ghz` from bool to uint, with value2 suppressing the 2.4 GHz band advertisement so an idle station stays on five-GHz (`main.c:L5452-L5454`). This is isolation tooling, not additional validated band support. `tools/ack_setup5g.sh:L1-L18` explicitly loads the **80 MHz channel112 replay** with `ac_5g_80=1`; it creates a monitor interface and scans5560 MHz. The generic gateway ping at its end is not interface-bound, so even an observed “network ok” there would not alone establish BCM4360 traffic rather than the backup link. `tools/txsb_sweep.sh:L1-L20` injects unicast frames while trying sub-band values and reads ucode transmission/error counters. It is a proposed hardware experiment, not an archived successful sweep. It also touches the exact wider-bandwidth/debugfs territory where later notes report freezes, so it should not be run casually.

**Effect on the main judgment:** retain these small chanspec/primary-channel changes as possible useful nonmerged research. Do not mistake the branch name, test script existence or inherited old trace archive for working five-GHz TX. There is no branch-only recorded successful association or packet test. The branch predates master note111's zero-RX findings and note112's debugfs hang warning and does not supersede them. It does not change the latest viability verdict.

### Public issue1 establishes trace exchange, not completed driver support

GitHub API inspected on 2026-10-02:

- Issue [`gonsolo/bcm4360-acphy#1`](https://github.com/gonsolo/bcm4360-acphy/issues/1), opened by `aleferri` on2026-09-28T22:47:12Z, asks **“Can you send me a 2.4Ghz mmio trace for the 4360?”** and says the requester is also developing a4352/4360 driver.
- The only comment, dated2026-09-29T09:14:31Z, says **“Never mind, there were in traces already”**. [Exact comment permalink](https://github.com/gonsolo/bcm4360-acphy/issues/1#issuecomment-5887236886).
- The issue was closed by `aleferri` on2026-10-02T12:03:38Z, state_reason `completed`. [Issue API](https://api.github.com/repos/gonsolo/bcm4360-acphy/issues/1), [comments API](https://api.github.com/repos/gonsolo/bcm4360-acphy/issues/1/comments).

This independently corroborates public availability/use of the raw traces and collaboration described in notes108-109. **The closed issue means the trace request was fulfilled or unnecessary, not that two-way2.4 GHz support, TX reliability, calibration or five-GHz support was fixed on October2.** Issue metadata is newer than pinned master but is not a newer code/hardware acceptance result. No other repository was audited for this supplement.

## Appendix: exact evidence path index

`spec` means `docs/AC-PHY-CLEAN-ROOM-SPEC.md`. Bare source filenames mean the file under `b43-src/`, and bare tool filenames mean the file under `tools/`. Numbered note abbreviations mean these exact files:

- note33: `notes/33-status-2026-09-28-wpa2-handshake-and-real-ip-traffic.md`.
- note53: `notes/53-status-2026-09-28-farrow-ported-to-5ghz.md`.
- note76: `notes/76-possible-kernel-7.2.7-regression-not-a-firmware-bug.md`.
- note90: `notes/90-status-2026-09-29-6-18-53-reference-capture-suspend-is-genuinely-near-instant-regression-confirmed-kernel-side.md`.
- note91: `notes/91-status-2026-09-29-irq-ack-race-hypothesis-refuted-suspend-split-further-baselined-on-6-18-53.md`.
- note92: `notes/92-status-2026-09-29-conclusive-the-entire-80ms-is-the-suspend-ack-poll-nothing-left-to-split-in-driver-code.md`.
- note93: `notes/93-status-2026-09-29-remote-compile-server-and-first-bisect-kernel-staged.md`.
- note94: `notes/94-status-2026-09-29-first-bisect-boot-hit-emergency-mode-vfat-fix-rebuilt.md`.
- note95: `notes/95-status-2026-09-29-second-bisect-boot-no-input-fixed-hid-chain-plus-text-console.md`.
- note96: `notes/96-status-2026-09-29-third-bisect-boot-no-getty-fixed-with-explicit-systemd-wants.md`.
- note97: `notes/97-status-2026-09-29-fourth-bisect-boot-login-succeeds-shell-exits-instantly-debug-shell-staged.md`.
- note98: `notes/98-status-2026-09-29-fifth-bisect-boot-vt-switch-doesnt-work-shell-exits-clean-pivoting-back-to-graphical.md`.
- note99: `notes/99-status-2026-09-29-sixth-bisect-boot-graphical-login-worked-no-i915-driver-caused-broken-rendering.md`.
- note100: `notes/100-status-2026-09-29-switched-to-nixos-config-plus-generic-modprobe-everything-initrd.md`.
- note101: `notes/101-status-2026-09-29-eighth-bisect-boot-no-apps-run-current-system-missing-fixed-initrd-only.md`.
- note102: `notes/102-status-2026-09-29-ninth-bisect-boot-desktop-fully-worked-no-usb-stick-network-firmware-path-timing.md`.
- note103: `notes/103-bisect-first-pass-result.md`.
- note104: `notes/104-alessio-patches-tried-all-negative-and-the-bimodal-init.md`.
- note105: `notes/105-ucode-wake-analysis-nap-is-a-side-effect-phy-tx-error-is-the-discriminator.md`.
- note106: `notes/106-load-until-connected-wrapper.md`.
- note107: `notes/107-tx-tables-gain-calibration-checked.md`.
- note108: `notes/108-alessio-reply-and-afe-calibration-port-attempt.md` and reverted `notes/108-afe-cal-port-attempt.patch`.
- note109: `notes/109-dma-ring-alignment-refuted.md`.
- note110: `notes/110-tx-status-attempt-count-bug-fixed-upload-16x.md`.
- note111: `notes/111-txphyerr-shm-record.md`.
- note112: `notes/112-srom-rev11-decode.md`.
- note113: `notes/113-ht-feasibility.md`.

[Latest SROM and hard-hang warning](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/notes/112-srom-rev11-decode.md#L3-L24)

[HT end-to-end gap](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/notes/113-ht-feasibility.md#L3-L16)

[Latest retry-wrapper hardware results](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/notes/106-load-until-connected-wrapper.md#L20-L53)

[TX status fix and real traffic measurements](https://github.com/gonsolo/bcm4360-acphy/blob/1493b8de401ddefef05916ce8b354f6d99d97797/notes/110-tx-status-attempt-count-bug-fixed-upload-16x.md#L8-L32)

## 10. Bottom line for the coordinator

Use **"real2.4GHz legacy networking demonstrated on the author's MacBookAir6,1, but mostly-replayed PHY state and roughly21% clean fresh-init success at latest HEAD, made usable experimentally by retries"** as the headline. Do not repeatREADME's five-GHz-RX-working, reliably-reconnecting or conclusively-kernel-regression claims without the later corrections. Latest5GHzRX isnegative, HT/n/acmissing, TX54Mb/s PHY isnot18Mb/s AC operation, and system suspend safety isnot established by MAC-suspend timing.

The project greatly strengthens the feasibility argument that open host-side BCM4360 operation is possible. It does not remove the hard analog calibration, board adaptation, TX timing, modern-rate and provenance work. For the user's primary MacBookAir network, the safe present judgment is **research target with backup/recovery required, not production replacement**.
