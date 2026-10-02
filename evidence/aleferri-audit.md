# aleferri BCM4352/BCM4360 reverse-engineering viability audit

**Audit date:** 2026-10-02. **Source revision:** `aleferri/b43-ac-wip` at exactly `a68a838d8793086ea980b6b71603a6a95623eebd`, subject `enhance test by using real d11 core code`, author/committer timestamp `2026-10-02T13:12:35+02:00`.

**Adjacent repository:** the local default `main` of `aleferri/b43-add-bcm43xx-ac` is `fee3317cc7936dd2bfdf25e7f7ca6eae3601afb5`, dated 2026-09-22. Its only working-tree file, `README:1`, says `work moved to https://github.com/aleferri/b43-ac-wip`. It is a redirect, not a second current implementation. Web-search results still reference its old `master/sprom-rev11` paths. Those search snippets are not evidence about the audited redirect HEAD or about current upstream acceptance.

All source citations below are relative to the pinned b43-ac-wip tree, unless explicitly identified otherwise. A permanent URL can be formed as:

`https://github.com/aleferri/b43-ac-wip/blob/a68a838d8793086ea980b6b71603a6a95623eebd/<path>#L<line>`

**Follow-through:** [d11-interpreter-audit.md](d11-interpreter-audit.md) pins the public external interpreter at `2361e9e8aad9f2912877b82be5cc529b3dd390a1` and reproduces actual version-stamp instruction execution on an already-local, byte-order-normalized firmware image. It supersedes the earlier external-dependency availability limitation, but does not establish full firmware boot or RF success.

## 1. Executive assessment

**This is a substantial, unusually well-documented trace-driven bring-up project, not a demonstrated working replacement for `wl` on BCM4360.** It is worth contributing to, particularly its SROM decoding, hardware-I/O capture pipeline, AC-PHY calibration research and regression infrastructure. It is not yet a credible daily-use Wi-Fi driver, and the repository does not establish completion of its own on-air MVP.

The strongest result is reproducible: the actual PHY source compiled in a userspace harness matches the selected, normalized D6220 cold traces at **99.89% on ch36/20**, with both documented 43-segment sweep ranges reproduced. This is excellent evidence that much of the vendor-observed programming sequence has been reconstructed. It is **not** evidence that 99.89% of the hardware works, that a beacon was transmitted, that association succeeds, or that 802.11n/ac traffic works.

Important limits:

1. README explicitly says there is **no recent hardware run** (`README.md:86`), but independent issue #4 documents a September 30 real BCM4352/ARM64 attempt, with no visible beacons after local fixes. See the hardware addendum below. Vendor `wl` captures include real association and traffic. Port-loaded register dumps also exist, so it would be wrong to say that nobody has ever loaded the port. Neither those dumps nor the replay scores establish successful RF operation of this exact HEAD.
2. Production 2.4 GHz channel switching is deliberately rejected (`b43/phy_ac.c:10137-10142`). The unit harness overrides this with `ALLOW_24=true`.
3. HT/VHT receive capability bits are advertised, but HT/VHT TX headers and RX rate interpretation are unresolved. Requested MCS transmissions are dropped. An 80 MHz tuning trace is not an 802.11ac data-path validation.
4. MacBookAir6,1 coverage has improved materially: a dedicated profile and its FEM table are present. Router scores still do not transfer to this 2x2 x86 laptop. PMU, driver-version, power and calibration differences remain.
5. The latest “real d11 core” commit adds a **C state model and decoded-write replay**, plus glue for an **external** microcode interpreter. It does not turn the integration harness into a real firmware-driven hardware simulator. I reproduced several false-positive state-equivalence cases and found swapped microcode overlays in its wrapper.
6. The integration harness has important known abstractions: dummy firmware, empty initvals, oracle-supplied firmware revision, artificial suspend handshake, inline work, and poison RX buffers whose frames are dropped. Its reported successful `probe/start` and interrupt counts must be read in that context.

**Practical verdict:** promising research base for a narrow, board-qualified 5 GHz legacy-rate bring-up. Not presently proven usable on the air, not general BCM4360 support, not functional n/ac support, and not upstream-ready as one large driver series.

## 2. Audit method, safety and evidence boundaries

The original repository was inspected read-only. Initial and final `git status --porcelain` were empty, `git rev-parse HEAD` matched the requested hash, and final `git diff --quiet` returned 0. No source edits, commits, branches, module loading, hardware access, network-interface operations, firmware installation, kernel configuration changes or package installation were performed. No child agents were used.

Inspected commands before running them: unit Makefile and gates, integration Makefile/fetch/apply scripts, D11 Makefile/wrapper, SROM Makefile, band-delta script, and relevant Python processing paths. Builds ran only after exporting a pinned copy via `git archive HEAD` into:

`/path/to/research-workspace/evidence/aleferri-host-audit/`

All build products, extracted capture archives, synthetic fixtures and logs are there. This is an audit copy without `.git`, not a modification of the original checkout. Compiler was **GCC 15.3.0**, interpreter **Python 3.14.7**. Unit, D11 and SROM userspace builds succeeded without compiler warnings in the captured build logs. Scratch artifacts occupy approximately 765 MiB at the measured point, primarily capture extraction and the pinned copy.

Evidence categories used here:

- **Reproduced:** ran an inspected host-side command against this exact source/capture set.
- **Source-confirmed:** directly visible implementation, not necessarily exercised in a real kernel.
- **Repository-reported:** documented experiment or score not independently reproduced here.
- **Not established:** no suitable acceptance result, or a dependency prevented execution.

The full integration build was attempted at its prerequisite check and blocked because `/usr/src` does not exist on this host. I did not install headers or silently substitute another kernel version. Thus the two integration percentages below are repository-reported, not reproduced by this audit.

## 3. What the source actually implements

This is considerably more than PCI-ID recognition or a placeholder PHY. The source inventory includes 10,821 lines of `b43/phy_ac.c`, 1,744 of `radio_2069.c`, 1,153 of `tables_phy_ac.c`, 276 of `ppr_ac.c`, and modified core/DMA/TX/RX/bus/LED code. Raw size is not a quality measure, but it establishes the scale and review burden.

### 3.1 Entry points and supported silicon

`docs/driver-status.md:9-29` maps the entry points to callers. The source confirms:

- `op_init` requires **BCMA** and chip ID **0x4352 or 0x4360** (`b43/phy_ac.c:6037-6051`).
- Channel switching requires radio **2069 rev 4**, with a frequency-table lookup (`b43/phy_ac.c:10163-10175` and subsequent lookup). This is not blanket support for all AC-PHY revisions or all BCM43xx devices.
- The table supports 5 GHz synthesizer rows at 5170-5825 MHz. Bonded widths use the block center, rather than mistuning the synthesizer to the primary 20 MHz center. Table presence still does not grant regulatory permission to transmit.
- `op_init` probes cores, initializes the analog front end, programs chip-dependent PMU fields, loads mode/tables/registers, and latches first-bring-up state (`b43/phy_ac.c:6067-6122`).
- Software rfkill, analog switching, channel calibration, power recalculation, 1-second/60-second work, radar polling and noise completion are wired, not merely named callbacks (`docs/driver-status.md:19-30`).
- Core support includes rev-42 reset/init differences, DMA ring alignment, address-match table and shared-memory layouts, beacon template placement, AC TX status handling and revised channel/capability registration.

