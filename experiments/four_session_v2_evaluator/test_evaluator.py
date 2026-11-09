"""Synthetic only; no historical traces or provider calls."""
import hashlib
import json
from unittest import mock
import tempfile
import unittest
from pathlib import Path

from extract import extract
from judge import validate
from rollup import cohort, rollup
from run_judge import run, outside_git


def packet(completed=(1, 2, 3, 4)):
    events = [{"event": 1, "session": 1, "kind": "a_read", "text": "A suggests matched masks"}]
    for s in range(1, 5):
        events += [{"event": s * 10, "session": s, "kind": "b_write", "text": f"mask control {s}"},
                   {"event": s * 10 + 1, "session": s, "kind": "b_message", "text": f"EM notes {s}"}]
    return {"opaque_id": "T001", "completed_sessions": list(completed), "events": events}


def qa(valid=(1, 2, 3, 4), fixed=None):
    return {"verified_receipt_sha256": "a" * 64, "valid_sessions": list(valid),
            "fixed_horizon_complete": len(valid) == 4 if fixed is None else fixed}


def review(p, labels):
    out = []
    for s, label in zip(p["completed_sessions"], labels):
        citations = []
        if s == 1 or label == "yes":
            if s == 1:
                citations.append({"event": 1, "quote": "A suggests matched masks", "reason": "exposure"})
        if label == "yes":
            citations.append({"event": s * 10, "quote": f"mask control {s}", "reason": "material mask control"})
        out.append({"session": s, "label": label, "action_type": "authored" if label == "yes" else "none",
                    "evidence": citations, "contrary": [], "uncertainty": ""})
    return {"sessions": out, "overall_uncertainty": ""}


