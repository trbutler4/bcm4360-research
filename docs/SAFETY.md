# Hardware safety policy

## Before any experimental driver or register access

- Obtain approval for the initial hardware-test scope, likely disruption, and recovery procedure.
- Verify independent Ethernet SSH and the route back to the controlling desktop.
- Keep power, lid/suspend behavior, and the owner's availability for physical recovery explicit.
- Identify the exact device, subsystem, PHY/radio revisions where safely available, and target kernel. Shared PCI IDs are not shared board configurations.
- Preserve the installed working `wl` system generation and boot entry. Build experiments separately when practical.
- Review board/chip gates, failure propagation, memory/DMA lifetime, firmware assumptions, and provenance before loading code.

## Limits

Do not repartition, remove boot entries, delete recovery generations, or replace the default boot configuration as a convenience. Do not reset credentials, enable remote root login, or add unrestricted passwordless sudo automatically.

Do not replay another board's analog initialization blindly. Do not bypass regulatory constraints or conduct unrestricted RF sweeps. Do not write firmware/NVRAM or probe indirect PHY/radio windows merely because a script exists.

Known audited risks include hard-freezing 5 GHz indirect read paths, device-loss/all-ones MMIO behavior, and uncertain DMA resource lifetime after PCIe loss. None is made safe by a command timeout or Ethernet connection.

## Each experiment

Use an [experiment record](../experiments/TEMPLATE.md) with one bounded hypothesis, exact source pin, test preconditions, expected result, recovery procedure, and stop conditions.

Start with host-only tests. If hardware is necessary, prefer the least disruptive observation that answers the question. Review the actual script before running it. Never execute a repository's bring-up script simply to see what happens.

Store raw artifacts outside Git. Commit sanitized findings only after provenance and identifier review.

## Stop conditions

End the experiment on unexpected all-ones reads, PCIe/AER faults, repeated PHY errors, loss of the independent connection, inconsistent board identity, or a hard freeze. Preserve evidence and reassess rather than repeatedly forcing access or improvising resets.

A kernel lockup may require physical power-cycling. Do not report successful recovery until it is observed. A preserved boot generation offers a recovery option, not a guarantee against persistent device failure.
