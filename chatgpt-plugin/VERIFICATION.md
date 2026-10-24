# Verification record — 24 October 2026

## Executed locally

- Python 3.12, MCP SDK 2.3.0, Uvicorn 0.54.0.
- `pytest -q`: 38 passing tests. Covers exact matches, shared-payment ambiguity, every matching constraint, currency precision, invalid money, duplicate IDs, quoted CSV/BOM, malformed/oversized input, date-window validation, formula-safe exports, statelessness, HTTP handling, sample-only protection and private local CSV execution.
- `python verify_mcp.py`: passed against a real child server over loopback HTTP. MCP initialization, tool enumeration, sample calculation, UI resource MIME/content and denied custom data in sample-only mode verified.
- JavaScript syntax check with Node.js 24: passed.
- Sample result: 3 invoices / 3 payments; 1 matched, 1 ambiguity hold, 1 unmatched, 2 unallocated payments. Matched total: OMR 12.345.

## Not yet executed or established

- Browser visual and interaction verification. The available cloud browser refused the local file test URL; no screenshot or successful visual check is claimed.
- Live ChatGPT installation and embedded component bridge/download behavior.
- Hosted HTTPS endpoint. Railway's connector returned reauthentication required before any resource was created.
- Docker image build and runtime verification.
- Public plugin submission, organization verification and review approval.
- Remote authentication or production financial-data processing.

These are separate acceptance gates. Passing local protocol tests is not a claim of ChatGPT directory availability or production readiness.
