# OpenBRCM unmerged branch evidence audit

Audit date: 2026-10-02. Pinned branch `origin/m34d3b-band-init-test`, commit **`22e77166f73c39dbf3d827c949403fda26e93bc8`**, committed 2026-09-28 09:22:00 +0200. Comparison main: **`06d60d610f4e1cba1f20a188453c8f3ba69357fb`**. This is a repository evidence/source audit, not a new hardware result or independently reproduced vendor RE result.

## Executive judgment

**The branch is substantially more advanced than main in diagnostic implementation and analysis, but it is not a working Wi-Fi driver and does not establish BCM4360 MacBook Air viability.** Its newest completed hardware milestone is **M3.4D6, the BCMA/AI D11 core-enable transition only**. The next milestone, **M3.4E, D11 MAC accessibility and internal clock validation**, is design/analysis only, not implemented as the proposed new experiment. D4 PHY bring-up remains blocked. `hardware_test_go` is **NO**. The branch's D3B band-init hardware attempt **failed with device inaccessibility and a platform reset**; completing 73 table writes is not proof of a usable band-init state.

The test target is **BCM4352 `14e4:43b1`, ASUS PCE-AC56 `1043:85ba`, chip revision 3, D11 revision 42, PCIe2 BCMA core `0x83c`**, not an Apple BCM4360 Air board. There is no demonstrated scan, association, real RX frame completion, TX completion, channel tuning, operational RF/PHY, or 5 GHz support. The large new PHY/radio inventories are static evidence, not hardware implementation.

Sources: [canonical current state][state], [authoritative handoff][agent], [milestones][milestones], [representative mac80211 source][mac].

## 1. Scope, comparison and safe audit method

`git diff --numstat` confirms **179 changed files, 59,759 insertions, 391 deletions** relative to pinned main. This is not a small static band-init PR: it adds D3B implementation, central device-loss protection, radio identity probing, extensive diagnostic modes, runtime/crash-capture infrastructure, multiple failed hardware investigation records, D4/AC-PHY analyses, canonical state/ledger generation, Ghidra helpers and external-RE-tool integration. PR #17's earlier static description cannot accurately characterize this final branch.

I exported the pinned commit with `git archive` into `/path/to/research-workspace/branch-export`. No checkout, worktree, Git configuration, commit, child agent, module load/unload, sudo, MMIO, PCI probing, or hardware script was used. All compilations and generated Python cache files were confined to the export.

Mandatory startup was attempted read-only. **`scripts/re-bootstrap.sh` FAILED**: external `re` executable, `re.db`, canonical blob path and verification gates are absent, and this clone's hook configuration is inactive. I did not repair main/config, reconstruct the external index, or do manual vendor disassembly. Accordingly, all vendor instruction/relocation claims below are audited as published repository evidence, not newly independently proven binary findings. Ordinary documentation/source review and pure host helper tests were performed; vendor RE itself was blocked by the bootstrap prerequisite.

The separately supplied vendor object was hash checked successfully:

`/path/to/research-workspace/vendor-input/lib/wlc_hybrid.o_shipped`

SHA256 **`352a6e349f74c69b78e76f68c63752c99b8f6b22dc942af531b754211d7f4743`**. This establishes input identity, not presence or reproducibility of the missing RE database/tooling.

## 2. What is actually hardware proven?

| Area | Most defensible branch conclusion | Critical exclusion |
|---|---|---|
| M2/M2.5 | Historical BCM4352 BCMA bind, validated rev11 external-SPROM MAC, conservative HT 2x2 registration and bring-up milestones | `iw phy` is capability exposure, not RF operation |
| M3.4B RX DMA | Historical FIFO0 RX DMA Level-1 engine bring-up | No real received frame completion proved |
| D2A | Historical isolated 10,850-word microcode upload and bounded PSM start | No PHY/radio/channel proof |
| D2B | Historical isolated 610 common-initvals records and gates | No band-switch/PHY proof |
| D3A0 | Historical isolated 4-TX/FIFO0-RX lifecycle, verified normal quiesce and release | Zero TX payload mappings, no real TX; not safety proof after device loss |
| D3A1 | Historical isolated vendor post-common/pre-PHY tail, DMA interleaving and normal teardown | Stops before band init; one asserted CFP-start readback later corrected |
| MHF/SPROM | MHF3=0/antsel_type=0 hardware evidence on ASUS board; resulting vector `{0x0100,0,0,0,0x0080}` | Board-specific evidence, not Apple configuration |
| D3B | Implemented/static tested; attempted, **FAILED**, NOT HARDWARE PROVEN; standalone checkpoint retired | Table loop completion does not prove postconditions or stability |
| D4 | Analysis/inventories and diagnostic safety infrastructure | No operational PHY/radio checkpoint, implementation GO NO |
| D5/RUN 1 | Addresses, wrapper reachability and core-down entry state measured | Config all-ones/coherency conclusion invalid |
| D6/RUN 2 | Exact three-write AI core-enable transition, `ai_iscoreup=1` | Does not prove D11 MAC readability, clock readiness, PHY or radio |
| M3.4E | Read-only design/analysis, next milestone | Not implemented/executed as the proposed next accessibility experiment |