The distinction between the PHY and the rest of the MAC/core is important. The unit harness compiles the PHY-side files and **mirrors** selected core work at vendor-observed points. The integration harness is the place intended to test real b43 core callers. A unit match does not prove the live core executes mirrored work at the right time.

### 3.2 Kernel configuration remains explicitly broken/experimental

`b43/Kconfig:151-158` still makes `B43_PHY_AC` depend on `BROKEN` and says “Say N, this is BROKEN and crashes driver.” README instructs a hardware tester to remove that dependency manually, noting that no patch does so (`README.md:122-124`). A userspace test forcibly enabling AC code does not change that shipping status.

`CONFIG_B43_DFS` is independently experimental. Its help says every threshold-crossing pulse is reported as radar without certified pattern matching, and “Say N” (`b43/Kconfig:160-170`). Do not use the all-channel replay score as certification evidence.

### 3.3 Source and generated patches agree in the checked direction

I assembled a scratch kernel-path tree from `b43/`, `bcma/drivers/` and `bcma/include/`, then ran `git apply --reverse --check` on all three generated patches. **All three returned 0.** This is useful evidence that their post-image hunks agree with this HEAD's sources.

It is not a forward application/build test against an actual upstream kernel. No vanilla base was fetched here, and the complete kernel integration was blocked by missing headers. The patch series still combines several independently reviewable concerns into very large changes (`docs/driver-status.md:86-103`, `README.md:157-161`).

## 4. Hardware evidence and board portability

### 4.1 Real hardware captures are mostly evidence about the stock driver

The D6220 reference is BCM4352 2x2, `wl` 7.14.89.14 on OEM Linux 3.4 (`router-data/d6220/README.md:5-21`). Its channel sweep is real hardware I/O, not invented data. But it is hardware I/O produced by **`wl`**.

The agcombo is BCM4360 rev 3, D11 rev 42, 3x3 dual-band, `wl` 7.14.43.21. Its raw SROM path returns zero, so its supplied board calibration comes from NVRAM (`router-data/agcombo/README.md:5-27`). Its bus captures are an up/down window, with initial attach before capture, and channel changes through down/up, not a running-interface scan.

MacBookAir6,1 files include first load and association on both bands, scans, traffic and port-loaded register dumps (`router-data/macbookair6-1/README.md:17-27,45-61`). In particular, the documented associations on ch1/20 and ch100/80, interrupts and TX descriptor posts belong to **hybrid `wl`**, not this open driver. `macdump-b43-*` and PMU state under b43 show some physical inspection of a loaded port, not an on-air acceptance test.

There is no packet capture, end-to-end association transcript, successful data transfer result or measured RF result in the inspected material establishing this exact HEAD's on-air MVP. The honest conclusion is **unproven**, not “hardware definitively cannot work.”

### 4.2 Board matrix

| Board | Silicon/topology | What is usefully covered | Why it does not establish broad BCM4360 viability |
|---|---|---|---|
| D6220 | BCM4352, 2x2, FEM 6/sub 0, `wl` 7.14.89 | Main cold/hot PHY reference, raw SROM/NVRAM and table dumps | Different chip/topology from 3x3 BCM4360 and different RF frontend from laptop |
| DSL-3580L | BCM4352, 2x2, 5 GHz only, FEM 6/sub 0, older `wl` 6.30 | Intended physical port target, raw calibration data, version differences | Older vendor branch is explicitly not the oracle; not a BCM4360 laptop |
| agcombo | BCM4360 rev 3, 3x3 dual-band, FEM 6/sub 0, `wl` 7.14.43 | Chip dispatch, third chain, bus interrupts, different vendor build | Cold replay differs materially, SROM harness mode synthetic, no actual b43 packets validated |
| TG789vac v2 | BCM4360, 3x3, FEM 6/sub 0, `wl` 7.14.89 | Strong second-chip cold-sweep trace corroboration | Shared vendor version/frontend family gives useful but correlated evidence; power differences unresolved |
| Archer T5E | BCM4352, 2x2 dual-band, FEM 1, hybrid 6.30 | Dual-band bus/channel-set reference | FEM 1 has no verified loaded table; exploratory band score changed |
| MacBookAir6,1 | BCM4360 rev 3, silicon has 3 cores, **2 wired chains**, FEM 2/sub 1, hybrid 6.30 | Firstload/scan/TX captures, SROM, PMU and MAC dumps; dedicated profile/FEM code | Not covered by the headline router scores; PMU, 6.30/7.14, power and calibration differences remain |

The dedicated MacBook profile is real and present, despite stale nearby prose suggesting otherwise: `test/board_profile.h:405-462` has `chip_id=0x4360`, `chip_rev=3`, PCI `0x43a0`, `num_cores=3`, `coremask=rxchain=3`, SROM-derived PA fields and boardflags3=1. Core 2's unprogrammed fields are retained, rather than treated as a third wired antenna.

`b43/phy_ac.c:2960-3042` now has both router FEM 6/sub 0 and MacBook FEM 2/sub 1 tables, including the MacBook-specific setup and Bluetooth coexistence condition (`3052-3092`). This is meaningful progress beyond “the MacBook is completely unsupported.” The comment at `test/board_profile.h:412` saying its FEM table still stops with a warning is stale relative to the actual lookup.

### 4.3 Portability and safety caveats

- For an unknown FEM, `b43_phy_ac_set_regtbl_on_femctrl` warns that another table could damage the front end and returns without loading one (`b43/phy_ac.c:3060-3067`). This is **a return from a void helper**, not a propagated refusal of the entire bring-up. The enclosing caller continues. The documentation's “stops with a warning” should not be read as a full fail-closed RF safety gate.
- The table writer is verified only for PHY rev 1 and silently returns locally for another revision (`3070-3072`). All reference boards are a narrow silicon family. Audit complete refusal behavior before claiming unsupported revisions are safely excluded.
- PMU code applies the router-observed `max_res_mask=0x7ff` to 4352/4360 (`bcma/drivers/bcma/driver_chipcommon_pmu.c:217-229`). The MacBook stock driver instead writes `0x1ff` during attach and leaves `0x1fb` up (`docs/retrace-todo.md:750-755`, MacBook README:84-86). The cause, silicon revision versus vendor behavior, is not resolved.
- D6220 and DSL are closely related board revisions, not independent arbitrary frontends (`router-data/d6220/README.md:10-11,30-35`). Multiple boards strengthen generalization, but do not span all FEM designs, chain masks, calibrated power fields or thermal conditions.

## 5. Bandwidth, rates and data-path readiness

### 5.1 5 GHz versus 2.4 GHz

5 GHz programming spans 20, 40 and 80 MHz. The reproduced cold sweeps contain 25/12/6 configurations, not every possible primary-channel permutation or every operational scenario. Six weather-radar segments end before CAC finishes; README explicitly calls these partial attaches (`README.md:83-84`). A high percentage on them is not proof of post-CAC beacon operation.

2.4 GHz is **not production-enabled**: default `ALLOW_24` is false and `switch_channel` returns `-EOPNOTSUPP`. Unit Makefile always passes `-DALLOW_24=true` (`test/unit/Makefile:26-33`). Its band gate is an exploratory delta comparison, not a normal-kernel feature test.

