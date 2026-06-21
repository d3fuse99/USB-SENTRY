<h1>USB-SENTRY 🛡️</h1>

<img width="2553" height="1323" alt="image" src="https://github.com/user-attachments/assets/3083e3b7-1a72-4449-afca-77b3646b55d3" />


**Zero-dependency forensic analyzer, dynamic live monitor, and active hardware lockout controller.**

USB-SENTRY is a high-performance host security and forensics framework built to inspect, audit, and actively protect Windows ports. Operating under a default-deny security model, it locks down physical connections, logs forensic metadata chronologically, and provides Just-In-Time (JIT) temporal authorization controls secured by a cryptographically signed database.

---

<h2>Features</h2>

* **Broad Hardware Auditing**: Parses both USBSTOR and USB controller nodes, tracking flash drives, keyloggers, BadUSBs, and general HID devices.
* **Dual Forensic Timestamps**: Decodes 64-bit Windows FILETIME last-connection metrics and parses system SetupAPI logs to locate the exact first connection event.
* **Active Threat Mitigation**: Runs an elevated background monitor thread that programmatically disables unauthorized PnP hardware instantly via Windows Defender-level controls.
* **Just-In-Time (JIT) Override**: Locks down ports by default. Authorized administrators can unlock the host temporarily (for 2, 5, or 15 minutes) with automated graceful relocking.
* **Instant Manual Re-locking**: Allows the administrator to instantly arm the security daemon early by clicking the green unlocked state button.
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