These historical hardware claims are retained narrow results. They must not be interpreted as sequential completion of all intervening firmware/PHY milestones. D6 is a diagnostic milestone, not recovery of a working D3B/D4 bring-up.

## 3. D3B: two attempts, correction, crash and retirement

The first attempt used candidate `5fa5e5b`, module prefix `3a10aff9`. D2A/D2B/T1/DMA/T2 ran, but the shared D3A1 gate rejected `tsf_cfpstart`: readback `0x3c000000` versus expected `0x02000000`. **No bsinitvals record was applied.** Verified DMA teardown succeeded. The gate was wrong: D11 `0x18c` is a write-only CFP-start programming register, with readable state elsewhere (`0x604/0x606`). The branch removes equality validation there while retaining write accounting and other gates. Historical D3A1 claims must be read with this erratum.

Corrected attempt identity is fully recorded in [D3B postmortem][d3bcrash]: candidate **`2917ca9987ce9aedb58121b375e19208ebf1628c`**, runtime implementation **`ffa2a548911007b58605df51150e24d422d6d957`**, signed module SHA256 **`889710295f2e1c1c80088d333c244220c32127fda7cbc8644cca67c09ab2e1ed`**. The prefix passed, MHF was written, and all **73 band-switch records, 39 16-bit plus 34 32-bit**, completed. About 4.84 seconds later post-D3B reads were all ones, validation failed with `-EIO`, and the driver entered DMA quiesce. No later OpenBRCM log followed. The machine froze/reset; next boot recorded AMD reset reason **`0x08000800`, uncorrected-error data-fabric sync flood**. Pstore was empty.

The original teardown continued after trusted direct registers showed inaccessibility. It could read `0x24=0xffffffff`, write a garbage RMW value `0xfffeffff`, and then issue DMA reset/control writes and polls, possibly core containment. That is a real safety bug distinct from the unexplained initial loss of access. Root cause is **not established**: transient PSM/band-SHM state without PHY, state divergence, core/link/endpoint failure and teardown amplification remain hypotheses. Neither a particular initvals record nor omission of PHY has been conclusively proven causal.

The repository concludes that the vendor continues immediately from band-switch table application into `wlc_phy_init`, with no intervening synchronization/stable checkpoint. **STOP-before-PHY is retired as a standalone hardware milestone.** The proposed combined D3B+D4 boundary itself still needs scope, calibration/PHY-table and bounded-teardown analysis. It is not approved simply because the old stop was bad.

Important source/governance split: `src/ob_d3b.c::ob_d3b_test` and its module mode still exist and can run the sequence. Retirement is a documented safety boundary, **not deletion or unconditional source-level disabling**. The fatal latch protects re-entry after a latched failure, not the first user-invoked run. Do not equate the presence of a callable mode with approval.

## 4. Addressing, reset and sentinel corrections

Newest [address measurement][addr] overrides root-level `REV42-*` histories:

