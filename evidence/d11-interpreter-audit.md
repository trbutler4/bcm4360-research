# Public D11 interpreter follow-through

Audit date: 2026-10-02. Addendum to `aleferri-audit.md`. Bounded follow-through, no children or hardware access.

## Pin and availability

Public source cloned successfully, without submodules or firmware downloads, into `repos/aleferri--b43-tools`. Exact current HEAD is **2361e9e8aad9f2912877b82be5cc529b3dd390a1**, subject `provide some conditions and init values from real capture`, author timestamp 2026-10-02T13:11:41+02:00, commit timestamp 13:57:23+02:00. It is available, not a hypothetical unpublished dependency. The earlier audit's statement that the external interpreter was unavailable describes that earlier test boundary and is superseded by this follow-through.

Pinned citation prefix: https://github.com/aleferri/b43-tools/blob/2361e9e8aad9f2912877b82be5cc529b3dd390a1/interpreter/

`psm.py`, `ucode_init.py` and `cosim.py` have explicit GPL version 2 headers. The public interpreter requires Python's standard library for ordinary unseeded execution. Named condition seeding additionally needs a local OpenFWWF `cond.inc` (`cond.py:70`), not downloaded here. The original driver wrapper still does not pin this external repository revision.

## Is execution real?

**Yes, within a limited interpreter model.** `psm.py:492-505` loads 64-bit instructions from raw-be32 32-bit word pairs, reconstructs the codeword, and decodes operands/opcodes. `325-459` reads source operands, computes effects, writes modeled memory/registers and advances the PC. Version stamps are computed by interpreting actual blob instructions, not filled with hardcoded board version constants. This is materially stronger than the C D11 model's synthetic boot handshake. It is still not full firmware or chip emulation.

Decoder validation against b43-dasm and four successful version blocks are repository-reported (`README.md:78-104`), not all reproduced here. Direct decoder agreement does not validate execution semantics: the disassembler need not know how a conditional branch or arithmetic flag behaves.

Important source limitations:

- `psm.py:59-88`: branch/extended bit-field/call-stack semantics are best-effort, external conditions are configurable stubs, and nap does not implement actual sleep. Rotations are explicitly best-effort 16-bit operations (`368-379`), despite the README grouping arithmetic broadly as high confidence.
- `417-442`: jext/jnext use unmodeled flags defaulting false. Divider-related conditions jdn/jdpz/jdp/jdnz are forced false. This cannot reproduce arbitrary reset, interrupts, packet handling or dispatch.
- `285,445-451`: **strict defaults false**. Unknown instructions, ret and TKIP operations become NOPs with an unimplemented count, unless a caller explicitly enables strict mode. The top comment saying TKIP raises is conditional, not the default behavior. Confidence tags are recorded only if tracing is enabled (`455-456`), whereas `ucode_init.py` disables tracing.
- `461-475`: hardware-wait detection is lack of increasing highest PC, a heuristic. A legitimate long loop confined below a prior high PC can trigger it, and its name does not prove a specific physical ready signal is missing.
- `ucode_init.py:70-89` catches general execution exceptions, emits sparse nonzero SHM and returns 0. It does not assert expected revision, block completion or absence of unsupported instructions. It also discards the return reason from `PSM.run`, so an out-of-bounds halt is reported as `stop=max_steps`. Reproduced below.

## Safe smoke test with already-local firmware

Existing coordinator-provided material was found after the original audit: `vendor-input/lib/wlc_hybrid.o_shipped`, a little-endian x86-64 ELF, and its previously extracted `vendor-input/firmware-slices/d11ucode42.bin`. No object/blob was fetched or newly extracted from an online source. Existing metadata `evidence/vendor-firmware-slices.json` pins source SHA256 `352a6e349f74c69b78e76f68c63752c99b8f6b22dc942af531b754211d7f4743`, slice 43,400 bytes, slice SHA256 `22cf38bc3bf3b974397368ad1552885ec4482e3c83286621b7c1adbfee3d1a73`.

### Format correction is essential

The ELF slice stores **little-endian 32-bit words**, while the interpreter needs raw-be32. Passing the raw slice directly to a strict interpreter rejected opcode unk_802 at PC0 and unk_E06 at the default PC0xF76. Those failures are input-format errors, not evidence that the correctly encoded firmware is unsupported.

An inspected standard-library-only helper `evidence/d11-normalize-local.py` converts each already-local 32-bit word from little endian to big endian, preserving instruction word order. It writes only scratch `evidence/d11ucode42-local-raw-be32.bin`, SHA256 **cbaa4ebd7bd132612305652fc3b0fe4c2954e8724eb05c2adb802583d0438561**. No source or original input was modified.

This also exposes a generalization risk in the audited driver's `reverse-tools/extract_ucode.py:7,62-80`: it describes symbol bytes as big-endian as stored, copies them unchanged and decodes the size word with `>I`, without checking ELF byte order. That can work for its big-endian router input but does not produce interpreter-ready bytes for this little-endian laptop/vendor ELF. Use ELF endianness and explicitly normalize firmware words.

### Reproduced execution results

`evidence/d11-interpreter-smoke.py` uses the public loader and executor with `strict=True`, traces confidence, bounds PC0 to 30,000 steps and other starts to 64. A structural search finds an `orx` write into SHM word0 at **0xE46**, appropriate to this different firmware family. There was no firmware-value patching.

