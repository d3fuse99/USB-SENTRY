<h1>USB-SENTRY 🛡️</h1>

<img src="https://raw.githubusercontent.com/d3fuse99/USB-SENTRY/main/screenshot.png" alt="USB-Sentry Console UI" width="100%" />

**Windows USB forensics analyzer, live monitor, and active whitelist controller.**

USB-SENTRY is a lightweight, zero-dependency host forensics and access control tool designed to inspect, identify, and authorize external mass storage devices. It extracts deep registry artifacts under high-risk hardware nodes, visualizes connection history chronologically, and helps secure hosts against unauthorized USB threat vectors (like BadUSB or malicious flash drives).

---

<h2>Features</h2>

* **Automated Forensic Parsing**: Extracts deep registry records under HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR.
* **Precise Timeline Extraction**: Decodes Windows 64-bit FILETIME connection timestamps to present an exact chronological ledger.
* **Zero-Dependency Light Footprint**: Formulated strictly with native Python 3 standard modules and raw HTML5/CSS3/ES6 JS.
* **Dynamic Cyber-Ops Console**: Visually stunning dashboard tracking active database metrics, whitelists, and real-time security alerts.
* **XSS-Hardened Execution**: Programmatically renders DOM nodes to bypass unsafe innerHTML sinks, protecting administrators against script injection.
* **High-Fidelity Simulation Fallback**: Auto-detects virtual machines or clean environments without hardware history and provisions high-fidelity simulation entries for diagnostics.

---

<h2>How to run</h2>

1. **Administrative Access**: Open **PowerShell** (or Windows Terminal) as an **Administrator** (optional, recommended for raw system registry queries).
2. **Launch Controller**: Run the backend daemon from the project directory:

   ```bash
   python server.py
