#!/usr/bin/env python3
"""Axezent AI CTR reference checker.

This checker validates finite AI-agent trace receipts against deterministic policy
packs. It deliberately makes a narrow claim: ACCEPT means the submitted receipt
obeys the declared policy rules implemented here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

Receipt = Dict[str, Any]
Policy = Dict[str, Any]

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SCHEMA = "AXEZENT-AI-CTR-RECEIPT-v1"
EXPECTED_TRUTH_LABEL = "BOUNDED_AI_TRACE_POLICY_CHECK"


@dataclass(frozen=True)
class CheckReport:
    result: str
    errors: Tuple[str, ...]
    warnings: Tuple[str, ...]
    receipt_sha256: str

    def to_json(self) -> Dict[str, Any]:
        return {
            "engine": "Axezent AI CTR reference checker",
            "result": self.result,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "receipt_sha256": self.receipt_sha256,
            "truth_boundary": "finite deterministic receipt under declared policy pack",
        }


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.match(value))


def path_is_forbidden(path: str, forbidden_prefixes: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/").lstrip("/")
    for prefix in forbidden_prefixes:
        p = prefix.replace("\\", "/").lstrip("/")
        if normalized == p or normalized.startswith(p):
            return True
    return False


def step_hash_fields(step: Dict[str, Any]) -> Iterable[Tuple[str, Any]]:
    for key, value in step.items():
        if key.endswith("sha256"):
            yield key, value


def verify_receipt(receipt: Receipt, policy: Policy) -> CheckReport:
    errors: List[str] = []
    warnings: List[str] = []

    receipt_hash = sha256_json(receipt)

    if receipt.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"schema must be {EXPECTED_SCHEMA}")

    if receipt.get("truth_label") != EXPECTED_TRUTH_LABEL:
        errors.append(f"truth_label must be {EXPECTED_TRUTH_LABEL}")

    task = receipt.get("task", {})
    if not isinstance(task, dict):
        errors.append("task must be an object")
        task = {}

    allowed_write_paths = set(task.get("allowed_write_paths", []))
    if not allowed_write_paths:
        warnings.append("task.allowed_write_paths is empty")

    trace_steps = receipt.get("trace_steps", [])
    if not isinstance(trace_steps, list) or not trace_steps:
        errors.append("trace_steps must be a non-empty list")
        trace_steps = []

    forbidden_prefixes = policy.get("forbidden_path_prefixes", [])
    allowed_step_kinds = set(policy.get("allowed_step_kinds", []))
    allow_network = bool(policy.get("allow_network_access", False))
    tests_required = bool(policy.get("tests_required", False))

    saw_passing_test = False
    previous_step_id = 0

    for index, step in enumerate(trace_steps):
        if not isinstance(step, dict):
            errors.append(f"trace_steps[{index}] must be an object")
            continue

        step_id = step.get("step_id")
        if not isinstance(step_id, int) or step_id <= previous_step_id:
            errors.append(f"trace_steps[{index}].step_id must be a strictly increasing positive integer")
        if isinstance(step_id, int):
            previous_step_id = step_id

        kind = step.get("kind")
        if not isinstance(kind, str):
            errors.append(f"trace_steps[{index}].kind must be a string")
            continue

        if allowed_step_kinds and kind not in allowed_step_kinds:
            errors.append(f"trace_steps[{index}] has disallowed kind: {kind}")

        target = step.get("target")
        if isinstance(target, str):
            if path_is_forbidden(target, forbidden_prefixes):
                errors.append(f"trace_steps[{index}] touched forbidden path: {target}")

        if kind == "file_write":
            if not isinstance(target, str):
                errors.append(f"trace_steps[{index}] file_write missing target")
            elif target not in allowed_write_paths:
                errors.append(f"trace_steps[{index}] modified undeclared file: {target}")

        if kind == "network_access" and not allow_network:
            errors.append(f"trace_steps[{index}] network access is not allowed")

        if kind == "test_run":
            if step.get("exit_code") == 0:
                saw_passing_test = True
            else:
                errors.append(f"trace_steps[{index}] test_run exit_code was not 0")

        for key, value in step_hash_fields(step):
            if not is_sha256(value):
                errors.append(f"trace_steps[{index}].{key} must be lowercase hex SHA-256")

    if tests_required and not saw_passing_test:
        errors.append("policy requires at least one passing test_run step")

    final_answer = receipt.get("final_answer", {})
    if not isinstance(final_answer, dict):
        errors.append("final_answer must be an object")
        final_answer = {}

    required_claim = policy.get("required_final_claimed_result")
    if required_claim and final_answer.get("claimed_result") != required_claim:
        errors.append(f"final_answer.claimed_result must be {required_claim}")

    result = "ACCEPT" if not errors else "REJECT"
    return CheckReport(result=result, errors=tuple(errors), warnings=tuple(warnings), receipt_sha256=receipt_hash)


def cmd_verify(args: argparse.Namespace) -> int:
    receipt = load_json(args.receipt)
    policy = load_json(args.policy)
    report = verify_receipt(receipt, policy)

    if args.json:
        print(json.dumps(report.to_json(), indent=2, sort_keys=True))
    else:
        print(report.result)
        if report.errors:
            for error in report.errors:
                print(f"ERROR: {error}")
        if report.warnings:
            for warning in report.warnings:
                print(f"WARNING: {warning}")
        print(f"receipt_sha256={report.receipt_sha256}")

    expected = receipt.get("checker_expectation", {}).get("expected_result")
    if expected and expected != report.result:
        print(f"EXPECTATION_MISMATCH: expected {expected}, got {report.result}", file=sys.stderr)
        return 2

    return 0 if report.result == "ACCEPT" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Axezent AI CTR reference checker")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="verify a receipt against a policy pack")
    verify.add_argument("receipt", help="path to receipt JSON")
    verify.add_argument("--policy", required=True, help="path to policy pack JSON")
    verify.add_argument("--json", action="store_true", help="emit JSON report")
    verify.set_defaults(func=cmd_verify)
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