Useful 2.4 GHz pieces exist: 14 channel-table rows, Farrow resampling, TX-gain table, noise shaping, some SROM-derived PA/RX-gain setup. Open items include TX target/rate rules, board-specific coefficients, FEM variants, 40 MHz configuration, and calibration coverage (`docs/retrace-todo.md:677-734`). Only a hot ch6 MacBook calibration is captured for 2.4 GHz. No 2.4 GHz 40 MHz capture establishes correctness.

### 5.2 HT/n and VHT/ac are not implemented end-to-end

`b43/main.c:6143-6175` advertises HT receive MCS masks and VHT receive MCS 0-9 maps based on SROM RX chain count. VHT TX map is all unsupported (`0xffff`), and HT TX parameters remain unset. This was used in part to let the stack configure bonded widths.

The operational gaps are larger than that conservative TX map:

- `b43_op_tx` drops frames whose requested first/second rate is HT/VHT MCS (`b43/main.c:4176-4203`).
- AC uses the older `format_598` TX header layout in `b43/xmit.c` (e.g. `342-344,550-552`), without a mapped HT/VHT header.
- RX reuses `format_598` and legacy PLCP interpretation (`b43/xmit.c:660-664` and later RX path). The project explicitly acknowledges that an HT/VHT frame can be dropped or reported at an incorrect legacy rate (`docs/retrace-todo.md:320-341`).
- No usable AMPDU/AMSDU, beamforming, LDPC, link adaptation or long-MPDU implementation is established.

**Risk:** advertising receive MCS support that the RX parser cannot reliably recognize can induce peer behavior the driver cannot handle. “We prevent MCS transmission” is not a sufficient receiver-capability safeguard. Capability advertisements should follow tested RX behavior, or the experimental nature must be kept tightly contained.

Even legacy TX/RX is **source-present, not hardware-proven**. The current MVP deliberately leaves data TX/RX after full hardware-block configuration and beacons (`README.md:31-37`).

### 5.3 Crypto, TX status, power save and interrupts

AC hardware crypto is disabled because cipher numbering and key/header fields do not match the old firmware layout (`b43/main.c:3031`, `docs/retrace-todo.md:269-276`). Software crypto is a reasonable conservative direction, but does not prove the remaining RX/TX header interpretation.

AC TX status reading handles two packages, decodes the first and drops the second (`b43/main.c:1570-1602`). Per-rate retry accounting still uses legacy assumptions rather than the four decoded attempt counts (`docs/retrace-todo.md:364-385`). The captured 472 stock statuses support field research, not successful submission/completion of b43 DMA packets.

Probe-response offload is deliberately disabled. PMQ is deliberately disabled, with mac80211 buffering intended instead (`docs/retrace-todo.md:288-318`). These are explicit scope choices, not hidden claims of vendor completeness.

Interrupt masks and DMA geometry have been made more AC-specific, but reserved/power-up bits lack handlers and PHY TX errors are acknowledged without full processing (`docs/retrace-todo.md:177-215`). Replay of interrupt register traffic is only a partial validation of this boundary.

## 6. Calibration: actual algorithms, fits and snapshots

It would be misleading to dismiss this driver as a single hardcoded register dump. It has real measurement/compute/save/restore machinery. It would be equally misleading to say calibration has been generally solved.

### 6.1 Measurement-driven pieces

- **Radio RC calibration:** programs engine passes, kicks and bounded polls (`b43/radio_2069.c:1289-1308`), derives LPF cap from measured E/F as `((F-E)*193)>>8`, applies measured RC code, and derives DAC-buffer cap from a measured bitfield (`1388-1416`). This is not simply copying the reference board's cap.
- **AFE calibration:** saves chain gains, arms actual hardware calibration bits, reads radio STAT, restores control and gains (`b43/radio_2069.c:1443-1514`). Readback-derived CTRL prevents overwriting a width field with a fixed constant.
- **TX power:** `ppr_ac.c` loads SROM per-chain/per-band PA and per-rate data. `b43_phy_ac_est_pwr_lut` computes detector tables from PA coefficients (`phy_ac.c:1916` onward), and idle-TSSI measurement/configuration is present (`1246-1304` onward). The project distinguishes measured analog quantities from static radio tables.
- **RX IQ:** hardware accumulator collection and loopback gain search feed the integer solver (`phy_ac.c:8764-8830`). It averages per-tone coefficients rather than averaging accumulated powers, with explicit mantissa and rounding rules. Both band/width and core count affect measurement flows.
- **80 MHz frequency-dependent correction:** measured slope selects one of five observed FIR banks (`phy_ac.c:8833-8923`). This is measurement-dependent, although the bin boundaries are fitted.
- **Tempsense:** samples per chain and saves/restores hardware state (`docs/tempsense-wiring-evidence.md:6-14`). Raw collection exists, even though conversion/control policy does not.

### 6.2 Where generalization remains unproven

| Area | Status and consequence |
|---|---|
| RX IQ exactness | 296/309 exact `a`, 259/309 exact `b` in documented corpus; `b` commonly one LSB off (`phy_ac.c:8751-8762`, `docs/retrace-todo.md:587-596`). Unknown input remains. These residuals are algorithm debt, not evidence of RF image rejection performance. |
| Loopback gain search | Halving criterion reproduces 128/148 searches; chain 1 high-band cases hit index 0 still outside target window (`docs/retrace-todo.md:598-603`). The floor behavior and low-power give-up regime need real edge-case evidence. |
| 80 MHz FIR | Five tap banks and thresholds are observed/fitted; code explicitly says gap-midpoint thresholds are **not the stock estimator's actual rule** (`phy_ac.c:8845-8867`). A nearby unseen measurement can choose the wrong bank. Some debt prose calling selection merely chain-tabulated is older than this implementation. |
| LO LUT bases / coefficient blocks | Several sub-band LUT bases and table-7 values remain transcribed, with explicit “coefficients not computed at runtime yet” in one apply phase (`phy_ac.c:6756-6777`, `docs/retrace-todo.md:605-614`). Do not confuse saved measured `afe_res_cal` snapshots (`phy_ac.c:9662-9673`) with hardcoded snapshots: the former are legitimate runtime state. |
| TX power policy | Measured locale ceilings and Local Max tables exist (`phy_ac.c:824-885,1637` onward). Chain-class assignment is best fit among alternatives, not known meaning. Second 40/80 MHz pass and TG789vac legacy rates do not fully match (`docs/retrace-todo.md:415-577`). cfg80211 ceiling is applied, but trace fit does not prove conducted power, EIRP, EVM, PA safety or compliance. |
| Sub-band rate fields | `sb*`, `dot11agdup*`, `mcslr*` are extracted but not applied. Most vectors are zero; TG789vac is a nonzero counterexample (`docs/retrace-todo.md:579-585`). A high weighted score can hide power-policy defects affecting few writes. |
| Temperature | No conversion/consumption yet. The documented `T ~= 0.0485*diff + 100` is a tentative fit with too few points, not a portable conversion algorithm (`docs/tempsense-wiring-evidence.md:31-60`). No validated thermal backoff/chain throttling follows from the sampling trace. |
| CRS trigger | Arithmetic is substantially reconstructed, but five unexpected updates and hot-ring reset behavior remain (`docs/retrace-todo.md:656-675`). |
| Discarded reads | The project has perturbation tools and names uncertain read/constant sites (`docs/retrace-todo.md:616-632`). Per-address perturbation can still miss a discarded read at one site when the same address is consumed elsewhere (`test/unit/read_perturb.py:13-17`). |

