<h1>USB-SENTRY 🛡️</h1>

<img width="2559" height="1318" alt="image" src="https://github.com/user-attachments/assets/40627679-1e03-4663-afcb-01581c5f5d8a" />

**Windows USB forensics analyzer, live monitor, and active whitelist controller.**

USB-SENTRY is a lightweight, zero-dependency host forensics and access control tool designed to inspect, identify, and authorize external mass storage devices. It extracts deep registry artifacts under high-risk hardware nodes, visualizes connection history chronologically, and helps secure hosts against unauthorized USB threat vectors (like BadUSB or malicious flash drives).

---

<h2>Features</h2>

* **Extended Hardware Support**: Scans both USBSTOR (mass storage) and USB controller nodes, tracking keyboards, webcams, and BadUSB emulators.
* **Dual Forensic Timestamps**: Decodes and displays both the very first connection time (extracted from SetupAPI system logs) and the last modified write time.
* **Real-Time Toast Alerts**: Instantly fires beautiful sliding breach alerts on the web dashboard upon unauthorized device insertions.
* **Cryptographically Secured Whitelist**: Uses SHA-256 signatures salted with a local machine key to prevent manual database tampering.
* **Zero-Dependency Light Footprint**: Formulated strictly with native Python 3 standard modules and raw HTML5/CSS3/ES6 JS.
* **XSS-Hardened Execution**: Programmatically renders DOM nodes to bypass unsafe innerHTML sinks, protecting administrators against script injection.
* **High-Fidelity Simulation Fallback**: Auto-detects virtual machines or clean environments without hardware history and provisions high-fidelity simulation entries for diagnostics.

---

<h2>How to run</h2>

1. **Administrative Access**: Open **PowerShell** (or Windows Terminal) as an **Administrator** (optional, recommended for raw system registry queries).
2. **Launch Controller**: Run the backend daemon from the project directory:

   ```bash
   python server.py
