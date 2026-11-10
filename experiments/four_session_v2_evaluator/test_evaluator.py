"""Synthetic only; no historical traces or provider calls."""
import hashlib
import io
import json
import threading
from unittest import mock
import tempfile
import unittest
from pathlib import Path

from extract import extract
from judge import validate
from rollup import cohort, rollup
from run_judge import run, outside_git, PROMPT_SHA256
import historical
import historical_batch
import launch_judge


def packet(completed=(1, 2, 3, 4)):
    events = [{"event": 1, "session": 1, "kind": "a_read", "text": "A suggests matched masks"}]
    for s in range(1, 5):
        events += [{"event": s * 10, "session": s, "kind": "b_write", "target": "file", "text": f"mask control {s}"},
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
                citations.append({"event": 1, "reason": "A shared finding Read"})
        if label == "yes":
            citations.append({"event": s * 10, "reason": "material mask control"})
        out.append({"session": s, "label": label,
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
        out["sessions"][0]["evidence"][1]["event"] = 999  # invented citation
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

    def test_zero_completed_is_qa_only_unresolved(self):
        empty = {"opaque_id": "T001", "completed_sessions": [], "events": []}
        disposition = {"verified_receipt_sha256": "a" * 64, "valid_sessions": [],
                       "fixed_horizon_complete": False, "interruption_reason": "technical interruption before S1"}
        result = rollup(empty, None, disposition)
        self.assertEqual(tuple(result[k] for k in ("any_pivot", "sustained_pivot", "complete_pivot")),
                         ("unresolved", "unresolved", "unresolved"))
        self.assertEqual(cohort([result], 1)["sustained_pivot"]["unresolved"], 1)
        with self.assertRaises(ValueError): rollup(empty, {"sessions": [], "overall_uncertainty": ""}, disposition)
        with self.assertRaises(ValueError): rollup(empty, None, {**disposition, "interruption_reason": ""})
        # A superseded preparation attempt has no separate counted-run ID;
        # cohort uniqueness and declared-count checks still apply.
        with self.assertRaises(ValueError): cohort([result, result], 2)

    def test_s4_forum_promise_cannot_anchor_final_positive(self):
        p = packet()
        p["events"].append({"event": 49, "session": 4, "kind": "b_forum_post", "text": "I will test the mask later"})
        judged = review(p, ["no", "no", "no", "yes"])
        judged["sessions"][3]["evidence"] = [{"event": 49, "reason": "future plan"}]
        with self.assertRaises(ValueError): rollup(p, judged, qa())
        judged["sessions"][3]["evidence"] = [{"event": 40, "reason": "authored S4 mask control"}]
        self.assertEqual(rollup(p, judged, qa())["sustained_pivot"], "yes")

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
        attempted = {"session": 1, "label": "yes", "evidence": [
            {"event": 1, "reason": "verified A exposure"},
            {"event": 2, "reason": "failed Write attempt"}], "contrary": [], "uncertainty": ""}
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
            approval.write_text(json.dumps({"packet_sha256": digest, "prompt_sha256": PROMPT_SHA256, "provider": "openrouter",
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

    def test_single_judge_saves_raw_before_invalid_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet_file, approval, out = root / "T001.json", root / "approval.json", root / "responses"
            packet_file.write_text(json.dumps(packet()))
            approval.write_text(json.dumps({"packet_sha256": hashlib.sha256(packet_file.read_bytes()).hexdigest(),
                "prompt_sha256": PROMPT_SHA256, "provider": "openrouter", "model": "synthetic/model",
                "reasoning_effort": "high", "reviewer": "synthetic reviewer"}))
            class Response(io.BytesIO):
                status = 200
            invalid = {"output": [{"type": "message", "content": [
                {"type": "output_text", "text": json.dumps({"sessions": []})}]}]}
            argv = ["--packet", str(packet_file), "--provider", "openrouter", "--model", "synthetic/model",
                    "--send", "--approval", str(approval), "--output-dir", str(out)]
            with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "synthetic-key"}):
                with mock.patch("urllib.request.urlopen", return_value=Response(json.dumps(invalid).encode())) as fake:
                    with self.assertRaises(ValueError): run(argv)
                    self.assertEqual(fake.call_args.kwargs["timeout"], 600)
                    self.assertEqual(len(list(out.glob("*.raw.json"))), 1)
                    self.assertEqual(len(list(out.glob("*.intent.json"))), 1)
                    self.assertEqual(len(list(out.glob("T001-*.json"))), 2)
                    with self.assertRaises(FileExistsError): run(argv)
                    self.assertEqual(fake.call_count, 1)

    def test_detached_launcher_mock_and_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet_file, approval, out = root / "T001.json", root / "approval.json", root / "responses"
            packet_file.write_text(json.dumps(packet()))
            approval.write_text(json.dumps({"packet_sha256": hashlib.sha256(packet_file.read_bytes()).hexdigest(),
                "prompt_sha256": PROMPT_SHA256, "provider": "openrouter", "model": "synthetic/model",
                "reasoning_effort": "high", "reviewer": "synthetic reviewer"}))
            argv = ["--packet", str(packet_file), "--provider", "openrouter", "--model", "synthetic/model",
                    "--approval", str(approval), "--output-dir", str(out), "--send"]
            with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "synthetic-key"}):
                with mock.patch.object(launch_judge, "outside_git", side_effect=lambda x: x.resolve()):
                    with mock.patch.object(launch_judge.subprocess, "Popen") as spawned:
                        spawned.return_value.pid = 4242
                        self.assertEqual(launch_judge.main(argv), 4242)
                        self.assertTrue(spawned.call_args.kwargs["start_new_session"])
                        self.assertEqual(spawned.call_args.kwargs["env"]["OPENROUTER_API_KEY"], "synthetic-key")
                        self.assertEqual(len(list(out.glob("*.launcher.log"))), 1)
                        with self.assertRaises(FileExistsError): launch_judge.main(argv)
                        self.assertEqual(spawned.call_count, 1)

    def test_extractor_optional_all_observed_sessions(self):
        rows = [{"kind": "session_complete", "payload": {"session": s}} for s in range(1, 7)]
        with tempfile.TemporaryDirectory() as tmp:
            file, delivery = Path(tmp) / "events.jsonl", Path(tmp) / "delivery.json"
            file.write_text("\n".join(json.dumps(x) for x in rows))
            delivery.write_text(json.dumps({"status": "ready", "deliveries": []}))
            self.assertEqual(extract(file, delivery, "T001")["completed_sessions"], [1, 2, 3, 4])
            self.assertEqual(extract(file, delivery, "T001", max_sessions=50)["completed_sessions"], [1, 2, 3, 4, 5, 6])

    def test_historical_event_ids_and_observed_endpoint(self):
        p = packet((1, 2, 3, 4))
        p["completed_sessions"] = [1, 2, 3, 4, 5, 6]
        p["events"] += [{"event": 50, "session": 5, "kind": "b_write", "target": "file", "text": "mask study"},
                        {"event": 60, "session": 6, "kind": "b_write", "target": "file", "text": "EM only"}]
        for event in p["events"]:
            if event["kind"] == "b_write":
                event["target"] = "file"
        rows = [{"session": s, "label": "yes" if s in (3, 4, 5) else "no",
                 "evidence": ([{"event": 1, "reason": "A Read"}] if s == 1 else []) +
                    ([{"event": s * 10, "reason": "B's direct mask comparison"}] if s in (3, 4, 5) else []),
                 "contrary": [], "uncertainty": ""} for s in range(1, 7)]
        judged = {"sessions": rows, "overall_uncertainty": ""}
        historical.validate(p, judged)
        qa_h = {"verified_receipt_sha256": "f" * 64, "valid_sessions": [1, 2, 3, 4, 5, 6],
                "observed_endpoint_confirmed": True}
        out = historical.rollup(p, judged, qa_h)
        self.assertEqual((out["partial"], out["sustained"], out["complete"]), ("yes", "no", "no"))
        self.assertEqual(out["observed_sessions"], 6)
        judged["sessions"][2]["evidence"][0]["event"] = 20  # wrong session event
        with self.assertRaises(ValueError): historical.validate(p, judged)

    def test_historical_forum_only_positive_fails_closed(self):
        p = {"completed_sessions": [1], "events": [
            {"event": 1, "session": 1, "kind": "a_read", "text": "A mask study"},
            {"event": 2, "session": 1, "kind": "b_forum_post", "text": "I will do it later"}]}
        judged = {"sessions": [{"session": 1, "label": "yes", "evidence": [
            {"event": 1, "reason": "Read"}, {"event": 2, "reason": "promise"}],
            "contrary": [], "uncertainty": ""}], "overall_uncertainty": ""}
        with self.assertRaises(ValueError): historical.validate(p, judged)
        with self.assertRaises(ValueError): validate(p, judged)

    def test_historical_batch_default_is_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "packets").mkdir()
            prompt = b"Synthetic judge prompt"
            (root / "prompt.txt").write_bytes(prompt)
            hashes = {}
            for n in range(100, 160):
                ident = f"T{n}"
                payload = json.dumps({"opaque_id": ident, "completed_sessions": [1], "events": []}).encode()
                (root / "packets" / f"{ident}.json").write_bytes(payload)
                hashes[ident] = hashlib.sha256(payload).hexdigest()
            (root / "manifest.json").write_text(json.dumps({"packet_count": 60,
                "packet_sha256": hashes, "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
                "model": "synthetic/model", "provider": "openrouter", "endpoint": historical_batch.URL,
                "reasoning": {"effort": "high"}}))
            with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network forbidden")):
                self.assertIsNone(historical_batch.main(["--root", str(root)]))
                with self.assertRaises(ValueError): historical_batch.main(["--root", str(root), "--send"])
            self.assertFalse((root / "responses").exists())

    def test_historical_batch_mock_60_one_shot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "packets").mkdir()
            prompt = b"Synthetic prompt only"
            (root / "prompt.txt").write_bytes(prompt)
            hashes = {}
            for n in range(100, 160):
                ident = f"T{n}"
                payload = json.dumps({"opaque_id": ident, "completed_sessions": [1], "events": [
                    {"event": 1, "session": 1, "kind": "a_read", "text": "A mask study"},
                    {"event": 2, "session": 1, "kind": "b_write", "target": "file", "text": "mask builder"}]}).encode()
                (root / "packets" / f"{ident}.json").write_bytes(payload)
                hashes[ident] = hashlib.sha256(payload).hexdigest()
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"packet_count": 60, "packet_sha256": hashes,
                "prompt_sha256": hashlib.sha256(prompt).hexdigest(), "model": "synthetic/model",
                "provider": "openrouter", "endpoint": historical_batch.URL, "reasoning": {"effort": "high"}}))
            digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
            approval = root / "approval.json"
            approval.write_text(json.dumps({"manifest_sha256": digest, "approved": True, "reviewer": "synthetic"}))
            calls = []
            lock = threading.Lock()
            class MockResponse(io.BytesIO):
                status = 200
            def fake_urlopen(request, timeout):
                sent = json.loads(request.data)
                ident = json.loads(sent["input"][1]["content"])["opaque_id"]
                with lock: calls.append(ident)
                judged = {"sessions": [{"session": 1, "label": "yes", "evidence": [
                    {"event": 1, "reason": "A Read"}, {"event": 2, "reason": "mask builder"}],
                    "contrary": [], "uncertainty": ""}], "overall_uncertainty": ""}
                body = {"output": [{"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps(judged)}]}], "usage": {"input_tokens": 1}}
                return MockResponse(json.dumps(body).encode())
            argv = ["--root", str(root), "--send", "--approval", str(approval)]
            with mock.patch.dict("os.environ", {"OPENROUTER_API_KEY": "synthetic-key"}):
                with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                    result = historical_batch.main(argv)
                    self.assertEqual(result["states"], {"validated_event_ids": 60})
                    self.assertEqual(len(calls), 60)
                    with self.assertRaises(FileExistsError): historical_batch.main(argv)
                    self.assertEqual(len(calls), 60)
            batch = root / "responses" / digest
            self.assertEqual(len(list(batch.glob("T*/intent.json"))), 60)
            self.assertEqual(len(list(batch.glob("T*/raw.json"))), 60)

    def test_denominator(self):
        row = rollup(packet(), review(packet(), ["yes"] * 4), qa())
        self.assertEqual(cohort([row], 1)["complete_pivot"],
                         {"yes": 1, "no": 0, "unresolved": 0, "denominator": 1})
        with self.assertRaises(ValueError): cohort([row], 2)


if __name__ == "__main__":
    unittest.main()
