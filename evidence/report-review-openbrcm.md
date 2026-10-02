# OpenBRCM / architecture synthesis review

Reviewed `REPORT.md` on 2026-10-02, before coordinator revisions. Scope: architecture, OpenBRCM evidence and roadmap safety/governance. No report edits or hardware operations. Line numbers below refer to that pre-revision report.

## Exact suggested qualifications

1. **Phase F, lines 405-411:** Move synthetic device-loss/timeout testing, IRQ/work cancellation, DMA-lifetime verification and containment/recovery contracts into prerequisites for physical Phases D/E. Keep reload/resume campaigns as later expanded acceptance. Suggested sentence: “Before physical RX/TX experiments, require host-side fault-injection coverage and a reviewed DMA/IRQ containment and recovery contract; subsequent lifecycle campaigns expand, rather than introduce, those protections.”

2. **Line 411, leak acceptance:** Replace “no ... silent DMA leak” with: “No untracked resource loss or free-before-verified-quiesce. Explicitly recorded retained DMA mappings, a pinned module and reboot-only recovery are acceptable fail-closed containment after device loss, not successful teardown.” OpenBRCM deliberately retains uncertain DMA-owned resources. A blanket leak-free/unload-success gate would contradict its safety design. Sources: [D3A0 lifecycle and containment][d3a0], [postmortem Part A][crash], [handoff isolated DMA lifecycle][agent].

3. **Lines 192/203, retired D3B checkpoint:** Add: “Retirement is a documented safety boundary, not source-level disabling: `bsinitvals_test_only` and `ob_d3b_test()` remain callable. Their existence is not current approval to run them.” Sources: [postmortem §B16][crash], [D3B top-level function][d3b], [core module parameter and dispatch][core].

4. **Line 201, reproducibility:** Add: “Referenced raw RUN 1/2 captures and signed module artifacts are absent from this Git export, so their physical results are documentary, not independently replayed or signature-verified here. Some README/context/state summaries are stale or inconsistent; newest scoped canonical records prevail.” In particular, generated context identifies an earlier dirty HEAD, README still describes D3B as awaiting a run, and the current-state 'real traffic' summary conflicts with the explicit no-frame-completion boundary. Sources: [RUN 2 canonical record][freeze], [current context][context], [README][readme], [current state][state]. Export absence was checked locally and is recorded in [branch audit](openbrcm-branch-audit.md), §§8-9.

5. **Diagram, lines 109-114:** Label ARM node/edge “optional offload path, not required/proven for the proposed native SoftMAC path”; label radio “2069 on inspected boards”. The diagram should not imply that a functional ARM service is a demonstrated prerequisite or that radio identity transfers automatically to the user's unidentified Air. OpenBRCM's examined native implementation is BCMA/mac80211, while its radio identity/PLL branch remains hardware-required. Sources: [mac80211 integration][mac], [radio identity probe][radio], [current state open blockers][state]. ARM service interpretation remains bounded by the report's Kimptoc evidence, not independently reviewed in this OpenBRCM pass.

## Optional wording precision

* Line 182 heading: “staged bring-up and explicit safety governance” instead of “rigorous staged bring-up”, to avoid suggesting the failed checkpoint had already established rigorous physical safety.
* Line 188: explicitly say “D6 proves the AI-wrapper core-enable transition only; D11 MAC accessibility, clock readiness and operational PHY/RF remain open.” [RUN 2 canonical record][freeze] and [current state][state] distinguish the exact three-write proof from those nonclaims.

Otherwise, the scoped architecture and OpenBRCM readiness statements accurately distinguish source/static proof from physical functionality. These are review recommendations, not repository changes or new hardware evidence.

## Pinned sources

All OpenBRCM sources are pinned to `22e77166f73c39dbf3d827c949403fda26e93bc8`.

[d3a0]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_d3a0.c
[crash]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d3b/d3b_crash_postmortem.md#L415-L580
[agent]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/agent-state.md#L494-L545
[d3b]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_d3b.c#L269-L366
[core]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_core.c#L136-L144
[freeze]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/m34d4/rev42_ai_enable_freeze.md
[context]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/current-context.json
[readme]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/README.md
[state]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/docs/state/current-state.json
[mac]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_mac80211.c
[radio]: https://github.com/0x00000109/OpenBRCM/blob/22e77166f73c39dbf3d827c949403fda26e93bc8/src/ob_radio.c
