# Evidence audit: kimptoc/bcm4360-re

**Audited revision:** `7f822c789c7f3fda1aab001f79afb5df81642681`
**Audit date:** 2026-10-02
**Repository:** <https://github.com/kimptoc/bcm4360-re/tree/7f822c789c7f3fda1aab001f79afb5df81642681>
**Scope:** read-only repository evidence review. No module operations, MMIO, hardware access, user configuration changes, commits, or child agents. This is **not** an audit of `0x00000109/OpenBRCM`. Conclusions here must not be transferred to that separate project without checking its own hardware, firmware, architecture, and evidence.

**Late-discovered unmerged evidence:** Section 10 separately audits June 3 branch `0ba568addc0c2d167938da8d5ddeb7cb9b91ac35` and Issue #18. Main's May status is not the latest state across remote branches. The healthy-card trace is valuable, but its claimed identical silicon/ARM firmware is not established.

## 1. Bottom line, with confidence boundaries

1. **This repository demonstrates firmware extraction, chip-specific download/ARM-release work, a reproducible host-written shared-info response, console capture, and runtime ISR enumeration. It does not demonstrate an open working Wi-Fi driver.** There is no demonstrated scan/association/frame-transfer acceptance chain in the reviewed evidence. A successful `set_active`, console pointer, or harness “PASS” is a bring-up result, not network functionality.
2. **The operational BCM4360 `wl` architecture is host-heavy NIC/SoftMAC-like, with D11 microcode and an ARM offload helper.** The README's unqualified “FullMAC” target label is misleading. The presence of substantial `wlc_*` code and PCI-CDC strings inside the extracted ARM image does not demonstrate that it exposes a working FullMAC service to `brcmfmac`.
3. **The current extracted image is best treated as an offload/HNDRTE runtime under the tested initialization, not usable FullMAC firmware.** The late static reachability work supports that model, but overstates “dead code” in places: raw console logs explicitly contain `wl_probe called`, and the repository itself proves the static BFS misses a runtime PCI dongle registration path. The precise boundary is “no demonstrated full operational MAC path or brcmfmac-compatible service,” not “no wl-related code ever executes.”
4. **Adding PCI IDs, changing PCIe to BCDC, and implementing two control callbacks is not an evidenced route to Wi-Fi.** The existing PCIe backend selects msgbuf. The firmware does not publish the expected handshake in these tests. BCDC capability strings/banner do not establish an operational control plus event plus packet ABI. The originally proposed BCDC bridge is superseded in the findings ledger.
5. **The sample remains unusable under the recorded `wl` setup through May 12, but irreversible silicon damage caused by crash testing is not proved.** Persistent attach failure is observed. The supposedly permanent PCIe link degradation recovered, and the later disabled-BAR/CommClk pattern is better explained as failed-bind cleanup or power-management state. The causal damage explanation remains an author hypothesis, not an independently established physical diagnosis.
6. **The latest event audit is a strong practical stopping argument for this campaign, not a universal impossibility proof.** Two registered RTE nodes, no observed dongle ISR logging, a failed OOB pending-bit injection, and a PMU-only chipcommon callback explain why repeated pokes produced no protocol advance. Indirect-call coverage, nested callback-table contents, the exact bus pointer/register chain, and initialization on healthy hardware remain unresolved.

## 2. Evidence handling and provenance

Local `git rev-parse HEAD` returned the requested hash and `git status --short` was empty before review. Citations below use immutable GitHub blob URLs at that hash, not moving `main` URLs. Local paths/line numbers identify the same files. The report distinguishes:

- **Observed:** recorded log output or directly inspected source behavior.
- **Author analysis:** disassembly interpretation, symbol attribution, or historical account that could not be independently rerun against the proprietary input here.
- **Audit inference:** conclusions drawn from those observations, with limits stated explicitly.

Reviewed the README, KEY_FINDINGS ledger, current and historical portions of RESUME_NOTES relevant to closure/rechecks, PLAN, phase5 progress synthesis, phase6 guidance, transport/extraction analyses, latest offload/event analyses, representative extraction and event scripts, current modified `pcie.c`, standalone harness constants, and primary logs for shared-info, console, ISR list, OOB injection, and vendor attach failure. This is not a line-by-line review of every historical test or every driver patch.

**Important reproducibility limit:** proprietary firmware blobs and the original `wl.ko` are not committed. The extraction script explicitly excludes redistributed firmware (`phase1/scripts/extract_firmware.py:20-22`). Several analysis scripts open `/lib/firmware/brcm/brcmfmac4360-pcie.bin` directly. I inspected the scripts and committed outputs/notes, but did not run them or substitute firmware from this machine. Thus firmware MD5, complete disassembly conclusions, and caller counts are attributed to the project's records, not independently recalculated in this audit.

### Source register

References in brackets throughout this report resolve to these pinned files and exact line ranges:

