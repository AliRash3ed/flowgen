# Security Policy

## Data Privacy & Session Storage

FlowGen is built with local-first privacy:
- **Local Storage Only**: Your Google login cookies and browser profiles are stored strictly on your local disk (or container instance) and are never transmitted to external servers.
- **Git Protection**: The repository's `.gitignore` explicitly prevents `.browser2api/`, `user_data/`, and session files from being committed.
- **API Key Authentication**: When exposing FlowGen over the network or via Google Colab / Cloudflare tunnels, use the `FLOWGEN_API_KEY` environment variable to secure access.

## Reporting a Vulnerability

If you discover a security vulnerability within FlowGen, please report it responsibly by contacting the maintainer via GitHub issues or email before public disclosure.