### 6.3 Failure paths need more than a trace oracle

There are concrete reasons to prioritize fail-safe behavior:

- RC calibration returns a completion boolean, but the final DAC-buffer pass calls `b43_r2069_rccal_run` without testing its return and reads/applies a result anyway (`radio_2069.c:1412-1416`).
- AFE code's comment describes polling done/valid, but the implementation reads STAT twice, logs it, and restores CTRL without an actual completion/valid decision or error propagation (`1495-1506`).
- Unknown FEM loads no table but does not abort the enclosing initialization.

These are **source-confirmed paths**, not reproduced analog failures. A vendor read oracle supplies successful/reference states and cannot establish behavior of a stuck calibration engine, bad PLL lock, invalid accumulators, power-loss reset or different frontend. Validate and propagate failure before allowing unqualified RF bring-up.

### 6.4 Cold/hot/scan state is a live correctness concern

The unit harness manually seeds `do_full_init` from `AC_FIRST_INIT` (`test/unit/main.c:375-382,2279-2290`). In the real b43 path, `b43_phy_exit` sets it true on down (`b43/phy_common.c:125-132`), and op_init uses it to decide table initialization/first-bring-up (`phy_ac.c:6089-6114`). The project explicitly admits this is not a cold/hot discriminator (`docs/retrace-todo.md:400-404`). Thus a successful manually selected hot unit flow is not proof of the live down/up lifecycle.

The channel-switch tail also contains work observed only on first up/association in laptop scan traces; the project acknowledges that its current cycle can rewrite/zero MAC cells on each scan hop (`docs/retrace-todo.md:101-122`). Router captures mostly down/up rather than scan. This is a major laptop portability boundary and should be validated through real mac80211 callbacks, not just another single-channel trace.

## 7. Trace-comparison scores: strengths and limitations

### 7.1 What `grezzo` really measures

The metric counts equal operations in monotone aligned blocks. The reported parameters are `--min-block 8 --gap-tol 2`. The denominator is `len(V) + len(T) - equal`, a union-like stream count; a wrong-value pair can contribute two unmatched operations. Minimum block/gap tolerance change whether matching runs are considered reliable alignment evidence (`test/unit/cmp_skip.py:387-494,589-600`). They are alignment parameters, not statistical confidence intervals or RF tolerances.

Good design choices include reporting both missing and extra operations, separating raw/perimeter/known-exception views, requiring metric parameters, documenting nondeterminism, keeping cold/hot separate, and warning about incomplete capture classes. The exact periodic positional comparison is particularly useful regression evidence.

But **“raw” is already normalized and filtered**:

- `load_vendor` resolves wide reads, expands some bulks and removes duplicate/shadow/foreign operations (`test/unit/compare.py:282` onward, `937-950`).
- `canon` turns `UNDEFINED` and declared random-value cells into wildcards (`cmp_skip.py:532-535`).
- `drop_solo_vendor` and `drop_solo_port` run **before** raw scoring (`547-557`). These include omitted probe-response/SSID operations, self-test-specific words, LED structure differences, and classes the capture lacks (`compare.py:500-613`).
- The reproduction explicitly printed **313 vendor operations removed and 124 port operations removed** before ch36/20 `grezzo`.

Some removals are principled vocabulary reconciliation, such as an accessor marker followed by its actual bus writes. Others are intentional functionality exclusions. Consequently, “100% raw” does **not** mean every original bus transaction or every vendor feature is reproduced. Quote both the parameters and exclusions. The 99.89% is a strong result on this selected comparison surface, not a physical viability percentage.

### 7.2 Replayed reads/events reduce independence

The oracle queues reads per address from the same vendor capture used as expected output (`test/unit/README.md:172-182`, `wrap.c:485-518`). It lets real driver algorithms run on measured inputs, which is valuable. It also provides the successful hardware responses those algorithms are supposed to cause. Ordering/timing/race problems can remain invisible when a read receives the recorded vendor value even after a wrong earlier action.

Events, watchdog phase, beacon reloads, CAC completion and some environment fields are extracted from the expected trace and fed back into the test (`gates.sh:225-271`). This is a controlled replay regression, not independent discovery that real b43 schedules those events.

`UNIT_TEST` emits mirrored core operations at stock points rather than the true core's ordering (`test/unit/README.md:144-170`, `docs/retrace-todo.md:7-12`). Treat the impressive PHY score as conditioned on that scaffold. The harness does not simulate hardware timing, MAC races or scheduling (`unit README:182-183`).

Queue exhaustion must be zero, but `gates.sh:269-272` redirects harness stderr to `/dev/null`; the sweep logs therefore do **not** independently establish per-segment oracle health. In a separately retained, exact cold01 instrumented run I observed **7648 hits, 400 address misses, zero exhausted queues, 337 known addresses and 6 partially consumed addresses**. The missing-address count is not itself a failure because table/mirror/core reads can legitimately be absent, but it should be visible and classified.

### 7.3 Reproduced comparator weaknesses

**Selector alias:** `reverse-tools/tracelib.py:62-72` removes `sel=`. `OBJ.WR addr=0x000c val=0x001f sel=0x10000` and the same address/value with `sel=0x20000` normalize to the same string. The repository itself notes a historical bug where CWmin/CWmax writes to the wrong memory space still counted as matches (`docs/retrace-todo.md:386-393`). I independently reproduced the alias. Wrong address-space routing is a correctness error, not a formatting nuisance.

**Bus “raw” applies value tolerance:** README says the positional ±1 RX-IQ tolerance does not affect cmp_skip raw (`unit README:135-136`). That is true of its non-bus string alignment, but **not** generally true under `--bus`. `cmp_skip.py:402-410,435-437` calls `compare.py:881-903`'s `ops_equal`, which includes `val_entro_tolleranza`. My 17-operation fixture with one `0x06a1` write changed by one LSB scored **16/18 non-bus** but **17/17 bus**, with no bus divergence. Thus integration raw percentages can inherit the positional tolerance. Document or separate the policies explicitly.

**No binary raw-score gate:** `cmp_skip.py` prints a score and has no mismatch exit criterion. `gates.sh` status is driven by the positional comparator, which has its own perimeter/tolerance rules (`gates.sh:315-331`). High raw percentages and a zero shell exit are not interchangeable assertions. The reproduced multi-segment sweeps/hot/agcombo runs exited 1, despite impressive percentages. Do not describe those whole runs as PASS.

Finally, repeated initialization/table operations dominate the denominator. A rare but critical DMA/header/power/CAC action can be wrong while the weighted metric remains near 100%. Per-phase and safety-invariant assertions should accompany aggregate scores.

## 8. Latest commit: what “real D11 core” means, and actual defects

HEAD adds 17 files/1,274 lines, almost entirely the new D11 test and microcode-extraction tooling. It does **not** replace the port's PHY algorithms or integration bus shim. The preceding commit `19fe0a5` changed comparison; README scores are dated before this newest D11 work.

### 8.1 The implementation is a state model, not real MAC execution

`test/d11sim/d11_core.h:9-12` explicitly says it does not model PHY/radio or execute microcode. `psm42.c:10-25` loads big-endian words; `33-57` reports top-byte frequencies “opaque, not an opcode decode.” `core_ucode_boot` merely sets the MAC_SUSPENDED IRQ bit once when PSM_RUN and any ucode words are present (`d11_core.c:120-133`). It does not execute the uploaded instructions, model command dispatch, DMA, packets, timing or later reset/suspend cycles.