* **Functional D11 `core->addr=0x18001000`; AI wrapper `core->wrap=0x18101000`**, delta `0x100000`, not `0x1000`.
* Both addresses are independent eROM-derived values. PCIe2 config selectors are independently held at `0x80` and `0x70`. BAR slot size is not wrapper-address arithmetic. BCMA owns switching; raw writes to `0x80/0x70/0xac` are withdrawn.
* No positive role, including ChipCommon, is assigned to `0x18000000` on this board by newest canonical evidence.
* RUN 1 candidate did not record `pci_read_config_dword()` status. Its `0xffffffff` config results are **INVALID_EVIDENCE**, kernel PCI error sentinels, not register content. `coherent=0` must be **UNKNOWN**, not a proven incoherent window. Status logging/tri-state coherence is fixed statically later.
* D11 `0x0ffc` has **UNKNOWN register identity** and reads all ones in both core-down and core-up runs. It proves neither unreadability nor liveness nor wrong mapping. The classification string `CORE_UP_D11_STILL_ALL_ONES` describes this observation, not all D11 registers.
* **D11 `0x1e0` is not ChipCommon CLKCTLST.** D11 identity remains UNKNOWN with vendor bit usages 1/5/8/9. ChipCommon `0x1e0` carries FORCEHT/HAVEHT. The conclusion `D11+0x1e0=0x070b0042 => HAVEHT=1` is retracted. The raw value survives, not the clock interpretation. Logging/constants and the historical SB poll predicate are corrected statically, not hardware reproven.

RUN 1 marker `openbrcm-test-20260927-014301-8836`, commit **`cb15383614394b116c30ab9ac2b1b67c35575c5d`**, measured wrapper IOCTL=0, RESET_CTL=1, RESET_ST=0, `ai_iscoreup=0`.

RUN 2 marker `openbrcm-test-20260927-100501-6116`, candidate **`4c97d75af6e99d0c0bbe93492220b256d4af7a40`**, signed SHA256 **`f5ae20908913d4b8fea4d2b0f97cfac22a41ca9ef1b62aa409293824d1224200`**. Exactly three wrapper writes/readbacks: IOCTL=3, RESET_CTL=0, IOCTL=1. Entry reset-held state makes upstream disable early-return; no reset-status poll ran. `ai_iscoreup` changed to 1. Its harness CLEAN PASS means this experiment completed, not Wi-Fi works. **Unload is UNKNOWN/not recorded**, because capture ends at END. Both candidates are spent.

The separate [September 26 reset postmortem][reset] records another abrupt sync-flood reset following window experiments. Last PCI reads preceded reset by about 39 seconds, so causality is not uniquely established. Missing panic/pstore is not exculpatory: platform reset reason is evidence of a serious failure. Historical claims such as SB wrapper-unreachable and generic enable divergence are explicitly overridden, not a mandate to invent reset writes.

## 5. Radio identity, safe access and what remains unknown

[src/ob_radio.c][radio] implements a minimal identity observation, not RF initialization: preparation includes host/backplane, core enable, FAST clock and MAC-PHY clock gating. Then there are **two indirect selector writes** to D11 `0x3d8` and two 16-bit reads from `0x3da`, with trusted direct accessibility sentinels. Thus “read-only radio identity” means no radio data-register programming, **not zero hardware writes overall**. The normal radio identity candidate is frozen/static tested but **NOT EXECUTED** in current canonical state. Earlier attach diagnostics stopped at accessibility gates before the intended radio site, so they do not close the identity question.

The [offline decoder][decoder] derives radio ID from reg1, revision from `reg0 & 0xff`, and class from `(reg0 >> 4) & 0xff`. AC accepts IDs `0x2069`/`0x030b`, but only known 2069 classes close the relevant PLL branch: class 1 -> A, class 2 -> B, other accepted classes -> SKIP. Wrong ID remains UNKNOWN for 2069 PLL reasoning. Ambiguous revisions/all-ones/failed or conflicting captures are rejected. **No guessed branch default is valid**, and decoder-prepared state transition is not applied until real accepted hardware evidence exists.

[src/ob_guard.c][guard] centralizes D11/AXI/ChipCommon access. Trusted direct 32-bit all-ones can latch device loss, while SHM payload/16-bit data does not indiscriminately latch. After latch, reads return dead sentinels and writes are suppressed. D3A0 retains potentially DMA-owned resources, marks fatal and pins the module instead of freeing unverified DMA mappings. This fixes the observed post-loss teardown mistake statically; it does **not prove pre-latch accesses safe**. Diagnostic plain reads do not automatically arm the latch: canonical handoff expressly says `fault-latch=0` alone is not proof of safety.

## 6. D4 corrections that radically change apparent completeness

