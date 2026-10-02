# 2026-10-02: research and repository acceptance revalidation

## Purpose and boundaries

Revalidate the completed survey and repository through their real interfaces, rather than treating documentation inspection or a custom probe as sufficient acceptance. These observations were collected from 17:50 UTC onward.

This was **not** an experimental-driver hardware run. No driver was unloaded or loaded, no MMIO/PHY/radio access occurred, and no firmware was installed. The original report remains a historical survey at its frozen revisions, not a claim that the Air now has working open Wi-Fi.

Environment observed: x86_64 Linux, GCC 15.3.0, GNU Make 4.4.1, Python 3.14.7, and Nix 2.34.8. The temporary vendor-table environment used Python 3.14.7 and pyelftools 0.32.

## Observed outcomes

| Requirement | Interface exercised | Observation | Limit |
|---|---|---|---|
| Work in the moved repository | Bare `pwd`, `git status`, and origin lookup, with no `cd` override | Default workspace is the moved research checkout. Clean `main`, tracking `origin/main`, correct research remote | Does not test laptop access |
| Use the whole notebook after moving it | Its actual `make check` and `make test` targets | Repository check passed and all 20 tests passed | Checker is not a comprehensive secret or license audit |
| Retrieve the private repository independently | Authenticated GitHub clone into a new scratch directory, followed by the same Make targets | Clone succeeded at initial commit `48a2e011178eedfb3c6a2a2ecd430f9e66aa67be`. Checks and all 20 tests passed | Private authentication was already configured |
| Read the delivered research | Native linked-file Markdown reader opened `REPORT.md` from the moved checkout | Reader accepted the report and its linked-file source changed from the original scratch report to the repository copy | No independent visual screenshot or human agreement is claimed |
| Verify the private remote | GitHub repository inspection and `git ls-remote` | Visibility is `PRIVATE`, default branch is `main`, local/remote revisions matched | Visibility does not authorize proprietary uploads |
| Exercise original upstream host tests | OpenBRCM's top-level `hosttest` target, including a forced rebuild | Ten C test programs reported PASS. Nineteen SPROM decoder tests and seven vendor-table tests passed | Optional installed-firmware cases still skipped. No physical DMA or RF proof |
| Reproduce the proposed first contribution at the correct boundary | Aleferri's original `run_init_equiv.sh` public wrapper | Zero operations on both sides, zero-byte state dumps, no PSM boot, yet `IDENTICAL` and exit 0 | Synthetic inputs through the original CLI, not a radio test or an implemented fix |
| Exercise a real driver integration boundary | Original `make -C test/integration check` | Exit 2 before compilation because the required `/usr/src` kernel-header layout was absent | No passing driver integration build can be claimed |
| Establish independent Air SSH | Documented key-only SSH command with strict host-key checking | Exit 255: `macbook-air.local` could not resolve. No matching Air Tailscale peer | Ethernet routing, remote sudo, recovery boot, and deployed configuration remain unverified |

## 1. Original OpenBRCM public host interface

**Evidence:** reproduced host test, using the original checkout at `06d60d610f4e1cba1f20a188453c8f3ba69357fb`.

```sh
make -C "$OPENBRCM" hosttest
```

The first run returned 0, but the seven vendor-table tests skipped because their input/dependency was unavailable in that environment. That result was not recorded as seven passing tests.

The existing local vendor object was then checksum-verified against:

```text
352a6e349f74c69b78e76f68c63752c99b8f6b22dc942af531b754211d7f4743
```

Using temporary Nix-provided Python with `pyelftools`, and the upstream-supported `OPENBRCM_RE_BLOB` variable, the **same public aggregate** was rerun with a forced rebuild:

```sh
# Historical local flake input, shown with a portable path placeholder.
PYTHON_WITH_PYELFTOOLS='let flake = builtins.getFlake "/path/to/nixos-config"; pkgs = import flake.inputs.nixpkgs { system = "x86_64-linux"; }; in pkgs.python3.withPackages (ps: [ ps.pyelftools ])'
OPENBRCM_RE_BLOB="$LOCAL_VENDOR_OBJECT" \
  nix shell --impure --expr "$PYTHON_WITH_PYELFTOOLS" \
  --command make -B -C "$OPENBRCM" hosttest
```

Observed result: exit 0, ten C program PASS reports, nineteen Python decoder tests passing, and seven vendor-table tests passing without skips.

The firmware parser/initvals programs still reported three skipped real-file checks over two absent installed initvals files. We did not install firmware merely to make a test green. GCC also emitted `-Wmaybe-uninitialized` warnings about stats in the optional real-file test. Those warnings were not fixed in this scope.

The vendor object stayed outside Git. No firmware extraction, kernel-module linking, hardware loading, or vendor-byte redistribution was performed by this revalidation. Host DMA/IRQ tests remain modeled host evidence, not a physical-device acceptance test.