There is a legitimate external interpreter path: README says `aleferri/b43-tools/interpreter/ucode_init.py` executes a real extracted blob and gets board-specific revision stamps (`test/d11sim/README.md:15-24,28-36`). That claim was **not independently validated here**: the external tools and proprietary source blobs were not available/pinned in the audit tree. The same README limits confidence past the `0xF76` version-stamp entry point and says command dispatch through unmodeled IHR reads does not run (`110-146`). The external co-simulator described there is not the C model compiled here.

Even the scripted combined equivalence is separate replay of host writes followed by overlay of a prologue's output, not firmware executing against that driver's changing host state (`run_init_equiv.sh:54-74`). Its snapshots span the whole captured window, including down; init-only narrowing remains open (`D11 README:147-149`).

### 8.2 Reproduced and source-confirmed defects and blind spots

| Finding | Evidence and consequence |
|---|---|
| **Template RAM not modeled, false identical verdict** | RAM_CONTROL/RAM_DATA are 0x130/0x134 (`b43/b43.h:46-47`). C core treats them as ordinary register bytes; no template array exists (`d11_core.h:63-79`, `d11_core.c:85-96`, `snapshot.c:3-37`). Two fixtures wrote different first template words and the same final word. Their dumps were identical and comparator returned 0. A crucial beacon payload difference disappears. |
| **PHY/radio differences outside verdict** | `fakephy` is not in the snapshot surface. Different TX-power PHY writes generated empty, identical core dumps and returned 0. This is intentional scope, but prevents any RF viability inference from a D11 IDENTICAL result. |
| **Empty-input success** | Empty op streams produced empty state files, and `compare_state.py` returned IDENTICAL/0. There is no minimum coverage/success prerequisite. A zero-cell “equivalence” is not validation. |
| **Parse errors nonfatal** | An OBJ write lacking `sel` incremented parse_err, produced no state and replay returned 0 (`ops.c:75-82`, `d11sim.c:103-120`). This matters for old wl-diag captures missing selectors. A pipeline can silently compare impoverished states. |
| **Unknown selector/out-of-range operations not fail-closed** | An OBJ write with selector 5 generated no state and returned 0. `core_obj_write` silently returns for unsupported selectors; replay still increments `applied` (`d11_core.c:25-60`, `ops.c:79-82`). Counters are not proof of modeled effects. |
| **Folded bulk writes skipped with success** | `OBJ.BULKW` fixture produced no state and returned 0, with only a warning (`ops.c:85-87`, `d11sim.c:115-120`). Wrapper correctly requests `--no-bulk` for the wl side, but a separately supplied b43 trace can still lose data. |
| **Width inferred from spelling** | `ops.c:17-29,67-71` treats more than four hex digits as 32-bit. After writing 0x12340000 to MACCONTROL, `val=0x00000002` yielded 0x00000002, while numerically equivalent `val=0x2` yielded 0x12340002. The latter takes the 16-bit path and does not update the dedicated MACCONTROL latch. Input schema needs an explicit width, not formatting-derived semantics. |
| **Raw OBJADDR/OBJDATA register access not implemented** | Fixture writes to 0x160/0x164 left only REG cells, no SHM state. `objaddr` exists in the struct but core register access does not implement its indirect-memory/autoincrement semantics. The decoded OBJ vocabulary is handled upstream by mmio2ops; the C core itself is not a complete raw-bus model. |
| **IRQ W1C semantics not implemented** | IRQ register writes are plain assignments. Synthetic write 3 followed by ACK 1 leaves 1, not W1C remainder 2. Comparator excludes this cell, masking the discrepancy. Other non-latch/status/FIFO registers also need classification rather than a generic RAM register file. |
| **Microcode overlays reversed in wrapper** | `run_init_equiv.sh:60` associates wl dump with `--ucode-a`, `68` associates b43 dump with `--ucode-b`, but `73-74` compares A=b43 and B=wl. These two flags are swapped. Fix to b43 on A and wl on B. This can corrupt informational provenance and, with nonidentical write sets, the derived comparison surface. |
| **One side's ucode provenance can hide other side's host difference** | `compare_state.py:69-80` unions overlay keys and excludes those cells on both sides, also overwriting original host final state. My SHM mismatch returned DIFFERENT/1 without an overlay but IDENTICAL/0 when only A supplied an overlay at that cell. Per-side ownership and chronological last-writer reasoning are required. |

Synthetic results are retained in `audit-fixtures.py`, `synthetic-fixtures.log`, `synthetic-results.json` and `synthetic/`. These fixtures test the actual compiled code and comparator, not a copied implementation. They are **synthetic falsification witnesses**, not on-air tests.

Sparse snapshots also discard the distinction between never touched and explicitly zeroed cells (`snapshot.c`). Final-state comparison legitimately ignores some write history, but reset assumptions, memory clear coverage and required side effects must then be asserted separately. Ordering and intermediate safety invariants cannot be recovered from the final sparse dump.

### 8.3 Real vendor trace replay result

I decoded the checked-in agcombo `ch36.bin` with `--no-bulk` and replayed it in the C model:

- 122,584 decoded lines
- 49,822 “applied”, 72,762 ignored, zero parser errors
- REG 5,323 writes / 52,103 reads
- OBJ 14,520 writes / 2,643 reads
- PHY 28,860 writes / 16,603 reads, 5,616 mirror/readback divergences
- 11,958 ucode words stored; model says `psm booted=yes`
- zero folded-bulk records skipped

This is a useful parser/model smoke test against a real vendor capture. The `psm booted` label means the C handshake fired, **not that those 11,958 words executed**. Mirror/readback divergences are expected evidence of the fake PHY's incompleteness, not measured hardware errors of b43. No b43-versus-wl core-state equivalence was produced here because the b43 integration stream and external interpreter prerequisites were unavailable.

## 9. Integration harness: real code above simulated boundaries

The integration suite really intends to compile main.c, phy_common.c, DMA, TX/RX, LEDs, rfkill and bcma/core against installed kernel headers, with the port copied over vanilla source (`test/integration/README.md:3-7,117-128`; Makefile:69-84). This is more representative than unit core mirrors.

Its simulation boundaries are still decisive:

- `kernel_shim.c:296-370` serves a minimally valid firmware header with **64 zero payload bytes** and **zero initval entries**. The actual firmware revision comes from oracle SHM reads. Consequently, this test does not establish firmware upload execution or the complete real initvals path.
- `bcma_stub.c:437-463` synthesizes MAC_SUSPENDED from MACCONTROL; the comment explicitly explains that its dummy firmware would never start a real PSM.
- Work executes immediately inline, not asynchronously (`subsystem_stub.c:553-575`), and timing follows replayed jiffies/events.
- Regulation is represented by a stub table fitted to the vendor locale, rather than the entire actual cfg80211 policy/environment (`subsystem_stub.c:178-235`).
- DMA RX slots are stepped to recorded indices, but **every poisoned frame is dropped/recycled** (`integration README:63-69`). The 283 received frames in the agcombo score are stock-capture environmental events, not 283 correctly decoded/received b43 packets.
- Interrupts that occurred during vendor bring-up are delivered together later because harness bring-up is one call. This cannot exercise the same races.

