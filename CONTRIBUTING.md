# Contributing to FlowGen Image Studio

Thank you for your interest in contributing to FlowGen Image Studio! This is a free, open-source project designed to provide an unlimited batch image generation bridge.

## How to Contribute

### 1. Reporting Bugs
- Check the existing GitHub Issues before opening a new one.
- Provide clear reproduction steps, OS version, and any relevant console logs from `browser2api/run_hud.py`.

### 2. Feature Suggestions
- Open an Issue with the prefix `[Feature Request]` describing the proposed workflow or capability.

### 3. Submitting Pull Requests
1. Fork the repository.
2. Create a descriptive branch: `git checkout -b feature/my-new-feature`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. Commit your changes with clear messages.
5. Push to your branch and open a Pull Request against `main`.

## Code Guidelines
- Adhere to clean, readable Python code.
- Avoid unnecessary external dependencies when standard libraries or existing packages suffice.
- Ensure all GUI and multi-worker telemetry updates remain functional.

---
Maintained by **Ali Bhatti** ([@AliRash3ed](https://github.com/AliRash3ed)).
