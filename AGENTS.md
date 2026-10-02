# Instructions for research agents

## Scope and evidence

- Work toward small contributions to existing BCM4360 projects, not an assumed whole-driver rewrite.
- Refresh and pin upstream before new work. Keep historical observations distinct from current results.
- Label evidence as reproduced host test, code inspection, author hardware evidence, author claim, or assessment.
- Reproduce a failing witness before fixing it. Use actual public test entry points where possible. Record limitations and failures as carefully as successes.
- Do not say a modeled register match establishes working RX, TX, association, or RF correctness.

## Access and experiments

- Read `docs/ACCESS.md` and `docs/SAFETY.md` before any remote work.
- Read-only inventory and safe host-only development may proceed autonomously once access is authorized.
- Do not start driver unloading/loading, experimental boots, MMIO probing, firmware writes, or RF experiments without an agreed hardware-test scope and recovery plan.
- Confirm the SSH control path uses independent Ethernet. Tailscale alone does not establish independence from the BCM4360.
- Preserve the working `wl` installation and recovery generation. Never repartition or garbage-collect recovery generations for an experiment.
- Stop on unexpected all-ones reads, PCIe faults, repeated PHY errors, link loss, or hard freezes. Do not blindly retry resets or another board's replay.
- Avoid known freeze-producing 5 GHz indirect read paths and regulatory bypasses.
- Keep power and suspend behavior explicit. A host timeout cannot recover a kernel lockup.

## Files and publication

- No vendor binaries, extracted firmware, raw captures, credentials, upstream clones, or private board dumps in Git, even in a private repository.
- Use `PROVENANCE.md` for licensing and provenance decisions. Do not claim clean-room status without actual information-flow boundaries.
- No repository-wide license has been assigned yet. Do not assume research notes or third-party excerpts can be relicensed wholesale.
- Do not submit PRs, send issues/emails, change visibility, or publish data without authorization.
- Only a human can supply their own DCO `Signed-off-by`. Do not manufacture one for an agent or the owner.

## Workflow

- Keep the task plan current. Use small, reviewable commits with observed validation.
- Run `make check`, `make test`, and `git diff --cached --check` before committing.
- Review staged contents rather than trusting `.gitignore` or the checker alone.
- Edit with the provided file-editing tools, not ad hoc scripts that rewrite files.
- No em dash in new prose.
- Do not promise perpetual unattended work. State which active session or explicitly scheduled task is responsible for running experiments.