README reports `probe=0,start=0` and 82.61% on cold01, and 67.53% at the agcombo bus with 561 interrupts/283 capture frames. Those are plausible internal replay measurements; they are not acceptance evidence for kernel probe on hardware, real RX, real TX, beaconing or association. They were **not reproduced** here because the installed-header prerequisite failed before compilation.

The README itself responsibly explains that changing the measurement window previously moved the cold integration score from 90.90% to 82.61%, and that interrupt replay lowered the agcombo score by exposing additional b43 DMA operations (`README.md:63-82`). This is a good example of why a score increase is not automatically a driver improvement, and a score decrease is not automatically a regression.

## 10. Reproduced results at this exact HEAD

All percentages below use **`--min-block 8 --gap-tol 2`** unless stated otherwise. “Exit 1” means the overall positional gate found a divergence, not that compilation failed or the percentage is unmeasurable.

| Experiment | Observed result | Status / comparison with README |
|---|---|---|
| Unit userspace build | exit 0 | Reproduced |
| D11 userspace build | exit 0 | Reproduced |
| SROM userspace build | exit 0 | Reproduced |
| D6220 cold01 ch36/20 | **29817/29849 = 99.89%**, 2 wrong values, 27 missing, 1 extra, four blocks; gate exit 0 | Exact headline result reproduced. Positional gate tolerance/perimeter is not the same assertion as raw equality. |
| D6220 all 43 cold segments | **min 99.77%, median 99.91%, max 99.95%**; 14 printed positional divergence sites; whole gate exit 1 | Documented range reproduced with current parameters; no early-flow warnings |
| TG789vac all 43 cold segments | **min 99.77%, median 99.91%, max 99.98%**; 36 printed positional divergence sites; whole gate exit 1 | Documented range reproduced; no early-flow warnings |
| D6220 hot ch36/ch52/ch104 | **17798/18079=98.45%, 27346/27623=99.00%, 27390/27685=98.93%**; exit 1 | Headline hot values reproduced |
| agcombo cold01 ch36/20 | **31132/34155=91.15%**, 831 wrong-value pairs, 138 missing, 1063 extra; exit 1 | README says 91.05% and explicitly says this row was not remeasured on its date. Current result is 91.15%, not 91.05%. |
| Periodic ch36/20 positional gate | **MATCH, 496 vendor/test ops**, exit 0 | Reproduced. Two port ops removed; capture lacks TPL/CAL classes. Oracle: 261 hits, zero misses/exhaustions/partial queues. |
| Band delta, default d6220 profile | **58/72 shared deltas**, script exit 0 | Documented default reproduced, exploratory ALLOW_24-only path |
| Band delta, archer profile | **52/72 shared deltas**, script exit 0 | Document says 60/72. Current script/captures/source reproduce 52, not 60. No claim that this is an RF regression; discrepancy remains to explain. |
| SROM DSL raw | **77 PASS / 0 FAIL / 7 INFO** | Reproduced, duplicate harness extractor |
| SROM D6220 raw | **82 PASS / 0 FAIL / 2 INFO** | Reproduced, duplicate harness extractor |
| SROM agcombo synthesized | **83 PASS / 0 FAIL / 1 INFO** | Reproduced round-trip, not independent raw-layout proof |
| SROM bcm4360usb synthesized | **32 PASS / 0 FAIL / 52 INFO** | Reproduced, missing keys limit coverage |
| UBSan unit cold01 | Build/run exit 0; no runtime-error diagnostics; final trace byte-identical to normal cold01 output | Narrow host-execution check only; exact env and oracle consumption retained |
| Three generated patches, reverse check | exit 0 each | Post-image agreement, not actual forward upstream integration build |
| Integration check | **exit 2**, `/usr/src` absent | Blocked before compile; 82.61%/67.53% remain reported, not reproduced |
| D11 vendor bus replay | 122584 lines, 49822 applied, 72762 ignored, zero parse errors | Smoke test, no real microcode execution in C |
| D11/trace comparator audit fixtures | Multiple reproduced IDENTICAL false positives; selector alias and bus tolerance discrepancy | Concrete contribution candidates, detailed in sections 7 and 8 |

The band-delta script exits 0 even at 52/72 because it is a report, not a 72/72 assertion. The raw comparator similarly emits useful scores without imposing a pass threshold. Preserve actual logs and exit statuses in any downstream summary.

## 11. SROM provenance, licensing and upstream readiness

### 11.1 SROM test coverage is valuable but not the actual kernel extractor

Main source implements `bcma_sprom_extract_r11` at `bcma/drivers/bcma/sprom.c:486` and dispatches to it for revision 11 at `843-844`. Correct rev-11 header offsets matter particularly for MacBook chain extraction.

However, `bcma/harness/extract_r11.c:1-36` is a separate copy of an older draft's parser with corrected header offsets. The project explicitly says it is not testing `drivers/bcma/sprom.c` and does not check agreement on every other field (`bcma/README.md:92-103`). The passing harness numbers therefore cannot be promoted to “actual shipped extractor fully tested.”

The agcombo and USB tests synthesize SROM using the same offsets used to parse it. They check packing/round-trip and field completeness, but not independently that those offsets are right on actual silicon (`bcma/harness/README.md`, Synth mode section). Raw DSL/D6220 pairs provide stronger independent evidence, yet many fields are zero/saturated and the dumps are partial. A second physical board with nonzero sub-band rate fields remains a useful missing vector.

Best separable upstream work is still **SROM rev 11 extraction**, after binding tests to the actual kernel function, checking regressions for older revisions, and establishing the consumer path on real hardware. `bcma/README.md:29,92-105` itself says not ready for submission and identifies natural reviewers and a 2015 thread.

### 11.2 Provenance has transparent but unresolved holes

`PROVENANCE.md` records:

- D-Link GPL-release location and distinction between the stated v1.01 source and mirror's v1.00 asset; object revision and SHA256 for the extracted channel table (`3-17`). This is better than an untraceable dump, but acquisition should follow the exact stated object/hash.
- Netgear D6220 firmware/source archive URL (`19-26`).
- AGSOT TX-gain-table corroboration with a **TODO for image origin, mirror and contained driver revision**; the claimed 128/128 check cannot be reacquired from this tree alone (`28-40`).
- MacBook capture source and transferred files, with **redistribution permission pending** because the origin repository lacks a license (`42-51`).
- Broadcom proprietary-notice `d11.h` used to understand TX status names, with a claim that no text/code was copied (`53-62`). Public availability alone is not a license grant. This is a provenance/review concern, not evidence that infringing copying actually occurred.

The stated RE policy permits observing hardware accessors and blob data tables but not internal logic hooks (`docs/driver-status.md:77-84`). This is an explicit process boundary. It does not itself prove clean-room derivation of every line; do not infer either clean-room certification or misconduct from that policy alone.

### 11.3 License interpretation needs file-level care

Root `LICENSE` is **GPL version 3**. Kernel-derived files such as `main.c` and `phy_ac.c` are marked `GPL-2.0-or-later`; some new/support files such as `ppr_ac.c` and unit Makefile are marked `GPL-2.0` (not “or later”). The new D11 C files/Makefile lack individual SPDX headers in this revision.