- Correctly formatted blob loads **5,425 instructions**, not the README D6220's 5,976.
- From **PC0**, execution raises HardwareWaitLoop after **20,016 steps**, PC **0x0107**, revision/patch remain zero. Trace counts HIGH5, STUB4, BEST-EFFORT20,007, zero executed unsupported instructions. Full reset-to-ready execution is not validated.
- From **default 0xF76**, it halts after **5 steps** at 0xF7B due to rets with an empty call stack. No version words are produced. Default entry is firmware-specific, not generic.
- From **0xE46**, 64 steps produce revision **0x0340** and patch **0x007F**, with HIGH16 and BEST-EFFORT48, no unsupported instruction. Initial instructions concatenate immediates 0x03/0x40 and 0x00/0x7F into SHM0/1. Subsequent execution enters unverified field operations, so confidence should not be extended beyond the tested version writes.
- Public `ucode_init.py --start 0xe46 --steps 10` produces SHM byte offsets 0x0000=0340, 0x0002=007f, 0x0004=e913, 0x0006=356d.
- Independently located original ELF symbols `d11ucode_ge40_bommajor/minor` are at .rodata offsets 0x95530/0x95534, section file offset0x181170. Direct `od` reading yields **00000340 0000007f**, exactly matching the interpreted version. This tests a third family beyond the README's 0x310 and 0x3A0, for the narrow stamp operation only.
- Public wrapper with `--start 0x9999` returns **exit0**, empty SHM and misleading `stop=max_steps`. This concretely reproduces its false-success boundary. It is not a comparator failure or successful firmware run.

A helper that tried importing pyelftools failed because it is absent from default Python. No installation was performed. Independent BOM verification instead used readelf/od; the ordinary interpreter and normalization need no pyelftools.

## Co-simulation is stronger than overlay, but still narrow

Public `cosim.py` shares `PSM.shm` with decoded host writes (`74-117`), calls real interpreter steps at boot/command/hostflag boundaries, and models scratch, receive-match and template memory. Template RAM writes at `123-129` are present here, unlike the separate C d11sim. It is not fair to transfer the C model's missing-template defect to this Python model.

However, `cosim.py:42-47` expressly does not model PSM IHR/MMIO reads, so MAC-command handlers do not dispatch as real firmware would. Its register dictionary is not wired into PSM SPR/IHR reads. PHY/radio/reads are ignored (`31-34`), there are no actual DMA/RF/packet/timing engines, and boot jumps directly to the chosen version block rather than starting at reset. `87-106` catches all step exceptions silently, still increments ucode_runs and records output without reporting the cause. Provenance records changed words rather than all attempted writes and remains sticky. Snapshots omit zero state (`163-186`). These are additional reasons not to treat matching state as demonstrated command handling or on-air viability.

No combined co-simulation acceptance comparison was claimed here: the already-local blob differs from the D6220/agcombo capture firmware, the actual b43 integration trace remains blocked by absent kernel headers, and full hardware signal/IHR semantics are missing. For a useful next test, pair matching vendor firmware with a matching capture and strict exception/counter reporting, then distinguish boot-stamp assertions from command/packet assertions.

## Reproduction commands and artifacts

Commands below ran only against public source and existing local data. Use `ROOT=/path/to/research-workspace`:

```sh
git clone --depth 1 https://github.com/aleferri/b43-tools.git "$ROOT/repos/aleferri--b43-tools"
git -C "$ROOT/repos/aleferri--b43-tools" rev-parse HEAD
readelf -h "$ROOT/vendor-input/lib/wlc_hybrid.o_shipped"
sha256sum "$ROOT/vendor-input/firmware-slices/d11ucode42.bin"
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/evidence/d11-normalize-local.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/evidence/d11-interpreter-smoke.py" \
  "$ROOT/repos/aleferri--b43-tools/interpreter" \
  "$ROOT/evidence/d11ucode42-local-raw-be32.bin"
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/repos/aleferri--b43-tools/interpreter/ucode_init.py" \
  "$ROOT/evidence/d11ucode42-local-raw-be32.bin" --start 0xe46 --steps 10 \
  --out "$ROOT/evidence/d11-local-version.shm"
readelf -sW "$ROOT/vendor-input/lib/wlc_hybrid.o_shipped" | grep -E 'bommajor|bomminor'
readelf -SW "$ROOT/vendor-input/lib/wlc_hybrid.o_shipped"
od -An -tx4 -j $((0x181170+0x95530)) -N 8 "$ROOT/vendor-input/lib/wlc_hybrid.o_shipped"
```

Artifacts: `d11-interpreter-smoke.py`, raw and normalized smoke logs, normalization helper, normalized local blob, version SHM and invalid-entry empty SHM. Original b43-ac-wip and cloned b43-tools working trees were clean after execution. Python bytecode writes were disabled. No hardware, module loading, firmware installation, network configuration, vendor downloads or extractor fetching occurred.

**Verdict:** public, reproducibly obtainable real instruction interpreter, with an independently reproduced stamp on already-local firmware and explicitly limited execution semantics. It is valuable for targeted microcode research, not a complete D11 emulator, reset-to-running proof, command/packet acceptance test or evidence of RF success.
