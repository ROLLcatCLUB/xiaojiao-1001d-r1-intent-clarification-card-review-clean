from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path


STAGE = "1001D_R1_INTENT_CLARIFICATION_CARD_FIXTURE"
FINAL = "XIAOJIAO_INTENT_CLARIFICATION_CARD_FIXTURE_PASS"
SLUG = "xiaojiao_intent_clarification_card_fixture_1001D_R1"
MARKER = "ALL_1001D_R1_INTENT_CLARIFICATION_CARD_FIXTURE_CHECKS_OK"
REQ_CASES = {
    "ambiguous_this_object",
    "handout_do_that",
    "lesson_handle_this",
    "revise_second_section",
    "same_style_preference",
}
REQ_CARD_TYPES = {"inline_chips", "small_card", "parameter_drawer"}
REQ_REGISTRIES = {
    "intent_registry",
    "utterance_pattern_registry",
    "clarification_card_registry",
    "context_pack_policy_registry",
    "preference_candidate_registry",
    "observation_metric_registry",
}
BAD_PARTS = [".env", "token", "secret", "node_modules", "__pycache__", ".db", ".sqlite", "student_data", "provider_raw"]
REQ_FILES = [
    "docs/audit/xiaojiao_state_driven_intelligence_engine_end_to_end_dry_run_1001G_result.json",
    "docs/audit/xiaojiao_intent_parser_and_fallback_rule_fixture_1001D_review_decision.json",
    f"docs/foundation/{SLUG}.md",
    f"docs/foundation/{SLUG}.json",
    f"samples/{SLUG}/intent_clarification_card_fixture_1001D_R1.json",
    f"docs/audit/{SLUG}_result.json",
    f"docs/audit/{SLUG}_report.md",
    f"docs/audit/{SLUG}_checklist.json",
    f"docs/audit_packages/{SLUG}_manifest.json",
    f"scripts/validate_{SLUG}.py",
]


def fail(message: str) -> None:
    raise SystemExit(f"VALIDATION_FAILED: {message}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]

    for rel in REQ_FILES:
        if not (root / rel).exists():
            fail(f"missing required file: {rel}")

    g_result = load_json(root / "docs/audit/xiaojiao_state_driven_intelligence_engine_end_to_end_dry_run_1001G_result.json")
    d_decision = load_json(root / "docs/audit/xiaojiao_intent_parser_and_fallback_rule_fixture_1001D_review_decision.json")
    contract = load_json(root / f"docs/foundation/{SLUG}.json")
    fixture = load_json(root / f"samples/{SLUG}/intent_clarification_card_fixture_1001D_R1.json")
    result = load_json(root / f"docs/audit/{SLUG}_result.json")
    manifest = load_json(root / f"docs/audit_packages/{SLUG}_manifest.json")

    if g_result.get("final_status") != "XIAOJIAO_STATE_DRIVEN_INTELLIGENCE_ENGINE_END_TO_END_DRY_RUN_PASS":
        fail("1001G source gate not passed")
    if d_decision.get("review_decision") != "ACCEPT":
        fail("1001D review decision not accepted")
    if contract.get("stage_code") != STAGE or contract.get("stage_type") != "intent_clarification_card_fixture_only":
        fail("contract identity mismatch")
    if result.get("stage_code") != STAGE or result.get("final_status") != FINAL:
        fail("result identity mismatch")
    if result.get("pass") is not True or result.get("marker") != MARKER:
        fail("result pass/marker mismatch")
    if fixture.get("stage_code") != STAGE or fixture.get("fixture_type") != "static_intent_clarification_card_fixture_only":
        fail("fixture identity mismatch")
    if contract.get("next_stage") != "1001D_R1_REVIEW_PENDING_BEFORE_1000F":
        fail("next stage mismatch")

    for key, value in contract.get("hard_boundaries", {}).items():
        if value is not False:
            fail(f"hard boundary must be false: {key}")
    for key, value in fixture.get("boundary_flags", {}).items():
        if value is not False:
            fail(f"fixture boundary must be false: {key}")
    for key, value in result.get("boundary_flags", {}).items():
        if value is not False:
            fail(f"result boundary must be false: {key}")

    registries = fixture.get("baseline_registries", {})
    if set(registries.keys()) != REQ_REGISTRIES:
        fail("baseline registry set mismatch")

    cases = fixture.get("cases", [])
    if {case.get("case_id") for case in cases} != REQ_CASES:
        fail("required cases mismatch")
    seen_card_types = set()
    for case in cases:
        cid = case.get("case_id")
        card = case.get("clarification_card", {})
        confirmed = case.get("confirmed_intent", {})
        options = card.get("options", [])
        seen_card_types.add(card.get("card_type"))
        if len(options) < 2 or len(options) > 4:
            fail(f"{cid} option count out of range")
        if not case.get("teacher_selected_option_id"):
            fail(f"{cid} missing teacher selection")
        if case.get("teacher_selected_option_id") not in {opt.get("option_id") for opt in options}:
            fail(f"{cid} selected option not in card")
        if confirmed.get("confidence") != 1.0:
            fail(f"{cid} confirmed confidence must be 1.0")
        if confirmed.get("source") != "clarification_card_selection":
            fail(f"{cid} confirmed source mismatch")
        if not confirmed.get("intent") or not confirmed.get("target_object") or not confirmed.get("action_gate"):
            fail(f"{cid} confirmed intent missing required fields")
        if case.get("token_cost") != 0 or case.get("model_call_executed") is not False:
            fail(f"{cid} must stay zero-token and no model execution")
        if cid == "same_style_preference" and confirmed.get("memory_write_required") is not False:
            fail("preference case must not write memory")

    if seen_card_types != REQ_CARD_TYPES:
        fail("required card types not covered")

    zip_path = root / f"docs/audit_packages/{SLUG}.zip"
    if not zip_path.exists():
        fail("missing package zip")
    with zipfile.ZipFile(zip_path) as zf:
        entries = zf.namelist()
    for entry in entries:
        normalized = entry.replace("\\", "/")
        if normalized.startswith("/") or "\\" in entry or ":" in normalized:
            fail(f"unsafe ZIP path: {entry}")
        if any(part in normalized.lower() for part in BAD_PARTS):
            fail(f"forbidden ZIP entry: {entry}")
    if manifest.get("manifest_minus_zip") != [] or manifest.get("zip_minus_manifest") != []:
        fail("manifest alignment not empty")
    if sorted(manifest.get("zip_entries", [])) != sorted(entries):
        fail("manifest zip entries mismatch")

    print(MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