The latest [pi_fptr relocation proof][pifptr] refutes “AC constructor zeroes callbacks, therefore wlc_phy_init is a no-op.” The repository reports a relocated immediate at `0xa3005` installs `sub_b018f` into `pi+0x28`; the apparent zero in relocatable disassembly was a placeholder. Its full sweep reports 48 installs and zero true NULL stores. This is static constructor evidence, **CONDITIONAL**, not observed runtime dispatch. It invalidates prior D4 scope assumptions that excluded band-init PHY work.

Likewise, older `wlc_phy_init_aphy`/abgphy interpretations are superseded for this AC path. The latest documented path goes through `wlc_phy_init`, anacore, switch_radio ON and `sub_b018f`, followed by channel and calibration work. D4 must cover **attach-time AC work plus band-init PHY work together**. Active blocker: **`d4.phy_boundary.scope`**.

The [canonical operation inventory][ops] reports **13,246 database rows**, 11,246 above the old CLI's 2,000-row truncation point, and static AC closure of **948 functions, 297 with operations**. This supersedes the large older per-revision inventories. These are whole-blob/static upper bounds, not executed writes for this board. Their size should not be mistaken for implemented PHY code. The database is unavailable here, so completeness totals are repository claims, not independently re-counted index facts.

The [operational checkpoint analysis][checkpoint] still finds **no STRONG checkpoint**: radio identity/PLL selection, runtime calibration/channel values, async work, observability and a deterministic postcondition remain unresolved. Its older statement that dev_lost is unwired must be read against the later implemented central guard: existing access safety infrastructure is now present, but the not-yet-implemented operational D4 path is not thereby validated.

## 7. Concrete missing functionality and BCM4360 Air transfer risk

The decisive implementation evidence is not the milestone numbering. In [src/ob_mac80211.c][mac], `start` returns **`-EOPNOTSUPP`**, channel change returns **`-EOPNOTSUPP`**, TX frees/drops the skb, BSS programming is absent, and **5 GHz is explicitly NULL**. [RX source][rx] is diagnostic FIFO0 engine handling and explicitly excludes `ieee80211_rx*` delivery. Host capability tables exposing HT 2x2 do not establish air traffic. No scan/association path can overcome these missing hardware operations.

For Air BCM4360, the branch is useful **research infrastructure**, not a transplantable working driver. Required independent evidence includes exact Apple PCI/subsystem/chip/D11/PHY/radio revisions, BCMA/eROM mapping, OTP/SPROM/NVRAM storage and board values, firmware/initvals applicability, regulatory/channel set, antenna/frontend topology, calibration/power data and suspend/resume/PCIe behavior. None is validated for the Air by this branch. Even a common D11 revision or shared rev11 decoding must not transfer ASUS MHF, PHY initialization or reset provenance automatically. The BCMA ID table matches core revisions 17/23/24/42, not a comprehensive Apple board compatibility whitelist. An incidental match is not support.

No evidence here demonstrates silicon impossibility. The right viability conclusion is **unproven, substantial work and current hardware-risk blockers**, not impossible and not close to usable based on line count. First resolve BCM4352 diagnostic accessibility and vendor-stable operational boundaries, then establish Air-specific provenance before any port/test request.

## 8. Provenance and reproducibility limitations

[Clean-room policy][provenance] declares GPL-2.0 specification-driven implementation, forbids copying proprietary/in-tree driver code, and requires DCO. [Firmware documentation][firmware] explicitly does not bundle firmware and requires exact vendor-derived rev42 slices: 43,400-byte ucode, 4,888-byte common initvals, 592-byte band-switch initvals. The blob hash matches the shared pinned object, but firmware redistribution/licensing and Apple applicability are not solved by that identity check. README's clean-room declaration is a project policy assertion, not this audit's legal determination.

External tooling is recorded at `/media/kartashoff/Storage/opensource/iced/test`, external tooling commit `aa67a9553decd85a93abad1bfcb0c588326cb04d`, database schema 5 and recorded database SHA256 `8a4bc47abb699f908746c64476c4e8a18849c5e8d21f89e093414b8e196d3fec`. The repository ships wrappers/reports but not that database or full external Rust tool implementation. Ghidra/decompiler and several mrbin specs are also outside the checkout. Pinned vendor object availability does not make the full deterministic research pipeline self-contained.

