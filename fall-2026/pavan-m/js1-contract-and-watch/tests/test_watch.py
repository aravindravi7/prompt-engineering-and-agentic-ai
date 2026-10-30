import json
from agent.watch import run_watch


def write_fake_response(path, ids):
    """Write a tiny fake Greenhouse response with the given posting ids."""
    data = {
        "jobs": [{"id": i, "title": f"Job {i}"} for i in ids],
        "meta": {"total": len(ids)},
    }
    path.write_text(json.dumps(data))


def test_first_run_baseline_reports_zero_new_postings(tmp_path):
    # Setup: a saved response with 3 postings, and NO state file yet
    seeded = tmp_path / "response.json"
    write_fake_response(seeded, [1, 2, 3])
    state_path = tmp_path / "state.json"
    evidence_dir = tmp_path / "evidence"

    # Run the watch once
    result = run_watch(state_path, evidence_dir, seeded_file=seeded)

    # TODO 1: check that this run was marked as a baseline
    assert result["baseline"] is True

    # TODO 2: check that no postings were reported as new
    assert result["new_ids"] == []

    # TODO 3: open the state file and check it now remembers ids 1, 2, 3
    state = json.loads(state_path.read_text())
    assert set(state["seen_ids"]) == {1, 2, 3}