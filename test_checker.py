from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKER_PATH = ROOT / "axezent_ctr_checker.py"
spec = importlib.util.spec_from_file_location("axezent_ctr_checker", CHECKER_PATH)
checker = importlib.util.module_from_spec(spec)
assert spec.loader is not None
import sys
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


def load_json(rel: str):
    with (ROOT / rel).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def test_passing_receipt_accepts():
    receipt = load_json("passing_receipt.json")
    policy = load_json("software_safe_v1.json")
    report = checker.verify_receipt(receipt, policy)
    assert report.result == "ACCEPT"
    assert report.errors == ()


def test_forbidden_file_receipt_rejects():
    receipt = load_json("failing_receipt_modified_forbidden_file.json")
    policy = load_json("software_safe_v1.json")
    report = checker.verify_receipt(receipt, policy)
    assert report.result == "REJECT"
    assert any("forbidden path" in err or "undeclared file" in err for err in report.errors)


def test_failed_tests_receipt_rejects():
    receipt = load_json("failing_receipt_tests_failed.json")
    policy = load_json("software_safe_v1.json")
    report = checker.verify_receipt(receipt, policy)
    assert report.result == "REJECT"
    assert any("test_run exit_code" in err for err in report.errors)