This is not a basis for declaring the whole repository uniformly GPLv3 or automatically suitable for Linux submission. Preserve the applicable file licenses, clarify the root license's intended coverage, add explicit new-file licensing, and review redistribution of traces, proprietary extracted tables/blob material, and external tools. GPL-2.0-only pieces and GPLv3 are not interchangeable licensing choices. The audit does not provide a legal conclusion about derivative-work status of hardware tables or instruction blobs.

`test/d11sim/README.md:54-57` explicitly keeps extracted proprietary ucode out of the tree. Its external interpreter dependency is not pinned, further limiting reproducibility of the newest “real execution” claims.

### 11.4 Bounded upstream review investigation

I used the existing websearch tool for current author/SROM11 review and historical BCM4360/rev11 discussion. Results returned old GitHub draft paths and general driver resources, not an authoritative review thread or merge decision for this exact series. No current mailing-list acceptance/rejection was independently verified. The report therefore relies on the source's explicit not-yet-for-submission status and does **not** claim that no submission ever occurred.

## 12. Recommended contribution plan

### Priority 0: repair the evidence model before increasing its score

A small, read-only-friendly first contribution would be a **D11/comparator regression suite plus fail-closed input handling**, not another bundle of constants tuned to the reference trace.

Concrete acceptance tests:

1. Fix `run_init_equiv.sh` overlays so A=b43 receives b43 ucode and B=wl receives wl ucode. Test asymmetric overlay keys/values.
2. Empty input, missing fields, invalid selectors, unsupported required classes, folded data-less writes and out-of-range addresses must fail or produce an explicitly incomplete verdict, never authoritative IDENTICAL/0.
3. Preserve region/selector, explicit access width, endian conventions and source identity. Test numerically equivalent padded/unpadded fields.
4. Model template RAM and demonstrate that different beacon words produce DIFFERENT even when the last RAM_DATA value matches.
5. Distinguish modeled latches, W1C IRQs, FIFOs, reset-only state and volatile cells. Either implement indirect OBJ register semantics or state clearly that input must already be decoded and reject raw indirect accesses.
6. Track per-side ownership and last-writer provenance. Do not blanket-drop the union of all ucode-written cells or overwrite a later host final value with an independently executed earlier prologue.
7. Separate strict raw comparison from positional ±1 tolerance in bus mode. Keep selectors in canonical identity. Add the reproduced alias and 17-op tolerance fixtures.
8. Require capture coverage manifest, relevant phase bounds, tool revision, blob hash and a nonzero measured comparison surface. Publish ignored/unmodeled counts alongside any equivalence result.

These are concrete defects with host-side witnesses, so they can be fixed and reviewed without touching anyone's radio. They make future viability claims more trustworthy than simply boosting an aggregate percentage.

### Priority 1: get separable SROM work genuinely testable/upstream-reviewable

Compile/test the actual `bcma_sprom_extract_r11` rather than a driftable copy. Add raw MacBook vector coverage without publishing unnecessary device identity, nonzero sub-band fields, inactive-core sentinels, older-revision regression vectors, and synthetic boundary values clearly labeled as synthetic. Keep PCI ID, PMU policy and generic NVRAM fields separate where review permits. Resolve redistribution/provenance and root/file-license ambiguity before sending.

### Priority 2: fail-safe lifecycle and honest capabilities

- Reject unsupported frontend/silicon combinations through an actual propagated error, not just a helper return.
- Make RC/AFE/PLL/IQ failure paths bounded, validated, logged and propagated without enabling RF from stale results.
- Separate core-reset generation, first PHY bring-up, later down/up and scan retune. Validate real mac80211 callback sequences and preserve keys/MAC state on scan hops.
- Resolve MacBook PMU mask behavior using chip-revision and vendor-version evidence, not router score inheritance.
- Do not advertise HT/VHT receive modes beyond verified RX header/PLCP handling. Map TX/RX DMA headers before claiming n/ac readiness.

### Priority 3: a future hardware acceptance campaign, not performed here

After those safeguards, a qualified maintainer can test one explicitly identified board and non-DFS 5 GHz channel first, with recoverable console and conservative power. Required artifacts should include exact kernel/patch/firmware/SROM identities, probe/start logs, external monitor capture of a real b43 beacon, receiver behavior, measured or constrained RF power, then legacy TX/RX/association under controlled conditions. Repeat cold/hot/rfkill/scan transitions before widths, DFS or high-throughput features.

For MacBookAir6,1, start from its own rev-11 SROM/FEM2-sub1/2-chain profile. Do not use the 3x3 router's advertised streams or its high score as qualification. Add 2.4 GHz and HT/VHT only after their calibration/header gaps have independent acceptance evidence. This is a proposed follow-up campaign, not authorization to change hardware during this read-only audit.

## 13. Reproduction commands and retained artifacts

The commands below describe the successful audited workflow. All variables refer to the new evidence copy. They must not be repointed at a live kernel/module tree. `fetch`, `git am`, `modprobe`, `ip link` and hardware capture scripts were **not** executed.

