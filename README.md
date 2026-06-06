# Axezent AI Cognitive Trace Replay Kernel

**Axezent AI CTR** is an open-source compliance turnstile for AI agent outputs.

It checks whether a submitted AI output obeyed a declared deterministic receipt, policy pack, file-diff boundary, test result, and evidence hash trail.

The core principle is simple:

```text
No claim without a receipt.
```

An AI agent may generate code, analysis, citations, operational instructions, or repository edits. Axezent AI CTR does not blindly trust the output. It requires a finite receipt that can be checked step by step.

```text
Untrusted AI output
        ↓
trace receipt
        ↓
policy replay checker
        ↓
PASS / FAIL / INCOMPLETE
        ↓
audit-ready result
```

## Truth Boundary

Axezent AI CTR does **not** claim that an AI model is globally truthful, fully aligned, or permanently safe.

It verifies a narrower and stronger claim:

> Given a submitted finite receipt and a declared policy pack, the checker verifies whether the receipt obeys the deterministic rules in that policy pack.

## Quick Start

Run the passing demo:

```bash
python axezent_ctr_checker.py verify passing_receipt.json --policy software_safe_v1.json
```

Expected result:

```text
ACCEPT
```

Run a failing demo:

```bash
python axezent_ctr_checker.py verify failing_receipt_modified_forbidden_file.json --policy software_safe_v1.json
```

Expected result:

```text
REJECT
```

Run Python tests:

```bash
python -m pytest test_checker.py
```

Run Rust scaffold tests:

```bash
cargo test
cargo run
```

## Browser Upload Edition

This package is intentionally flat at the repository root so GitHub browser upload does not lose folder structure.

The intended workflow file is still:

```text
.github/workflows/main.yml
```

If your operating system hides `.github`, create that file manually in GitHub and paste the contents of `GITHUB_WORKFLOW_MAIN.yml`.

## What This Does

Axezent AI CTR verifies finite receipts for deterministic compliance rules. A receipt records what an AI agent claims it did, which files or artifacts it touched, which hashes were produced, and which tests or checks were run.

The checker returns:

```text
ACCEPT      receipt obeys the declared policy
REJECT      receipt violates the declared policy
INCOMPLETE  receipt lacks required evidence
```

## What This Does Not Do

Axezent AI CTR does not prove:

- the AI was globally truthful
- the AI was fully aligned
- the AI never hallucinated
- hidden model reasoning was verified
- all future outputs are safe
- all software is bug-free

## Included Files

- `axezent_ctr_checker.py` — Python reference checker
- `test_checker.py` — Python tests
- `software_safe_v1.json` — launch policy pack
- `passing_receipt.json` — passing example
- `failing_receipt_modified_forbidden_file.json` — failing example
- `failing_receipt_tests_failed.json` — failing example
- `axezent_ai_ctr_receipt_v1.schema.json` — receipt schema
- `Cargo.toml`, `lib.rs`, `main.rs` — Rust runtime scaffold
- `GITHUB_WORKFLOW_MAIN.yml` — visible backup workflow

## Commercial / Enterprise Direction

The open-source kernel provides the public verification standard.

Commercial layers can include signed compliance certificates, private audit vaults, enterprise dashboards, custom policy packs, high-throughput streaming integrations, long-term receipt storage, and customer-specific security controls.

Contact: axezentai@Gmail.com

## License

MIT License. See `LICENSE`.
