USB-Sentry
==========

Forensic and Security Monitoring Framework for Windows USB Storage History.

This project scans, visualizes, and monitors historically connected USB mass storage devices from the Windows registry, correlating them with an authorized whitelist to detect potentially unverified or hostile hardware (such as Rubber Ducky or untrusted flash drives).

Project Architecture
--------------------

* server.py - Entry script hosting the HTTP dispatch server.
* scanner.py - Forensic analyzer query engine mapping active registries.
* db.py - Local persistent store tracking trusted hardware authorizations.
* index.html - Application root markup layout.
* style.css - Clean high-tech cyber-ops styling sheet.
* app.js - Security-hardened operations application controller.

Key Features
------------

* Automated Registry Analysis - Scans HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR for hardware connection history.
* Safe Dynamic DOM Rendering - Replaced legacy HTML inner injection sinks with safe modern DOM elements, completely eliminating XSS vulnerability classes.
* Graceful Simulation Fallback - Automatically falls back to high-fidelity simulation on non-Windows hosts or clean environments lacking USBSTOR records.
* Access Control Matrix - Whitelist management console storing trusted state signatures locally.

Deployment and Usage
--------------------

1. Save all project files into a single directory on your machine.
2. Spin up the local HTTP web server by running the entry script:

   python server.py

3. Open your favorite web browser and navigate to the local portal:

   http://127.0.0.1:9090
