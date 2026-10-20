# Engineering walkthrough

**Hamed Minaei · Conservative financial matching**

## Problem and implemented scope

Exact decimal arithmetic, minor-unit rules, tenant/currency isolation and one-to-one ambiguity holds.

## Demonstration evidence

The fixture includes a unique OMR settlement, competing USD payments and an unmatched invoice. Ambiguous records never become automatic settlements.

Run `python demo.py` and compare with `docs/demo-output.json`.
Run `python -m unittest discover -s tests -v` to inspect failure-path behavior.
The verification workflow runs those commands on Python 3.11, 3.12 and 3.13.

## Review guide

1. Read the core implementation and the Architecture section of README.
2. Inspect tests for both permitted behavior and failure/ambiguity cases.
3. Review PR #1 for the initial implementation and its verification results.
4. Read Security and Limitations before extending or integrating the component.

## Portfolio description

"Conservative financial matching: Exact decimal arithmetic, minor-unit rules, tenant/currency isolation and one-to-one ambiguity holds. Includes a reproducible synthetic demonstration,
behavioral tests and CI verification."

This describes the implemented component, not an operating production service.
Development assistance and ownership are recorded in AUTHORS.md.