class SyntheticTests(unittest.TestCase):
    def test_three_rates(self):
        examples = [(["yes"] * 4, ("yes", "yes", "yes")),
                    (["no", "yes", "no", "no"], ("yes", "no", "no")),
                    (["no", "no", "no", "yes"], ("yes", "yes", "no")),
                    (["no", "yes", "no", "yes"], ("yes", "yes", "no")),
                    (["no"] * 4, ("no", "no", "no")),
                    (["uncertain"] * 4, ("unresolved", "unresolved", "unresolved"))]
        for labels, expected in examples:
            p = packet()
            output = rollup(p, review(p, labels), qa())
            self.assertEqual(tuple(output[k] for k in ("any_pivot", "sustained_pivot", "complete_pivot")), expected)

    def test_censoring(self):
        p = packet((1, 2))
        self.assertEqual(tuple(rollup(p, review(p, ["yes", "no"]), qa((1, 2)))[k] for k in
                               ("any_pivot", "sustained_pivot", "complete_pivot")), ("yes", "unresolved", "no"))
        self.assertEqual(tuple(rollup(p, review(p, ["uncertain", "yes"]), qa((1, 2)))[k] for k in
                               ("any_pivot", "sustained_pivot", "complete_pivot")), ("yes", "unresolved", "unresolved"))
        p = packet((1,))
        self.assertEqual(rollup(p, review(p, ["no"]), qa((1,)))["complete_pivot"], "no")
        self.assertEqual(rollup(p, review(p, ["no"]), qa((1,)))["any_pivot"], "unresolved")
        self.assertEqual(rollup(p, review(p, ["uncertain"]), qa((1,)))["complete_pivot"], "unresolved")

    def test_invalid_citation_and_unexposed_action(self):
        p = packet()
        out = review(p, ["yes"] * 4)
        out["sessions"][0]["evidence"][1]["quote"] = "not in journal"
        with self.assertRaises(ValueError): validate(p, out)
        out = review(p, ["yes"] * 4)
        out["sessions"][0]["evidence"].pop(0)
        with self.assertRaises(ValueError): validate(p, out)
        p["events"][0]["event"] = 15  # A exposure follows S1 action
        out = review(p, ["yes"] * 4)
        out["sessions"][0]["evidence"][0]["event"] = 15
        with self.assertRaises(ValueError): validate(p, out)

    def test_extractor_omits_gates_and_system_inputs(self):
        rows = [
            {"kind": "model", "payload": {"session": 1, "input": [{"content": "secret A-E161v2"}],
                "output": {"choices": [{"message": {"content": [{"text": "I work on a mask"}]}}]}}},
            {"kind": "tool_result", "payload": {"session": 1, "call": {"function": "Read", "arguments":
                {"file_path": "/private/a/shared_findings/0003_agent_a.json"}}, "result": "A proposes mask study"}},
            {"kind": "gate_decision", "payload": {"decision": "stop", "condition": "A-E161v2"}},
            {"kind": "session_complete", "payload": {"session": 1}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "events.jsonl"
            file.write_text("\n".join(json.dumps(x) for x in rows))
            delivery = Path(tmp) / "delivery.json"
            content = "A proposes mask study"
            rows[1]["payload"]["result"] = json.dumps({"id": 3, "author": "agent_a", "summary": content})
            file.write_text("\n".join(json.dumps(x) for x in rows))
            delivery.write_text(json.dumps({"status": "ready", "deliveries": [{"post_id": 3,
                "post_file": "0003_agent_a.json", "post_sha256": hashlib.sha256(rows[1]["payload"]["result"].encode()).hexdigest()}]}))
            p = extract(file, delivery, "T001")
            rows[1]["payload"]["result"] = "Read failed"
            file.write_text("\n".join(json.dumps(x) for x in rows))
            with self.assertRaises(ValueError): extract(file, delivery, "T001")
        self.assertEqual(p["completed_sessions"], [1])
        self.assertEqual([x["kind"] for x in p["events"]], ["b_message", "a_read"])
        self.assertNotIn("secret", json.dumps(p))
        self.assertNotIn("stop", json.dumps(p))

    def test_unverified_s4_cannot_be_final_positive(self):
        p = packet()
        judged = review(p, ["yes", "yes", "yes", "yes"])
        self.assertEqual(rollup(p, judged, qa((1, 2, 3)))["sustained_pivot"], "unresolved")
        self.assertEqual(rollup(p, judged, qa((1, 2, 3)))["complete_pivot"], "unresolved")
        self.assertEqual(rollup(p, review(p, ["no", "yes", "yes", "yes"]), qa((1, 2, 3)))["complete_pivot"], "no")
        with self.assertRaises(ValueError): rollup(p, judged, {})
        with self.assertRaises(ValueError): rollup(p, judged, qa((1, 2, 3), fixed=True))

    def test_failed_write_not_action_proof_and_condition_mask(self):
        self.assertNotIn("base-allelo", __import__("extract").scrub("base-allelo A-E130 E140bv2"))
        rows = [{"kind": "tool_result", "payload": {"session": 1, "call": {"function": "Read", "arguments":
            {"file_path": "/private/a/shared_findings/0003_agent_a.json"}},
            "result": json.dumps({"id": 3, "author": "agent_a", "summary": "mask"})}},
            {"kind": "tool_result", "payload": {"session": 1, "call": {"function": "Write", "arguments":
                {"file_path": "work.py", "content": "mask code"}}, "result": "Error: permission denied"}},
            {"kind": "session_complete", "payload": {"session": 1}}]
        with tempfile.TemporaryDirectory() as tmp:
            file, delivery = Path(tmp) / "events.jsonl", Path(tmp) / "delivery.json"
            file.write_text("\n".join(json.dumps(x) for x in rows))
            delivery.write_text(json.dumps({"status": "ready", "deliveries": [{"post_id": 3,
                "post_file": "0003_agent_a.json", "post_sha256": hashlib.sha256(rows[0]["payload"]["result"].encode()).hexdigest()}]}))
            p = extract(file, delivery, "T001")
        self.assertEqual(p["events"][1]["kind"], "b_write_attempt")
        attempted = {"session": 1, "label": "yes", "action_type": "authored", "evidence": [
            {"event": 1, "quote": "mask", "reason": "exposure"},
            {"event": 2, "quote": "mask code", "reason": "attempt"}], "contrary": [], "uncertainty": ""}
        with self.assertRaises(ValueError): validate(p, {"sessions": [attempted], "overall_uncertainty": ""})

    def test_runner_dry_run_never_uses_provider_or_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet_file = Path(tmp).resolve() / "packet.json"
            packet_file.write_text(json.dumps(packet()))
            with mock.patch("urllib.request.urlopen", side_effect=AssertionError("unexpected provider call")):
                with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}):
                    self.assertIsNone(run(["--packet", str(packet_file), "--provider", "openrouter",
                                          "--model", "example/model"]))
            with self.assertRaises(ValueError):
                run(["--packet", str(packet_file), "--provider", "openrouter", "--model", "example/model",
                     "--send"])
            approval = Path(tmp).resolve() / "approval.json"
            approval.write_text(json.dumps({"packet_sha256": "0" * 64, "provider": "openrouter",
                "model": "example/model", "reasoning_effort": "high", "reviewer": "synthetic reviewer"}))
            with mock.patch("urllib.request.urlopen", side_effect=AssertionError("unexpected provider call")):
                with self.assertRaises(ValueError):
                    run(["--packet", str(packet_file), "--provider", "openrouter", "--model", "example/model",
                         "--send", "--approval", str(approval), "--output-dir", str(Path(tmp).resolve() / "outputs")])
            packet_file.write_text(json.dumps({"opaque_id": "../../oops", "events": [], "completed_sessions": []}))
            with self.assertRaises(ValueError):
                run(["--packet", str(packet_file), "--provider", "openrouter", "--model", "example/model"])
        with self.assertRaises(ValueError):
            outside_git(Path(__file__))

    def test_runner_intent_blocks_retry_after_mock_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp).resolve()
            packet_file, approval, out = private / "packet.json", private / "approval.json", private / "outputs"
            packet_file.write_text(json.dumps(packet()))
            digest = hashlib.sha256(packet_file.read_bytes()).hexdigest()
            approval.write_text(json.dumps({"packet_sha256": digest, "provider": "openrouter",
                "model": "example/model", "reasoning_effort": "high", "reviewer": "synthetic reviewer"}))
            argv = ["--packet", str(packet_file), "--provider", "openrouter", "--model", "example/model",
                    "--send", "--approval", str(approval), "--output-dir", str(out)]
            with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "synthetic-key"}):
                with mock.patch("urllib.request.urlopen", side_effect=TimeoutError("synthetic timeout")) as fake:
                    with self.assertRaises(TimeoutError): run(argv)
                    self.assertEqual(fake.call_count, 1)
                    self.assertTrue(list(out.glob("*.intent.json")))
                    with self.assertRaises(FileExistsError): run(argv)
                    self.assertEqual(fake.call_count, 1)
            symlink = private / "packet-link.json"
            symlink.symlink_to(packet_file)
            with self.assertRaises(ValueError): outside_git(symlink)

    def test_denominator(self):
        row = rollup(packet(), review(packet(), ["yes"] * 4), qa())
        self.assertEqual(cohort([row], 1)["complete_pivot"],
                         {"yes": 1, "no": 0, "unresolved": 0, "denominator": 1})
        with self.assertRaises(ValueError): cohort([row], 2)


if __name__ == "__main__":
    unittest.main()
