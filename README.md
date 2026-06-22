<h1>USB-SENTRY 🛡️</h1>
<img width="2548" height="1320" alt="image" src="https://github.com/user-attachments/assets/b4b1c9e1-ecc0-4ec2-a450-1255122c6b5b" />

<img width="2551" height="1327" alt="image" src="https://github.com/user-attachments/assets/44f0deb2-b12e-4b9f-abf2-949eb63e5997" />

**Zero-dependency forensic analyzer, dynamic live monitor, and active hardware lockout controller.**

USB-SENTRY is a high-performance host security and forensics framework built to inspect, audit, and actively protect Windows ports. Operating under a default-deny security model, it locks down physical connections, logs forensic metadata chronologically, and provides Just-In-Time (JIT) temporal authorization controls secured by a cryptographically signed database and an interactive configurations panel.

---

<h2>Features</h2>

* **Broad Hardware Auditing**: Parses both USBSTOR and USB controller nodes, tracking flash drives, keyloggers, BadUSBs, and general HID devices.
* **Dual Forensic Timestamps**: Decodes 64-bit Windows FILETIME last-connection metrics and parses system SetupAPI logs to locate the exact first connection event.
* **Active Threat Mitigation**: Runs an elevated background monitor thread that programmatically disables unauthorized PnP hardware instantly via Windows Defender-level controls.
* **Interactive Settings Control**: Modifies active system configurations (mitigation toggles, sound alarm triggers, scan rate parameters) natively through a premium, grid-card console panel.
* **Programmatic Siren Alarm**: Synthesizes a continuous sci-fi warning siren via HTML5 Web Audio API whenever unauthorized hardware is actively connected (completely zero-dependency).
* **Just-In-Time (JIT) Override**: Locks down ports by default. Authorized administrators can unlock the host temporarily (for 2, 5, or 15 minutes) with automated graceful relocking and manual early re-lock capabilities.
* **Visual Security Log Console**: Accumulates and renders a chronological audit log in a real-time event journal (logs.json) directly on the dashboard.
* **Credential Hardening & UX**: Formulates a stylish eye-toggle password visibility button, live Caps Lock detection, and automatic Cyrillic layout (RU/UA) alerts.
* **Cryptographically Secured Database**: Salts whitelisted signatures with a machine-specific key file (secret.key) and stores irreversible SHA-256 hashes to prevent manual database tampering.
* **Real-Time Toast Alerts**: Fires dynamic sliding HTML5 breach alerts on the screen the moment an unauthorized connection is attempted.

---

<h2>How to run</h2>

1. **Elevate Privileges**: Open **PowerShell** (or Windows Terminal) as an **Administrator** (necessary for automated device-disabling countermeasures).
2. **Launch Controller**: Spin up the backend daemon from the workspace:

   ```bash
   python server.py
