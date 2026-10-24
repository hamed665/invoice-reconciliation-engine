# Verification record — 24 October 2026

## Executed locally

- Python 3.12, MCP SDK 2.3.0, Uvicorn 0.54.0.
- `pytest -q`: 43 passing tests. Covers exact matches, shared-payment ambiguity, every matching constraint, currency precision, invalid money, duplicate IDs, quoted CSV/BOM, malformed/oversized input, date-window validation, formula-safe exports, statelessness, HTTP handling, sample-only protection and private local CSV execution.
- `python verify_mcp.py`: passed against a real child server over loopback HTTP. MCP initialization, tool enumeration, sample calculation, UI resource MIME/content and denied custom data in sample-only mode verified.
- JavaScript syntax check with Node.js 24: passed.
- Sample result: 3 invoices / 3 payments; 1 matched, 1 ambiguity hold, 1 unmatched, 2 unallocated payments. Matched total: OMR 12.345.

## UI and input hardening follow-up

- Public UI hides unsupported CSV upload controls; private local mode retains them.
- Added selected-row feedback, keyboard focus styling, scroll-region label, processing/completion/error announcements and unallocated-payment count.
- Malformed quoted CSV headers and dates outside YYYY-MM-DD return validation errors.
- Standalone UI sends a restrictive Content-Security-Policy; no third-party fonts, scripts or trackers.
- Re-ran all 43 tests, JavaScript syntax check and real local MCP smoke after these changes.
- Visual browser, responsive viewport and real ChatGPT embedded bridge/download checks remain pending; these changes are not evidence of those checks.

## Executed on the existing VPS

- Docker image `reconcile-desk:831f88f` built and started on the authorized VPS.
- Container health: healthy. No published host ports; dedicated internal network, no application/database network attachment.
- Runtime limits: 0.25 CPU, 192 MiB RAM, 64 PIDs, read-only root filesystem and dropped Linux capabilities.
- Real Streamable HTTP MCP smoke executed inside the container: tool enumeration, sample reconciliation, UI resource and sample-only upload protection passed.
- Existing Almaha website and Inbox returned HTTP 200 after deployment.
- Existing Caddy configuration SHA-256 unchanged: `433fbf6d14ab895f911432e58c28f2e169ccee364818712fbb9f4a363b3bcdfc`.
- Public DNS and Caddy routing were not changed. The container is internal only.

## Not yet executed or established

- Browser visual and interaction verification. The available cloud browser refused the local file test URL; no screenshot or successful visual check is claimed.
- Live ChatGPT installation and embedded component bridge/download behavior.
- Hosted HTTPS endpoint. Railway's connector returned reauthentication required before any resource was created.
- Public plugin submission, organization verification and review approval.
- Remote authentication or production financial-data processing.

These are separate acceptance gates. Passing local protocol tests is not a claim of ChatGPT directory availability or production readiness.