## 2. Original initialization-equivalence gate, not just a copied comparator

**Evidence:** reproduced host test with independently authored synthetic inputs through the original CLI, at `b43-ac-wip` revision `a68a838d8793086ea980b6b71603a6a95623eebd`. The external `b43-tools` checkout at `2361e9e8aad9f2912877b82be5cc529b3dd390a1` supplied the expected public interpreter path, but no firmware blob was supplied or executed for these cases.

Inputs were kept in external scratch storage:

- Empty capture file: zero bytes.
- Empty b43 op stream: zero bytes.
- One-sided control: `0.000000 #1 cpu0 REG.WR off=0x0100 val=0x00000001`.
- Equal comparator control: `REG 0x0100 0x00000001` on both sides.
- Mismatch control: the same cell with values 1 and 2.

The actual gate invocation was:

```sh
sh "$B43_AC_WIP/test/d11sim/run_init_equiv.sh" \
  --wl-bin "$FIXTURES/empty-capture.bin" \
  --b43-trace "$FIXTURES/empty-b43.ops" \
  --b43-tools "$B43_TOOLS" \
  --work "$SCRATCH/gate-empty"
```

The decoder emitted **0 operations**. Both replay summaries reported **0 applied operations**, **0 ucode words**, and **`psm booted=no`**. Both resulting state dumps were zero bytes. Nevertheless, the public wrapper returned:

```text
VERDICT: host-configuration surface is IDENTICAL between b43 and wl
exit status: 0
```

Controls through the same original interfaces:

| Case | Observed verdict | Exit |
|---|---|---|
| Empty capture / empty driver stream through the gate | IDENTICAL | 0 |
| Empty capture / one modeled register write through the gate | DIFFERENT, one b43-only cell | 1 |
| Meaningful nonempty equal states through `compare_state.py` | IDENTICAL, one equal cell | 0 |
| Meaningful mismatched states through `compare_state.py` | DIFFERENT, one differing cell | 1 |

**Supported conclusion:** the proposed first contribution has a witness at the authoritative initialization-equivalence boundary, not merely a hypothetical consequence of comparing two empty dictionaries. The controls show the tool is not simply always returning success.

Equality of two empty mappings is mathematically legitimate for a generic comparator. The intended improvement is to require sufficient initialization evidence at the gate, preserving legitimate nonempty equality and mismatch behavior. This record does not implement that fix, demonstrate a complete initialization, or establish RF correctness. Refresh upstream before developing the contribution.

## 3. Real integration boundary was attempted and blocked

The original b43 integration target was executed directly:

```sh
make -C "$B43_AC_WIP/test/integration" check
```

Observed behavior: `/usr/src` was absent, the Makefile printed its missing-kernel-headers diagnostic, and Make returned 2 before compiling any driver file. No claim is made that this public integration target passed or that its source is inherently unbuildable.

Even a future passing host integration target will not replace physical RX/TX, association, board provisioning, or lifecycle acceptance.

## 4. Actual Air access remains externally blocked

The desktop's Tailscale backend was running, with zero peers matching the configured Air hostname. LAN name lookup returned 2. The documented SSH path was attempted with batch mode, IPv4, strict host-key checking, and a five-second connection timeout:

```sh
ssh -4 -n -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o ConnectTimeout=5 -o ConnectionAttempts=1 \
  trbiv@macbook-air.local '<read-only inventory commands>'
```

It returned 255 because the hostname could not resolve. No remote command executed. This does not prove the laptop is powered off or disconnected. mDNS may also be unavailable, and no alternate Ethernet address was supplied.

The access plan is therefore **prepared, not operationally validated**. Independent Ethernet routing, SSH authentication, noninteractive sudo, the deployed `wl` baseline, and recovery generation remain unverified. Hardware acceptance must not start until those prerequisites and a test/recovery scope are established.

## 5. Whole-result acceptance and what improved

The notebook was exercised both in its moved workspace and via a fresh private GitHub clone. The tests, document targets, correct remote, clean branch, and native report reader were checked over the complete result, not just an early scaffold.

The research is now better supported in two specific ways:

1. The empty-evidence finding was reproduced through the actual published initialization gate, with positive and negative controls. This strengthens the justification for the first bounded contribution without inflating it into a driver-completion claim.
2. Missing dependencies, skipped firmware checks, the blocked integration target, and failed SSH discovery were observed and recorded instead of being counted as successes.

The wider report's earlier host-test results and other authors' hardware measurements remain historical evidence at the documented pins. This revalidation did not rerun every historical suite or independently reproduce the physical measurements. The collaborative b43 recommendation remains an assessment, not a guaranteed successful-driver outcome.

No public PR, issue, email, license change, visibility change, kernel experiment, or NixOS configuration change was made.
