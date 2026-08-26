# USB-SENTRY 🛡️⚡
> **Host-Level USB Forensic Analyzer, Active Mitigation Daemon & Access Control Panel**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Platform Windows](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg?style=flat-square&logo=windows)](https://microsoft.com/windows)
[![Architecture Zero-Dependency](https://img.shields.io/badge/Dependencies-Zero%20External-success.svg?style=flat-square)](#)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**USB-SENTRY** is a high-performance host security and forensic tool designed to audit, detect, and programmatically neutralize unauthorized USB peripherals on Windows systems. Operating on a strict **Default-Deny** paradigm, it provides real-time PnP device inspection, chronological forensic timeline reconstruction, and temporal override authorization backed by a salted cryptographic database.

---

## 📸 Interface Preview

| Security Operations Console | Defense Policies & Configurations |
| :---: | :---: |
| ![Timeline Preview](preview-dashboard.png) | ![Settings Preview](preview-settings.png) |

---

## ✨ Key Features

* **Dual Registry & Driver Log Forensics:**
  * Reconstructs 64-bit Windows `FILETIME` timestamps directly from `SYSTEM\CurrentControlSet\Enum\USBSTOR` and `Enum\USB`.
  * Correlates SetupAPI (`setupapi.dev.log`) entries to identify the exact initial connection event.
* **Active Hardware Mitigation (PnP Lockdown):**
  * Automated background daemon intercepts unauthorized insertions (HID BadUSBs, Rubber Duckies, rogue storage, network dongles) and disables the hardware node via PowerShell PnP commands in real time.
* **Just-In-Time (JIT) Port Override:**
  * Physical ports remain armed by default. Administrators can authorize temporary bypass windows (2, 5, or 15 minutes) with automatic graceful re-lock.
* **Zero-Dependency Web Audio Siren:**
  * Uses the browser's native HTML5 Web Audio API synthesizer to fire tactical security alerts during active breach states without external audio assets.
* **Cryptographically Salted Signatures:**
  * Whitelist entries are irreversibly hashed (SHA-256) combined with a machine-bound random entropy salt (`secret.key`) to prevent offline tampering.
* **Real-Time Toast & Event Ledger:**
  * Live visual telemetry and an on-dashboard security log journal tracking every mitigation event, authorization attempt, and registry rescan.

---

## 📁 Repository Structure

```text
USB-Sentinel/
├── server.py        # Embedded HTTP controller & live monitor thread
├── scanner.py       # Windows Registry & SetupAPI forensic engine
├── mitigation.py    # Elevated PnP disabling countermeasures
├── db.py            # Salted cryptographic store & configuration manager
├── index.html       # Cyberpunk-themed operations dashboard
├── style.css        # Clean dark-mode SOC interface styling
├── app.js           # Real-time state synchronizer & audio engine
├── settings.json    # Default mitigation & scan parameters
├── whitelist.json   # Trusted hardware repository
└── .gitignore       # Protection rules for keys and runtime logs
