# Invoice Reconciliation Engine

![Verify](https://github.com/hamed665/invoice-reconciliation-engine/actions/workflows/verify.yml/badge.svg)

A conservative invoice/payment reconciliation engine that matches only unique evidence and holds ambiguous settlements for review.

**Status:** tested reference implementation with a reproducible synthetic CLI demo.
Built as an independent engineering portfolio project by [Hamed Minaei](https://github.com/hamed665).

## Features

- Exact Decimal arithmetic with explicit USD/EUR/OMR minor-unit precision.
- Matching scoped by tenant, currency, normalized reference, exact amount and date window.
- One-to-one bipartite candidate checks prevent payment reuse.
- Ambiguous matches remain unallocated; no greedy or fuzzy auto-settlement.
- Separate settled totals by tenant and currency, without floating-point money.

## Quick start

Python 3.11 or newer; only the standard library is used. No package install is required.

```bash
git clone https://github.com/hamed665/invoice-reconciliation-engine.git
cd invoice-reconciliation-engine
python demo.py
python -m unittest discover -s tests -v
```

The demo performs real computation against synthetic data. Its captured output is in
[docs/demo-output.json](docs/demo-output.json). It uses no customer records or production systems.

Evaluate your own schema-compatible local fixture with `python demo.py --input sample.json`.

## Architecture

Validation converts each invoice and payment to a normalized tuple. A candidate graph connects records only when all identity/money fields agree and the payment date falls between invoice date and max_days later. A match is emitted only when both endpoints have exactly one candidate. Remaining candidate edges become ambiguity holds; unmatched payments are returned for review. Complexity is O(invoices × payments), bounded to 1,000 records per side.

Core implementation: [reconcile.py](reconcile.py).
The core is separate from the demonstration runner and can be imported directly:

```python
from demo import run

report = run("sample.json")
assert report["invoices"][0]["status"] == "matched"
assert report["invoices"][1]["status"] == "ambiguous"
assert report["invoices"][2]["status"] == "unmatched"
print(report["settled_totals"])
```

## Installation and configuration

`reconcile(invoices, payments, max_days=45)` accepts lists of dictionaries. Each record requires string id, tenant, currency, reference, amount and ISO date. IDs must be unique within each input. Supported currencies: USD/EUR (2 decimal places), OMR (3). Positive amounts only, maximum 15 integer digits and 18 significant digits. `sample.json` is the input schema example. No environment variables or external services are required.

An optional Dockerfile runs the same demo under a non-root UID:

```bash
docker build -t invoice-reconciliation-engine .
docker run --rm --read-only --network none --tmpfs /tmp:rw,noexec,nosuid,size=32m invoice-reconciliation-engine
```

The Docker definition is provided for reproducibility. Container execution is not claimed as verified unless recorded in VALIDATION.md.

## Testing

`python -m unittest discover -s tests -v` runs 12 behavioral tests.
GitHub Actions runs those tests and the demo on Python 3.11, 3.12 and 3.13.
Action dependencies are pinned to commit SHAs and the workflow token is read-only.
See [VALIDATION.md](VALIDATION.md) for local evidence and verification scope.

## Security

All bundled records are synthetic. This program reads JSON and prints decisions; it never transfers money or changes a ledger. Restrict access to real financial files and validate their provenance in a production adapter. Do not log raw bank/customer records. Reference normalization intentionally ignores separators; collisions are handled as ambiguity when multiple records compete.

## Limitations

No partial payments, refunds, FX, fees, bank connector, fuzzy matching or ledger writes. Identical mistaken records on both sides can still match: reconcile against trusted source data. A unique exact match is evidence, not authorization to pay. The in-memory quadratic candidate graph is intended for bounded batches, not large bank statements. Read input files only from trusted/local paths; the CLI does not enforce a file-byte cap.

## Attribution and ownership

This repository is an original implementation created for Hamed Minaei's portfolio with
AI-assisted development and local verification. No upstream application's source code or
Git history was imported. Python's standard library supplies the underlying runtime,
SQLite bindings, cryptography primitives, JSON, dates and decimal arithmetic as used here.
The implementation, tests, synthetic fixtures and documentation are maintained in this repository.

License: [MIT](LICENSE). No third-party runtime packages are required.