| Ref | File / lines | What it supports |
|---|---|---|
| [R1] | [README.md:5-27](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/README.md#L5-L27), [README.md:49-95](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/README.md#L49-L95) | On-hold/damage framing, FullMAC label, original transport strategy and uncompleted phases |
| [R2] | [KEY_FINDINGS.md:17-58](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/KEY_FINDINGS.md#L17-L58) | Firmware identity, shared-info, runtime uncertainty and corrected host writes |
| [R3] | [KEY_FINDINGS.md:119-129](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/KEY_FINDINGS.md#L119-L129) | Mailbox claims and later routing-confound correction |
| [R4] | [KEY_FINDINGS.md:158-178](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/KEY_FINDINGS.md#L158-L178) | Late runtime/event closure, caveats, May rechecks and vendor failure |
| [R5] | [RESUME_NOTES.md:11-104](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/RESUME_NOTES.md#L11-L104) | Latest May 1/7/12 observations and baseline revert |
| [R6] | [RESUME_NOTES.md:110-157](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/RESUME_NOTES.md#L110-L157) | Apr 29 static closure and now-stale physical-damage synthesis |
| [R7] | [PLAN.md:3-100](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/PLAN.md#L3-L100) | Original brcmfmac/Asahi goal, April 27 frontier, OOB gate experiment |
| [R8] | [phase1/output/firmware_extraction.json:1-55](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase1/output/firmware_extraction.json#L1-L55) | Actual extraction provenance, symbol, size, tag, offsets |
| [R9] | [phase1/scripts/extract_firmware.py:59-167](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase1/scripts/extract_firmware.py#L59-L167), [phase1/notes/firmware_extraction_analysis.md:19-64](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase1/notes/firmware_extraction_analysis.md#L19-L64) | ELF extraction mechanism and early architecture/protocol guesses |
| [R10] | [phase4/notes/transport_discovery.md:5-159](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase4/notes/transport_discovery.md#L5-L159) | Host MAC, D11 microcode/DMA, ARM offload evidence |
| [R11] | [phase4/work/bcm4360_test.c:31-81](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase4/work/bcm4360_test.c#L31-L81) | Target IDs, TCM size, shared-info and ring constants |
| [R12] | [phase4/logs/test.28:179-216](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase4/logs/test.28#L179-L216), [phase4/logs/test.29:213-240](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase4/logs/test.29#L213-L240) | ARM safe release versus failed init/ring progress |
| [R13] | [phase5/logs/test.276.journalctl.txt:1365-1417](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.276.journalctl.txt#L1365-L1417) | Null INTERNAL_MEM, FORCEHT, actual handshake response and timeout |
| [R14] | [phase5/logs/test.278.journalctl.txt:1418-1449](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.278.journalctl.txt#L1418-L1449) | Firmware banner, both probe strings, frozen 587-byte console |
| [R15] | [phase5/logs/test.298.journalctl.txt:1418-1438](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.298.journalctl.txt#L1418-L1438), [phase5/logs/test.298.journalctl.txt:1501-1514](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.298.journalctl.txt#L1501-L1514) | Two runtime nodes, masks, pending pointer and stable late state |
| [R16] | [phase5/logs/test.303.journalctl.txt:1448-1466](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.303.journalctl.txt#L1448-L1466) | ISR count changes 1 to 2 during runtime |
| [R17] | [phase5/logs/test.304.journalctl.txt:1403-1426](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/logs/test.304.journalctl.txt#L1403-L1426) | OOB pending write produces no set bits and later two-node list |
| [R18] | [phase6/t299_t306_offload_runtime.md:17-49](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t299_t306_offload_runtime.md#L17-L49), [phase6/t299_t306_offload_runtime.md:115-126](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t299_t306_offload_runtime.md#L115-L126) | Offload versus FullMAC interpretation and explicit BFS limitations |
| [R19] | [phase6/t304d_pciedngl_isr_disasm.md:17-52](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t304d_pciedngl_isr_disasm.md#L17-L52), [phase6/t304d_pciedngl_isr_disasm.md:58-82](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t304d_pciedngl_isr_disasm.md#L58-L82) | Actual quoted ISR entry and single-bit test, analysis scope |
| [R20] | [phase6/t307_find_callers.py:23-86](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t307_find_callers.py#L23-L86), [phase6/t307_rte_cc_isr_body.py:20-67](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t307_rte_cc_isr_body.py#L20-L67), [phase6/t307_dispatch_table_writers.py:24-112](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t307_dispatch_table_writers.py#L24-L112) | T307 tool inputs and restricted search methods |
| [R21] | [phase6/t275_upstream_audit.md:8-32](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t275_upstream_audit.md#L8-L32), [phase6/t275_upstream_audit.md:99-149](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/t275_upstream_audit.md#L99-L149) | Valid upstream mismatch and superseded bridge speculation |
| [R22] | [phase6/cycle1b_dmesg.txt:1001-1004](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/cycle1b_dmesg.txt#L1001-L1004) | Raw vendor failure printk and detach error |
| [R23] | [phase5/notes/phase5_progress.md:44-116](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/notes/phase5_progress.md#L44-L116), [phase6/NOTES.md:24-119](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/NOTES.md#L24-L119) | Reusable bring-up results and explicit methodological cautions |
| [R24] | [phase6/downstream_survey.md:3-14](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase6/downstream_survey.md#L3-L14) | “Survey” did not actually examine named external trees |

For the next section's source citations, **P** means `phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c` at the audited revision. Actual current line numbers differ from several stale note references.

## 3. What was extracted, and what it is not

### 3.1 Exact extraction identity

The committed extraction record [R8] says the input was a **Linux** `wl.ko` from kernel **6.12.78**, size **7,624,256 bytes**, not a macOS executable. This corrects README wording about “macOS wl.ko.” Symbol `dlarray_4352pci` maps to file offset **0x4A5CB0**, length **442,233 bytes (0x6BF79)**. Its complete recorded tag is:

> `4352pci-bmac/debug-ag-nodis-aoe-ndoe Version: 6.30.223.0 CRC: ff98ca92 Date: Sun 2013-12-15 19:30:36 PST FWID 01-9413fb21`

The second variant `dlarray_4350pci` is **445,717 bytes**, file offset **0x511D20**, FWID **01-518e42f8**. Early variant-to-chip selection was explicitly tentative [R9]. Later use of the 4352 image on the target has stronger evidence: the firmware console identifies **BCM4360 r3**, so this is not merely a guessed family filename [R14]. The recorded MD5 of the working image is `812705b3ff0f81f0ef067f6a42ba7b46` [R2, R19], not independently verified here.

The extractor parses ELF64 sections/symbols and translates a relocatable object's section-relative symbol value to `section.offset + sym.value` [R9]. This is concrete extraction machinery, not a firmware reconstructed from string searches. The first recorded word `0xB80EF000` corresponds to Thumb-2 instruction bytes, not a conventional ARM32 vector address. Early scripts even reported `has_arm_vectors: false`, which was appropriately interpreted as an instruction-set issue rather than proof of corrupt firmware.

### 3.2 Three different things are easily conflated

| Component | Actual role in the repository's architectural evidence | Why the distinction matters |
|---|---|---|
| Host `wl.ko` closed MAC/PHY code | Complete host-resident `wlc_*`/`wlc_bmac_*` NIC operation and direct hardware control | Extracting ARM code does not replace this host functionality |
| D11 microcode/init tables | Timing-sensitive MAC behavior, frame FIFOs, normal/WoWL microcode, register initialization | These are not the ARM download array |
| ARM CR4 `4352pci-bmac` image | HNDRTE plus offload/PCI dongle/shared-code functionality under the tested setup | A running ARM image is not automatically a functioning FullMAC dongle |

Phase4's architecture analysis names **2,958 `wlc_*` functions**, **139 implemented `wlc_bmac_*` functions**, `d11ucode42` (~42.4 KB), `d11ac1initvals42` (~4.8 KB), WoWL ucode, `dma_attach`, `dma64proc`, direct SHM/FIFO/core operations, and the host `wl_isr → wlc_isr` path [R10:49-72]. These are author symbol/disassembly findings, not runtime traces reproduced in this audit, but they form a much stronger architecture argument than the mere existence of an ARM core.

“SoftMAC” here is architectural shorthand for the host-heavy NIC path. It does **not** mean the proprietary `wl` already delegates to Linux `mac80211`. Its own host MAC implementation connects through cfg80211. A new open driver could move appropriate high-level functions to mac80211, but would still need silicon/PHY/D11/DMA support.

### 3.3 Offload-only runtime versus full-MAC code in the blob

Late notes describe two overlapping code families: a live HNDRTE/offload path, and a rich FullMAC-looking `wl_probe → wlc_attach → wlc_bmac_attach → wlc_bmac_up_finish` path not reached by their static bootstrap BFS [R18]. That is compatible with shared Broadcom code and sleep/offload functions including ARP, IPv6 neighbor discovery, beacon handling, GTK/WoWL, filtering and scanning [R10:74-103]. Offload functions can be extensive without making the ARM the normal host-independent Wi-Fi controller.

However, **the absolute “entire wl_probe/FullMAC chain is dead” claim is too strong**:

- The actual T278 console includes `pciedngl_probe called` **and** `wl_probe called` [R14:1420-1422]. A BFS absence cannot erase an executed logging path. It does not prove full `wlc_attach`/MAC-up completion either.
- [R4:166] explicitly recognizes a missed indirect registration path: `pcidongle_probe` is outside the 311-function live BFS, but the ISR list gains its handler at runtime. T303 raw logs show count **1 → 2** [R16]. Static indirect-dispatch incompleteness is demonstrated, not theoretical.
- [R18:32-34] cites **pre-set_active** chain reads returning random data as proof the wlc ISR node “was never populated.” Pre-release uninitialized data cannot by itself prove an allocation never occurs after release. The stronger evidence is the post-release two-node list lacking `0x1146D`, not those pre-release reads.

**Precise audited conclusion:** the observed mode behaves like an idle offload/HNDRTE service and does not expose a demonstrated complete FullMAC service. A FullMAC-looking function family is present, but complete activation and a usable Wi-Fi ABI have not been demonstrated. “Contains FullMAC code,” “wl_probe string executed,” and “operational FullMAC firmware” are three separate claims.

## 4. Positive bring-up evidence and the transport dead end

### 4.1 The handshake is real, but it is not msgbuf readiness

The harness constants [R11] place 640 KB TCM at base zero and `shared_info` at **0x9D0A4**. Its known fields are:

| Offset | Value / interpretation |
|---|---|
| +0x000 | Host magic `0xA5A5A5A5` |
| +0x004 / +0x008 | Host DMA address low/high words |
| +0x00C | Buffer size `0x10000`, 64 KB |
| +0x010 | Firmware response observed as console-structure pointer `0x9AF88` |
| +0x2028 | Firmware-init-done field, observed zero |
| +0x2F38 | Host magic `0x5A5A5A5A` |

Phase4 test28 writes the magic, releases ARM without bus mastering, reads back console pointer **0x9AF88**, but gets **init timeout and zero delivered IRQs**. It records mailboxint **0x3** and intstatus **0x300** [R12]. Its “PASS” means safe release and re-halt, not firmware fully initialized.

Phase4 test29 enables bus mastering after release. It still times out, records olmsg firmware-to-host **wr=0 rd=0**, and returns **-110** [R12:213-240]. This is useful negative evidence against assuming a prepared ring already supplies a functioning runtime transport.

Phase5 T276 independently reproduces the console pointer exactly: host writes and verifies both magics/DMA/size, `set_active` returns true, then **t+0ms** and the poll-end both report `si[+0x010]=0x0009af88`, `fw_done=0`, `mbxint=0` [R13:1387-1395]. The earlier Phase4 mailbox signals did **not** reproduce. Thus the reusable observation is shared-info recognition and console publication, not complete reproduction of interrupt/protocol state.

This is also directly implemented in current source: [P:4615-4669](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L4615-L4669) zeros the structure and writes magics, DMA words, buffer size, and done=0. It precedes `brcmf_chip_set_active` at [P:4689](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L4689). The old ledger claim that Phase5 had “ZERO writes” is explicitly superseded [R2:58]. Do not carry that false diagnosis forward.

The firmware's 587-byte console includes chipcommon **rev43**, PMU **rev17**, chip ID **0x15034360**, and:

> `RTE (PCI-CDC) 6.30.223 (TOB) (r) on BCM4360 r3 @ 40.0/160.0/160.0 MHz`

The write index remains **587** at t+500ms, 5s, 30s, and 90s [R14]. That proves initialization code ran and later console output ceased. Frozen console/state plus the disassembled idle path support WFI, but frozen data alone is not a direct CPU-PC measurement.

### 4.2 Why standard brcmfmac PCIe cannot simply use this image

Current inspected source sets `bus->proto_type = BRCMF_PROTO_MSGBUF` at [P:8096-8103](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L8096-L8103). PCIe control callbacks at [P:3428-3439](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L3428-L3439) just return zero. They are not a working byte transport. T275 documents Kconfig selecting msgbuf and BCDC used by USB/SDIO [R21]. This is a genuine bus/protocol distinction, not a missing chip-ID entry.

The expected firmware-published shared-ram pointer at TCM[ramsize-4] was never observed and the ledger records the NVRAM trailer remaining there [R2:57]. A host-prepared offload shared-info structure is not interchangeable with msgbuf `pcie_shared`, completion rings, flow rings, packet transport, and asynchronous firmware events.

BCDC framing is a separate protocol from PCIe signaling. Even if `bcdc.c` could parse command responses, the project still lacks a demonstrated command buffer, host notification route, firmware notification/completion path, asynchronous WLAN events, and TX/RX data behavior. Two control stubs cannot supply those missing contracts.

### 4.3 Why the BCDC proposal aged out

Early Phase1 inferred BCDC-over-PCIe from `bcmcdc.c` strings [R9]. Phase4 architecture work argued those were shared-code artifacts rather than the normal NIC command path [R10]. T275 later revived a bridge proposal, including a claim that a first CDC command would cause shared-ram publication [R21:137-149]. That latter sequence was a hypothesis, not a successful command/response trace.

T275 also asserted the offload and PCI-CDC analyses concerned **different firmware images** [R21:101-109]. The extraction identity, shared MD5/FWID record, and T278 banner do not establish that distinction. Different interpretations of the same shared-code image cannot be promoted to a discovered alternative firmware asset.

The ledger explicitly supersedes “BCDC-over-PCIe via two stubs is the path,” rates general BCDC viability “LIKELY-WRONG,” and leaves runtime protocol unresolved [R2:43-46, R4 and KEY_FINDINGS:153-154]. Banner/source-file strings establish included code and identity, not a ready network ABI. Similarly, “no msgbuf image in linux-firmware/known sources” is a bounded search finding, **not proof that no suitable image exists anywhere**. T275 says it lacked upstream historical archaeology [R21:25-32], and the downstream survey admits it did not inspect OpenWrt/Asahi trees or search mailing lists [R24].

## 5. Event surface: what the late work really closes

### 5.1 Runtime ISR list is the strongest event evidence

T298 post-release logs directly enumerate:

| Node | Function pointer | Argument | Mask |
|---|---|---|---|
| 0 at 0x9627C | `0x1C99`, Thumb entry 0x1C98, pciedngl ISR | `0x58CC4` | `0x8`, routing bit3 |
| 1 at 0x96F48 | `0xB05`, Thumb entry 0xB04, RTE chipcommon-class thunk | 0 | `0x1`, routing bit0 |
| next | null | | |

`events_p=0x18109000` and `pending=0` accompany the count=2 snapshots [R15]. Later stages retain the two-node state. In T303, count changes 1→2 during the T276 window [R16], confirming live registration and invalidating the suggestion that this is simply stale TCM from a previous boot.

The node at **0x96F48** is the chipcommon thunk, **not a wlc ISR**. That directly corrects the earlier address-based attribution. The wrapper/OOB route is also distinct from PCIE2 mailboxmask. Wrapper bases are EROM-discovered and the OOB router is a separate agent.

### 5.2 pciedngl ISR: single mailbox bit, not olmsg DMA completion

Quoted disassembly [R19:58-82] shows:

- The entry loads a bus-info pointer and prints `pciedngl_isr called` at **0x1CA4**.
- It reads `[bus_info+0x18]+0x20` and tests **0x100** at **0x1CAE**.
- Analysis describes ACK then message-reading/dispatch from a bus-info-local ring, not the `shared_info`/olmsg host DMA ring.

The ledger's corrected reading is that the handler does not walk DMA completion descriptors or service the prepared olmsg ring [R4:168]. The frozen console index is strong evidence that this printf-bearing handler did not execute during the observed dwell windows, assuming the same logging path remained enabled and intact. It is not evidence that a registered handler periodically fired.

Two limits matter:

1. The physical identity of the indirect `bus_info+0x18` pointer was **not** fully traced. Some reports called it a “TCM shadow” or “software register”; the ledger explicitly says that is not proved [R4:167-168]. Register-indirect access can target MMIO just as easily as RAM.
2. The hostready implementation at [P:2875-2880](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L2875-L2880) writes mailbox1 **only if** `shared.flags & HOSTRDY_DB1`. No such usable flag/handshake was obtained here. Absence of a recognized flag explains why the standard path cannot trigger it, but absence of a literal in firmware cannot prove a deliberately different host transport could never use a doorbell.

### 5.3 OOB pending injection has a direct negative result

T304 explicitly saves the BAR0 window, selects **0x18109000**, reads +0x100=0, writes **0xFFFFFFFF**, reads back **0**, and restores the window [R17:1406-1412]. Its verdict is **W1C-or-RO(no-set)**. This rejects the simple “set pending bits by writing this register” mechanism under those conditions.

It does not distinguish W1C from read-only semantics, prove every possible OOB injection mechanism impossible, or provide an electrical measurement of IRQ assertion. It is nonetheless much stronger than a speculative register-name mapping.

### 5.4 T307 closes the remaining chipcommon handler within its search scope

The latest synthesis [R4:176; R6:120-134] describes:

- Thunk **0xB04** loads globals `*0x6296C` and `*0x62994`, tails to dispatcher **0xABC**.
- A **five-entry** callback table at **0x62914..0x6294F**, entries `{mask, function, argument}`.
- Active mask based on chipcommon-context +0x20 and global **0x62950**, with fallback **0x41** under a chip revision/condition test.
- Registration helper **0x63AC4**, a single discovered direct-BL caller at **0x63F44**, registering handler **0x1BA4**, mask **0x20**, arg=0.
- Handler/tail **0x1BA4/0x1B3C** perform PMU/PLL-area acknowledgments and countdown bookkeeping. No reported shared-info/ring/doorbell/protocol progression.

The scripts genuinely implement a direct Thumb-BL target scan and focused disassembly [R20]. But the scope is visible in the source: direct calls only, specific literal construction forms, adjacent `movw/movt` pairs, and disassembly windows. It is not exhaustive whole-program indirect-call/data-flow resolution.

**Critical qualification:** two top-level RTE nodes do **not** establish that the nested five-entry chipcommon table has exactly one occupied entry. Multiple nested callbacks can exist behind the same top-level node. The one direct caller supports one known registration, but the recorded ISR count does not close indirect registrations or direct stores to the nested table. A runtime dump of all five entries would be stronger evidence than arguing from top-level count.

Thus T307 offers a persuasive stopping result for the **known observed configuration**: neither known callback class supplies the desired brcmfmac handshake advance. It does not prove silicon is incapable of host-driven communication, that every initialization state is identical, or that chip replacement alone turns this firmware into FullMAC.

### 5.5 Older “MAILBOXMASK is write-locked” conclusion is confounded

The inspected current source shows:

- [P:2039-2044](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L2039-L2044): `write_reg32` writes `devinfo->regs + reg_offset` directly.
- [P:2300-2323](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L2300-L2323): core selection changes `BAR0_WINDOW` to `core->base`.
- [P:2868-2873](https://github.com/kimptoc/bcm4360-re/blob/7f822c789c7f3fda1aab001f79afb5df81642681/phase5/work/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c#L2868-L2873): interrupt-enable does not itself select PCIE2.

Consequently a zero readback through an incorrectly routed BAR0 window cannot prove PCIE2 hardware refused a write. The ledger later acknowledges this routing confound [R3:129]. Even a well-routed write is not proof it wakes the correct firmware callback.

The claim “zero PCIE2 base literals means firmware never accesses PCIE2” is also too strong. The same ledger explains dynamic EROM-derived addresses and unresolved pointer chains [R4:160,167]. **No literal references** is a valid search result. **No possible indirect MMIO access** is not a valid consequence. Firmware also need not explicitly read a mask register for that hardware mask to affect interrupt delivery. Accordingly, the Apr29 “MBM entirely closed by no refs” language [R6:116] should be read as the campaign's strategy decision, not a proved hardware theorem.

## 6. Silicon degradation claim and the May 12 reprobe

### 6.1 What the records actually establish

The proprietary driver loads/registers far enough to attempt device attachment, then prints:

> `wl driver 6.30.223.271 (r587334) failed with code 1`

A raw boot log also records `NULL ndev->ieee80211ptr` during cleanup [R22]. The ledger attributes the failure site to `wlc_attach` based on static inspection of the probe/printk sequence and distinguishes it from the `Unpatched return thunk in use` WARN [R4:178]. That is a more useful localization than saying module import itself failed.

“Code 1” is not decoded into a uniquely physical fault by the supplied evidence. The exact internal branch/error semantics remain unknown. In a pointer-returning attach API it is especially important to distinguish an error-status output from the attach function's main return value. The recorded printk/code localization supports “attachment failed in/around the closed wlc_attach path”; it does not by itself supply the error's hardware meaning.

The author tried mitigation flags, no-IOMMU settings, and several module parameters, with failure persisting [KEY_FINDINGS:98,178]. This weakens those particular software explanations for those tested pairings. It is not a controlled exclusion of all kernel/package/board/power/environmental causes.

### 6.2 Timeline and supersession

| Date | Observation in repository | Evidential consequence |
|---|---|---|
| Apr28-29 | Multiple hard freezes; endpoint CommClk-/ASPM disabled unlike root port; vendor attach fails | Supports abnormal device/platform state and a cautious stop, not yet permanent damage |
| May1, baseline reverted | Endpoint **CommClk+**, ASPM L0s/L1, **2.5GT/s x1**, clean MAbort; vendor code1 still fails | Refutes claimed permanence of link-state deterioration |
| May7, kernel 6.12.85, after drain/SMC | BARs enabled, CommClk+, normal speed/width; `Timeout+ AdvNonFatalErr+`; code1 at 4.349s | Attach failure persists despite normal visible link state |
| May12, same kernel, after drain/SMC | BAR0/2 disabled, CommClk-/ASPM disabled, but **2.5GT/s x1 link still trained**, assigned addresses preserved; code1 at 3.759s | Disabled/clock-policy state varies separately from persistent attach failure |

May observations are inline captured snapshots in RESUME_NOTES [R5], amended into KEY_FINDINGS [R4:177]. They are not independent raw May journal files inspected in this audit. The author reports **n≥4 reboots**, both **6.12.80/6.12.85**, SMC/reset/drain conditions, and approximately **11 days post-revert** of failure [R5:88]. Repetition is meaningful for persistence, but those boots are not four independent hardware samples.

The author's May12 interpretation is **host-side deactivation after failed bind**, mentioning `pci_disable_device` and runtime PM. That is plausible and much more consistent with the varying BAR/CommClk state than permanent clock-circuit degradation. However, no timestamped trace of the cleanup/PM transition is supplied. Assigned BAR addresses and a trained link do not independently prove the exact cleanup function, or that a device is literally powered down. Treat the specific mechanism as an interpretation, while treating **the link-state permanence claim as refuted by observed recovery**.

AER **AdvNonFatalErr+** persists; the transient Timeout bit clears. An advisory correctable/nonfatal flag is not a semiconductor-damage detector and can remain sticky after recoverable conditions. It is not sufficient physical-cause evidence.

### 6.3 What is not proved

There is no reported board substitution experiment holding software constant, known-good OS/driver comparison on this exact sample after failure, isolated attach-branch diagnosis, power-rail measurement, destructive-failure analysis, or demonstrated pre/post material change inside silicon. Even if a hardware fault were eventually established, its cause could be the card, board/power connection, platform state, pre-existing defect, or another physical mechanism, not necessarily cumulative electrical damage induced by software crashes.

The earlier H1/H3 split itself retained a **NixOS package/kernel difference** hypothesis [KEY_FINDINGS:98]. Reverting command-line/configuration does not necessarily roll back the driver build, package patch set, all platform state, or kernel integration. A handful of mitigation/parameter failures does not eliminate that remaining hypothesis. The ledger's proposed discriminator “another brcmfmac fire fails → H1 confirmed” would also be insufficient: the harness already has independent initialization/protocol and routing failure modes.

**Audited wording:** “Persistent device attach failure on this setup after a hazardous crash-heavy campaign; damaged hardware is plausible, but physical silicon degradation and attribution to crash testing remain unproved.” This neither declares the card healthy nor minimizes the wisdom of stopping risky tests.

### 6.4 Documentation conflicts to preserve, not repeat

- README still foregrounds “degraded at the silicon level” [R1], while May notes downgrade the link evidence and call H1 live [R5:46,86].
- RESUME_NOTES Apr29 synthesis says both blockers are “confirmed” and cites persistent CommClk degradation [R6:138-157]. The May section above it supersedes that evidence. This is chronology drift, not a second confirmation.
- PLAN and phase maps describe ongoing T300/Phase5 work as of Apr27 [R7,R23], while latest status is on hold through May12 [R5].
- KEY_FINDINGS contains explicit corrections to write-lock, “unmask thunks,” wrong structs, fabricated ISR firing, and absent shared-info writes. Status labels such as CONFIRMED must be interpreted with the correction rows, not extracted mechanically.

## 7. What remains reusable and recoverable

### 7.1 High-value reusable work

| Asset | Reusable value | Required qualification |
|---|---|---|
| ELF extraction script plus metadata | Find/download-array resources without hardcoded text-string guesses | Supply lawful local wl input, recheck family selection and hash |
| PCI/BCMA/core/TCM mapping | 14e4:43a0 rev3 Apple target, CR4/D11/PCIE2, TCM base/size, EROM-derived core addresses | Board/chip revision-specific, not universal across Broadcom devices |
| Download adaptations | Chip mapping, rambase0, 32-bit I/O writes, absent INTERNAL_MEM guard, ARM halt/release | Experimental patches, not production-ready lifecycle support |
| Shared-info/console work | Actual host writes, console pointer, log-ring interpretation, known init-done failures | Partial handshake only, missing interrupt/full-ready behavior |
| ISR and OOB tracing | Direct linked-list observations, separate nested dispatch model, pending-register negative test | Registration is not execution, snapshot is not all possible modes |
| Host wl resource analysis | D11 ucode/init-table inventory, MAC/DMA architecture, PMU/PLL/PCIe symbol leads | Symbols do not substitute for exact register sequence or runtime trace |
| Failure logs and methodological corrections | Avoid BAR0-window leaks, distinguish pre/post initialization, reject single-fire causal overclaims | Do not copy superseded claims into new designs |

The repo is particularly valuable as a **negative-result and instrumentation archive**. It narrows what did not work and exposes how quickly a wrong runtime/struct/register model can generate hundreds of low-information patches. The maintained explicit corrections are useful, despite inconsistent summaries.

### 7.2 Recoverable engineering work, not solved functionality

A host-native open NIC/SoftMAC effort could recover the chip/core knowledge and D11 resources, then build toward mac80211 with a genuine MAC/PHY/DMA implementation. It would still face AC PHY/radio calibration, board data/SROM/OTP handling, D11 rev42 microcode loading, interrupt handling, RX/TX DMA FIFOs, channel programming, power management, regulatory handling, firmware/offload interactions, and stable reset/remove semantics. Existing brcmsmac/b43 concepts are reference points, not evidence they already support this AC chip.

A healthy supported vendor setup could enable grounded differential tracing of actual wl initialization and packet traffic. Replacement hardware could restore that **research substrate**. It does not resolve an offload-only firmware ABI or supply a missing FullMAC product.

The damaged-sample question might be recoverable through controlled software/board comparisons, but no such outcome is established here. No recovery procedure was attempted in this audit. Do not rerun the old scripts just because they are available: their historical test path includes hard host lockups, failed watchdog recovery, unsafe reset/lifecycle behavior, and MMIO-routing confounds [KEY_FINDINGS:64-69,83-85; R23].

## 8. When a brcmfmac approach would be justified

There are two very different justifications:

### A. As a restricted bring-up/debug harness

Already justified by demonstrated download, ARM release, shared-info recognition and console observation. That role can reuse selected code with explicit stopping rules and independent validation. It is not an argument that the final driver should remain brcmfmac.

### B. As the actual network driver

Would become justified only with evidence of a suitable firmware/service contract, for example:

1. A lawful image that is demonstrated on **BCM4360 and the relevant board/revision** to initialize the MAC/PHY and offer host-independent WLAN control, events, and packet service; or a substantiated way to activate such a mode in the existing image.
2. Either a real msgbuf handshake/ring implementation, or a fully measured alternative bus transport suitable for a BCDC backend. PCI-CDC banners alone do not meet this condition.
3. Observed round-trip control transactions, followed by asynchronous scan results/link events and functioning TX/RX. Implementing GET_VERSION alone would establish a control path, not the complete WLAN device contract.
4. Stable initialization, timeout/recovery, IRQ/DMA handling, teardown, suspend/resume, board calibration and regulatory behavior on known-good hardware.
5. For a new/modified firmware route, evidence that the change supplies missing MAC/PHY operation and event/data-plane behavior, not merely a WFI wakeup or message parser.

A new firmware implementation could in principle make a FullMAC architecture possible on capable hardware, but that is a major firmware development project. Simply activating rich code in the shared image is not shown to be sufficient, lawful to redistribute, or supported by all necessary board/PHY data.

**Decision rule:** reuse this repo to avoid repeating failed harness hypotheses. Prefer the host-native architecture implied by the actual wl path unless a functioning firmware offload-of-the-entire-MAC service is independently demonstrated. Neither chip replacement alone nor two PCIe BCDC callbacks constitute that demonstration.

## 9. Audit validation and remaining limits

Validation performed: pinned hash/clean-tree check; inspected extraction metadata/parser; compared historical claims against current source line positions; checked shared-info writes against T276 logs; checked console banner/probe strings/frozen index in T278; checked exact ISR pointers/masks and runtime 1→2 transition; checked the OOB write/readback anchors; checked raw vendor failure output; reconciled April damage claims with May1/7/12 snapshots. No operational Wi-Fi tests, binary disassembly reruns, external firmware search, electrical measurements, or hardware operations were performed.

Most significant unresolved evidence gaps are the exact vendor attach failure branch/code meaning, the complete indirect firmware call/data-flow graph, nested chipcommon callback table contents at runtime, the dongle bus-info pointer's physical target, full vendor MMIO/config initialization sequence, and demonstration of any complete FullMAC firmware ABI. Those gaps are why this report supports **campaign-specific dead ends and a persistent failure**, while rejecting claims of proved universal architectural impossibility or proved crash-induced silicon damage.

## 10. Late addendum: unmerged June 3 Phase7 / Issue #18

### 10.1 Branch provenance and scope

Remote `origin/session/agent_c8549f15-1b90-4e62-8756-1d2e77d19740` resolves to **`0ba568addc0c2d167938da8d5ddeb7cb9b91ac35`**, one commit directly parented by the main audited pin. Its [June3 commit](https://github.com/kimptoc/bcm4360-re/commit/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35), by `kiloconnect[bot]`, adds six files/changes: KEY_FINDINGS entries, RESUME_NOTES status, Phase7 analysis and three logs. **No driver implementation changes are present.** I inspected via git show/diff without checkout.

[Branch RESUME_NOTES:11-45](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/RESUME_NOTES.md#L11-L45) changes current state to healthy BCM4360 traces received, Phase7 open. [Phase7 note:1-35](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/notes/issue18_trace_analysis.md#L1-L35) attributes them to @faisala726, TP-Link Archer T9E, Mint22.3/kernel6.14.0-37, wl6.30.223.271, and asserts identical442233-byte ARM firmware to the Apple target.

[Issue18](https://github.com/kimptoc/bcm4360-re/issues/18), fetched during this audit, reports clean vendor wl attachment, WPA2 association and DHCP. This is contributor testimony, not an open-driver success. It links a [gist](https://gist.github.com/faisala726/c10e53e711a2075b57b78c63f257c20d). Immutable branch copies, rather than the mutable issue/gist text, ground the checks below. The369450-event standalone init-only capture is available on request but **not committed**. The included capture is nominally init-to-association.

This contradicts main README's “no phases beyond6” planning statement. It means a project-wide “no progress after May12” conclusion would be wrong. It does not alter main's pinned results or prove recovery of the original sample.

### 10.2 Direct checks of the new artifacts

- [Configspace:1-77](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/logs/healthy_bcm4360_configspace.txt#L1-L77) records PCI14e4:43a0 rev03, subsystem bytes14e4:0619, BAR0 fe400000/32KB, BAR2 fe200000/2MB, Mem+/BusMaster+, driver wl, link2.5GT/s x1, CommClk+, **MSI disabled**, ASPM disabled, clean AER UESta. Useful working-vendor context, not proof that MSI must be enabled for operation.
- [Dmesg:2-19](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/logs/wl_init_dmesg.txt#L2-L19) identifies internal chip **0x4352 rev03 package01**, D11rev42, CR4rev2, PCIE2rev1, and an actual wl interface/banner. It also records b43 rejecting unsupported **AC PHY Type11, Analog12, Revision1**. That corroborates a host-native open PHY support gap.
- [Trace:13-20](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/logs/wl_assoc_mmiotrace.txt#L13-L20) maps BAR2's2MB and **0x4000 bytes of BAR0**, then reads chip word **0x15134352**. Main's Apple fw log says **0x15034360**. Same PCI ID/revision is **not proof of identical internal chip ID/package**. Board/NVRAM differences are not the only differences to investigate.
- Independent awk counts over the committed trace confirm **28493 reads +128296 writes =156789 MMIO accesses**.156803 is file lines including headers/maps, not156803 register events. Header156791 entries corresponds to accesses plus two MAP records.
- There are **zero R/W accesses in BAR2** in this capture. That validates a capture-specific observation, not a universal claim about all wl accesses.
- Width-aware counts: fe4003fc has **62945 four-byte writes +8592 two-byte writes**. fe4003fe has **28384 two-byte writes**,8714 two-byte reads. Combined write bytes at those two ports are **325732**, not a reconstructed442233-byte ARM payload. Repeated indirect-port writes need not represent unique image bytes.

### 10.3 Branch interpretation problems and open work

[Phase7 note:39-118](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/notes/issue18_trace_analysis.md#L39-L118) is preliminary, not a completed core-aware register decode:

1. Its R/W format labels the second field PID, but `R 4 1595.757634 4 0xfe400000...` has **width4** there. The fourth field is mapping ID, not an established CPU identity. MAP physical/virtual addresses are also reversed relative to the note's description. Payload arithmetic depends on widths.
2. It asserts identical `brcmfmac4360-pcie.bin` without ARM image extraction, hash/FWID comparison, or decoded CR4 download on the external card. Same wl version contains multiple firmware arrays and D11 microcodes. “Same firmware” is **not independently substantiated**.
3. It labels MMIO BAR0+0x128 “BAR0_WINDOW,” while main's demonstrated host window selector is **PCI config0x80**. Meanings depend on active core. Healthy config line77 shows config0x80=**0x18001000**, D11 base at that snapshot. This does not decode every trace window, but precludes blindly treating every physical BAR0 offset as a PCIe-core register.
4. It calls **0xb0e7a860** the dominant backplane target without a complete map. That is not one of the established0x180xxxxx/0x181xxxxx core bases. A value written to a hypothesized address port is not proof of a silicon core address.
5. [Note:132-164](https://github.com/kimptoc/bcm4360-re/blob/0ba568addc0c2d167938da8d5ddeb7cb9b91ac35/phase7/notes/issue18_trace_analysis.md#L132-L164) explicitly leaves exact register mapping, MAILBOXMASK/doorbell behavior, post-download poll interpretation, and the wake-trigger write as next steps. There is **no delivered measured firmware wake mechanism**.
6. PCI config switches are not automatically captured by normal mmiotrace. Without corresponding window-switch capture/correlation, assigning BAR0 MMIO offsets to cores can be ambiguous. The proposed vendor-config0x94/B4/B8 extraction may require additional instrumentation.

A stream of D11-region halfword/word writes might represent D11 microcode/object-memory programming, not the ARM download array. This audit does not assign exact register identities without a verified core/window map. The narrower justified point is that these port counts do **not prove the claimed ARM firmware transfer**.

### 10.4 Effect on research feasibility

This materially improves **research feasibility**: a functioning external vendor path now supplies substantial raw traces without firing the original failing sample. It is a real lead for the formerly blocked wl comparison, and the contributor offers targeted follow-up captures. It neither proves nor disproves original-chip physical damage, since board/internal chip ID/OS/package differ.

The data supports host-native wl/D11 architecture research, not automatic BCDC/msgbuf revival. The branch contains no transport code and no open-driver scan/association/TX/RX acceptance result. Its healthy-card firmware identity claim remains unverified.

> **At requested main pin:** campaign on hold after May12 failure and configuration-specific firmware/event dead ends. **On a one-commit unmerged June3 branch:** Phase7 trace analysis reopened using an externally functioning vendor card, with valuable raw data but incomplete and partly incorrect register/firmware interpretation.

**Addendum validation:** read full branch diff and all small Phase7 files, sampled trace start/end, independently counted R/W records/critical widths/BAR2 accesses, fetched Issue18, verified merge-base=main audited pin. Working tree remains unchanged. This is not a complete semantic decode of156803 trace lines.
