# Air access setup

## What is configured, not yet verified remotely

The inspected NixOS configuration enables NetworkManager, key-only OpenSSH for the normal user, the desktop's public key, Avahi/mDNS, and Tailscale. Root SSH and password authentication are disabled. The deployed laptop may differ from the checked-in configuration.

The laptop's current checked-in lid policy suspends on closing the lid. Initially connect AC power and leave the lid open.

At the 2 October 2026 access preflight, the desktop's Tailscale daemon was running, but no matching Air peer was found, and `macbook-air.local` had no resolved LAN address. No remote command or hardware test ran. This is historical status, not a live availability indicator.

## Physical setup

1. Connect a supported USB Ethernet adapter to the laptop and LAN.
2. Connect power and leave the lid open.
3. Confirm an Ethernet interface is connected with `nmcli device status` on the Air.
4. Use `macbook-air.local` or the Ethernet IP printed by `ip -br address`.
5. Connect with the desktop's existing SSH key as the normal laptop user.

Verify a new host-key fingerprint on the laptop before accepting it. Do not disable host-key checking, enable root SSH, share passwords in chat, or change credentials merely to get access.

## Read-only preflight once reachable

- Record kernel version, architecture, exact PCI device/subsystem IDs and revisions, active drivers, boot generation, and available memory/storage.
- Check Ethernet device state and the actual return route to the SSH client. An address from Tailscale does not prove the traffic uses Ethernet rather than Wi-Fi.
- Check noninteractive privileged access with `sudo -n true`. If not available, agree on narrowly scoped access for the planned experiments. Do not automatically install blanket passwordless sudo.
- Confirm the known-good boot entry remains available.
- Establish a baseline for working proprietary `wl`, if working Wi-Fi is present, before comparing an experimental implementation.

Do not include raw board dumps, network identifiers, or credentials in a baseline committed here. Do not use indirect PHY/radio reads as a routine inventory shortcut.

## Autonomy and recovery

Hardware work starts only after the Ethernet control path and experiment scope are verified. Ethernet protects network access, not the kernel from freezing. The owner must still be able to perform occasional physical power cycles or select a recovery boot.

Autonomous work requires an active Jcode session or an explicitly arranged background/scheduled task. Leaving the laptop on does not itself establish continuous monitoring.