```sh
REPO=/path/to/research-workspace/repos/aleferri--b43-ac-wip
AUD=/path/to/research-workspace/evidence/aleferri-host-audit

# Original read-only identity/status checks
cd "$REPO"
git rev-parse HEAD
git status --short
git log -5 --oneline
git show --stat HEAD

# Pinned audit copy. Initial directory was newly created for this audit.
mkdir -p "$AUD"
git archive HEAD | tar -x -C "$AUD"
make -C "$AUD/test/unit" -j4 > "$AUD/unit-build.log" 2>&1
make -C "$AUD/test/d11sim" -j4 > "$AUD/d11-build.log" 2>&1
make -C "$AUD/bcma/harness" -j4 > "$AUD/srom-build.log" 2>&1

cd "$AUD"
export TMPDIR="$AUD"
unzip -q router-data/d6220/cold-sweep.zip -d cold-d6220
unzip -q router-data/d6220/hot-sweep.zip -d hot-d6220
unzip -q router-data/tg789vac-v2/cold-sweep.zip -d cold-tg789
unzip -q router-data/agcombo/cold-sweep.zip -d cold-agcombo

COLD="$AUD/cold-d6220" GATE_TMP="$AUD/gate-cold01" \
  sh test/unit/gates.sh --min-block 8 --gap-tol 2 > gate-cold01.log 2>&1
COLD="$AUD/cold-d6220" sh test/unit/gates.sh --min-block 8 --gap-tol 2 \
  cold-d6220/cold[0-9][0-9]-ch*.txt > sweep-d6220.log 2>&1
COLD="$AUD/cold-tg789" sh test/unit/gates.sh --board tg789 \
  --min-block 8 --gap-tol 2 cold-tg789/cold[0-9][0-9]-ch*.txt > sweep-tg789.log 2>&1
HOT="$AUD/hot-d6220/segmenti" sh test/unit/gates.sh --hot \
  --min-block 8 --gap-tol 2 > hot-three.log 2>&1
COLD="$AUD/cold-agcombo" sh test/unit/gates.sh --board agcombo \
  --min-block 8 --gap-tol 2 > agcombo-cold01.log 2>&1

AC_READ_ORACLE="$AUD/router-data/d6220/wl-diag-wl1-steady-tick-ch36-bw20.txt" \
  test/unit/ac_trace periodic d6220 > periodic.out 2> periodic.stderr
python3 test/unit/compare.py router-data/d6220/wl-diag-wl1-steady-tick-ch36-bw20.txt \
  periodic.out > periodic-compare.log 2>&1
make -C bcma/harness check check-d6220 check-agcombo check-bcm4360usb \
  > srom-tests.log 2>&1
BAND_TMP="$AUD/band" BOARD=archer sh test/unit/band_gate.sh > band-archer.log 2>&1
BAND_TMP="$AUD/band" BOARD=d6220 sh test/unit/band_gate.sh > band-d6220.log 2>&1

# Attempted prerequisite check only, intentionally blocked rather than installing headers.
make -C test/integration check > integration-check.log 2>&1

python3 reverse-tools/mmio2ops.py router-data/agcombo/ch36.bin --no-bulk \
  -o agcombo-ch36.ops > d11-decode.log 2>&1
test/d11sim/d11sim replay --ops agcombo-ch36.ops --label wl \
  --dump agcombo-ch36.state > d11-replay.log 2>&1

# Audit-added scripts reside only in AUD and test the pinned original implementations.
python3 audit-fixtures.py > synthetic-fixtures.log 2>&1
python3 audit-comparator.py > comparator-fixtures.log 2>&1

# Undefined-behavior instrumentation in a separate scratch harness directory.
cp -a test/unit test/unit-ubsan
make -C test/unit-ubsan -B -j4 BIN=ac_trace_ubsan CC='gcc -fsanitize=undefined' \
  > unit-ubsan-build.log 2>&1
AC_CHANNEL=36 AC_BW=20 AC_MAC_WIDTH=1 AC_FIRST_INIT=1 \
AC_READ_ORACLE="$AUD/gate-cold01/merged" AC_READ_ORACLE_FROM=28 \
AC_TIMELINE="$AUD/gate-cold01/timeline" AC_WD_PHASE=0 AC_WD_ENTRY_TURN=1 \
AC_EDCF_RELOADS=0x1 AC_BEACON_RELOADS=2 \
  test/unit-ubsan/ac_trace_ubsan full d6220 \
  > ubsan-cold01-exact.out 2> ubsan-cold01-exact.stderr
diff -q gate-cold01/full ubsan-cold01-exact.out

# Check patches against the copied post-image, without applying them.
mkdir -p patch-check/drivers/net/wireless/broadcom
cp -a b43 patch-check/drivers/net/wireless/broadcom/
cp -a bcma/drivers patch-check/
cp -a bcma/include patch-check/
(cd patch-check
 for p in ../patches/*.patch; do
   echo "=== $p"
   git apply --reverse --check "$p"
   echo "exit=$?"
 done) > patch-reverse-check.log 2>&1

# Original remains pinned and clean.
git -C "$REPO" rev-parse HEAD
git -C "$REPO" status --porcelain
git -C "$REPO" diff --quiet
```

The initial instrumented attempt used `AC_MAC_WIDTH=0` and missed an explicit beacon-reload setting, then was corrected to the exact gate environment. The final `ubsan-cold01-exact.out` is byte-identical to `gate-cold01/full`; retain the final exact run for claims. Earlier scratch runs are not mixed into headline metrics.

Key artifacts: `gate-cold01/merged`, `full`, `timeline`, `cmp`; sweep/hot/agcombo logs; periodic trace and oracle stderr; `srom-tests.log`; both band logs; blocked integration log; patch-reverse log; `agcombo-ch36.ops/state`; D11 replay log; synthetic JSON/state fixtures; strict/bus comparator witnesses; final instrumented trace and oracle stderr.

## 14. Bottom line

The reconstructed source and repeated vendor-trace matches are real technical progress. The project has substantially better evidence and self-identified debt than many “BCM4360 support” forks. Its most useful next step is not another headline percentage, but closing the boundary between replayed success and actual driver behavior: faithful comparison/model semantics, actual extractor tests, fail-safe board/calibration handling, live lifecycle correctness, and finally externally observed RF acceptance.

## 15. Independent real-hardware evidence and exact-HEAD bug status

[Issue #4](https://github.com/aleferri/b43-ac-wip/issues/4), by `iferon44`, created/updated September 30, 2026, open with zero comments at retrieval, describes an ASUS RT-AX92U: BCM4908 ARM64, Linux 6.12.111, 5 GHz BCM4352 rev 3, radio 2069 rev 4, AC-PHY rev 1, NVRAM-derived rev-11 SROM and FEM6. The tester used `8c6149f` and rechecked against `c75e014`. These are third-party reported hardware observations, not this audit's independently reproduced tests. They invalidate a blanket claim of no hardware attempts, but do not establish success on this exact HEAD or a BCM4360 laptop.

**Two reported defects remain source-confirmed at `a68a838`, while one has been fixed:**

- **48-bit TX gain table remains unresolved.** `b43/phy_ac.c:4094-4105` describes table 0x20 as a 128-byte curve, truncates `txgain[k][0]` to `u8`, and calls `b43_actab_write_bulk(..., 8, 128, gaincurve)`. The same file describes 48-bit entries at `2087` onward and three-word readback at `4779-4786`. The tester reports vendor width 48, using an accessor for the first word and two direct PHY-data stores invisible to the accessor hook. They report later ARM64 PCIe external aborts with the narrow write, and clean repeated link-up/down after three 16-bit writes per entry. This audit confirms that the narrow source remains, not the physical causal chain independently. An accessor score can miss an entire physically essential payload.
- **RF sequence completion remains unresolved.** `b43/phy_ac.c:3185-3195` polls only `status & 0x0001`, while `3207-3219` triggers arbitrary `cmd_bit`, including `0x0002` at `2766`. The issue reports status `0x0202` after that trigger, so the helper returns while the engine remains active. Other callers use the same fixed-bit helper at `7039,7825,8002,8379`. Pass the triggered mask to completion checking and propagate timeout instead of assuming bit 0 for every command. The current ordering defect is source-confirmed and consistent with the report.
- **TX power callback suspension is fixed at this HEAD.** Current `b43_phy_ac_op_adjust_txpower()` explicitly brackets its body with `b43_mac_suspend()` and `b43_mac_enable()` (`141-147`). The worker still calls the PHY op without its own suspension (`b43/phy_common.c:490-500`), so the repair is at the appropriate callback boundary. Do not claim all three old issue defects remain. Source repair does not establish hardware retesting.

With local fixes and matching D6220 ucode 928.10005, the tester reports hostapd AP-ENABLED on ch36/20 at legacy rates, but a phone and separate laptop saw no SSID. Assumed SHM counter names indicate beacon attempts and approximately two TX PHY errors per beacon. ASUS ucode 1570.181 additionally produced template underflow. The tester found no missing accessor-level PHY/radio writes, only board-value differences. Counter naming is explicitly inferred, and firmware/board mismatch remains a confounder, so this is not proof of a universal exact root cause. It is strong evidence that software AP readiness and accessor agreement are insufficient RF acceptance.

[Issue #3](https://github.com/aleferri/b43-ac-wip/issues/3), owner-authored September 27, explicitly asks for raw MMIO because accessor hooks hide operations. Both issues were retrieved through the public GitHub API on the audit date, with zero comments at retrieval. Neither is upstream patch review. Prioritize raw-MMIO coverage, faithful wide-table payloads and trigger-specific sequencing before headline match improvements. Keep the already-fixed callback suspension as a regression test, not a new claimed outstanding defect.

The main conclusion stands with an important refinement: **real unsuccessful hardware bring-up has been reported, while successful on-air BCM4360 operation remains unestablished**.