Raw `artifacts/rev42-ai-*` directories and referenced probe traces are **absent from this Git export**. Signed kernel modules and physical captures cannot be independently verified here. Treat their recorded hashes/markers and summaries as documentary hardware evidence, not locally replayed or signature-verified artifacts.

## 9. Evidence hygiene: newest status wins, but inconsistencies remain

1. [README][readme] still says D3B awaits one-shot execution and presents early-main status. Newer handoff/state/postmortem say attempted/crashed/retired. README is stale for the branch.
2. [current-context.json][context] says `generated_from_head=3e5fdf17b7a9eed9eda845e1d019d2669d8236f3` and `dirty_tracked=true`, not the audited export SHA. Its binary/index fields are a captured environment report, not local availability. Use it as an index, not an identity attestation for this export.
3. [Ledger][ledger] dates itself September 25, has older captured repository HEADs, records `D4D-AI-ENABLE` as NOT HARDWARE PROVEN while later EXECUTED record supersedes it, and uses `merged` to mean committed on this branch, **not merged into default main**.
4. `state/current-state.json` contains “FIFO0 RX engine brought up with real traffic” in a summary. This contradicts README and authoritative historical scope, which explicitly say no real RX frame completion. Do **not** infer RX proof from this overstatement.
5. Handoff contains historical “no active blocker”/pending-retest passages and an older “Last failure/reset” summary even though the separate Sept26 postmortem records a later reset. They are not current permissions. The latest active blocker and canonical hardware GO=NO prevail.
6. Many milestone status strings extend the prescribed vocabulary (`HARDWARE RUNTIME PROVEN`, SIGNED, FROZEN, SPENT). Distinguish actual hardware observation from candidate packaging and static proof regardless of label.

## 10. Safe validation performed

* All **14 inspected C host executables** built and passed: math, caps, DMA, IRQ, RX, firmware, ucode, initvals, D3A0, D3A1, D3B, guard, radio and diagnostic tests. Radio executable reports **80 cases PASS**.
* Firmware/common-initvals tests explicitly **skipped missing `/lib/firmware/brcm/bcm4352-*initvals42.bin` files**. Build emitted `-Wmaybe-uninitialized` warnings in `ob_fw_test.c` stats handling. Thus PASS does not establish exact installed real-firmware validation.
* `tests/host/test_device_lost_guard.py` passed all source-centralization/gating checks.
* `tests/host/test_radio_probe_decoder.py`: **19 synthetic decoder tests passed**. Inspection confirmed no runtime CLI/module invocation in these chosen tests or imported decoder.
* `scripts/generate-artifact-ledger-md.py --check` passed: Markdown mirror matches JSON. This verifies synchronization, not truth of every record.
* Shared vendor SHA256 matches published provenance exactly.
* Bootstrap failed for external tooling/hook reasons above. No kernel module build, KUnit run, full `make hosttest`, docs-check shell pipeline, runtime harness, hardware script or new binary RE was executed. The full host target includes runtime CLI and external-tool tests, so I deliberately selected known-safe subsets rather than treating its name as a safety guarantee.

**Overall confidence:** high in source-level nonfunctionality, target mismatch, branch scale and current documented GO/STOP status; documentary rather than independent runtime confidence in historical physical runs; no independently established Air compatibility or vendor callgraph completeness.

## Pinned source references

[main]: https://github.com/0x00000109/OpenBRCM/tree/06d60d610f4e1cba1f20a188453c8f3ba69357fb
[state]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/state/current-state.json
[context]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/current-context.json
[agent]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/agent-state.md
[milestones]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/milestones.md
[ledger]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/artifact-ledger.json
[d3bcrash]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d3b/d3b_crash_postmortem.md
[addr]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/d11_addr_u1_measured.md
[reset]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/REV42-SYSTEM-RESET-POSTMORTEM.md
[radio]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_radio.c
[decoder]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/radio_probe_decoder.md
[guard]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_guard.c
[pifptr]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/d4_pifptr_relocation_proof.md
[ops]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/phy_radio_ops.md
[checkpoint]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/operational_checkpoint_analysis.md
[mac]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_mac80211.c
[rx]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_rx.c
[provenance]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/provenance.md
[firmware]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/firmware.md
[readme]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/README.md
