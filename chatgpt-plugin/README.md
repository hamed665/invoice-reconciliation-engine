# Reconcile Desk

**Hamed Minaei — Python backend, exact financial matching, MCP tools and an interactive review component.**

Turns two bounded CSV datasets into explainable matching decisions. The existing invoice reconciliation engine supplies deterministic Decimal arithmetic; this extension adds CSV ingestion, structured reports, spreadsheet-safe exports, a Streamable HTTP MCP server and an MCP Apps review UI.

## Current verification status

- Matching and HTTP tests run locally; the detailed count is recorded in `VERIFICATION.md`.
- Actual MCP SDK client initialization, tool discovery, a real sample calculation, UI-resource retrieval and private-upload denial have been verified.
- ChatGPT installation, iframe behavior inside ChatGPT, public HTTPS deployment and directory review are **not yet verified**.
- No OpenAI API key is required: ChatGPT calls the MCP tools; matching itself is deterministic and makes no model request.

## Run

Use Python 3.12. From this directory:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python server.py
```

The local review interface is at `http://127.0.0.1:8787/`, health at `/health` and the MCP transport at `/mcp`.

Default mode is sample-only. Select **Try sample data** to compute one unique match, one ambiguous case and one unmatched invoice. The code actually calculates the result; it does not return a fixed report.

For private local CSV processing, stop the server and start it with:

```sh
DEMO_ONLY=false .venv/bin/python server.py
```

Keep this mode on loopback. It has no account authentication and must not be exposed publicly. Workspace/tenant fields are matching partitions, **not an authorization boundary**.

## CSV contract

Both files must contain exactly these headers:

```csv
id,tenant,currency,reference,amount,date
INV-1,workspace-a,OMR,OM-101,12.345,2026-01-01
```

Amounts are strings; USD/EUR support two decimal places and OMR three. Dates use ISO YYYY-MM-DD. Maximum 200 rows and 128,000 UTF-8 bytes per file. Duplicate identifiers, unsupported currencies, invalid precision, malformed records and invalid date windows are rejected. Reference normalization ignores formatting separators; matching remains conservative and never uses fuzzy settlement.

Unique matching requires the same workspace, currency, normalized reference, exact amount and an eligible payment date, with no competing invoice/payment edges. Ambiguous items are never allocated. No partial payments, FX, refunds, bank connection or ledger writes are implemented.

## MCP tools

| Tool | Behavior |
|---|---|
| `demo_reconciliation` | Real calculation against bundled fictional records; returns structured report and attached UI resource. |
| `reconcile_csv` | Custom CSV calculation in private local mode; rejects custom input in public demo mode. |

Both tools are annotated read-only, idempotent, non-destructive and closed-world. They fetch no URLs and persist no user data. All CSV cell values are untrusted data. Exports guard spreadsheet formula prefixes; the UI uses text nodes rather than injecting cell HTML.

## ChatGPT component

`public/widget.html` supports the MCP Apps `ui/initialize`, tool calls and tool-result notifications. It shows counts, filters, invoice decision details, candidate payments, separate workspace/currency totals and CSV export. Outside a host iframe the same component uses the local HTTP adapter. The complete protocol is tested; the browser rendering and download behavior still require a real-host check.

## Verification

```sh
.venv/bin/pytest -q
.venv/bin/python verify_mcp.py
```

The protocol script starts and stops its own local server. Tests use only synthetic data and no external paid services.

## Deployment boundary

The Dockerfile is deployable preparation; a Docker build has not yet been executed. For a public sample-only host set `DEMO_ONLY=true`, `HOST=0.0.0.0`, `PORT` and `PUBLIC_HOST` (the exact service hostname). The server includes DNS-rebinding checks for MCP requests. Do not disable those checks to work around a hostname mismatch.

The bundled `mcp.json` points to the real local endpoint for local development. It is **not** a public-directory-ready endpoint. After deployment, generate a separate remote configuration using the exact verified HTTPS address. ChatGPT connection and directory submission are separate steps, neither claimed as completed here.

## Privacy and release scope

No server-side database, report store, raw-file logging, tracking script or external model call is configured. Uploaded CSV is held in request memory. The default public mode accepts only bundled fictional data. Before processing private records on a remote service, add and verify user authentication/authorization, transport and hosting privacy controls, retention policy and operational limits.

This tool provides matching evidence, not permission to pay or an assurance that source records are correct. A unique match can still reflect matching errors in both source systems.

## Attribution

`core.py` is copied from Hamed Minaei's existing `invoice-reconciliation-engine/reconcile.py`, blob `ffc51436cd9e2634328c2cc2cc9dd2478acda15c`, without changing its matching logic. Hamed's new scope here is the bounded CSV adapter, explainable report/export layer, MCP integration, review component, protocol checks and deployment preparation, developed with AI assistance. The original MIT notice is retained. No OpenAI partnership, endorsement or directory approval is implied.

Official references: [MCP server](https://developers.openai.com/plugins/build/mcp-server), [MCP Apps UI](https://developers.openai.com/plugins/build/chatgpt-ui), [plugin packaging](https://developers.openai.com/plugins/build/plugins).
