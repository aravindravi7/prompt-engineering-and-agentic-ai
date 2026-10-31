"""Ask Claude (fresh `claude -p` conversations) about experiment postings and save every reply.

    python3 -m tools.ask_claude --prompt prompts/baseline-v1.txt --split development --out experiment/replies/baseline-v1
    python3 -m tools.ask_claude --prompt prompts/baseline-v1.txt --sampling --repeat 4 --out sampling/replies

Each call is a new conversation with no tools, run in an empty folder. Every reply is saved with its
date, model and validator result, including the rejected ones. A reply file that already exists is
not asked again, so an interrupted batch can be resumed without re-asking.
"""

import argparse
import gzip
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agent import claude_judge
from agent.resume import load_resume

HERE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--split", choices=["development", "held-out"])
    parser.add_argument("--sampling", action="store_true", help="only the 5 sampling postings")
    parser.add_argument("--job", type=int, nargs="+", help="only these posting ids")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    chosen = json.loads((HERE / "experiment" / "postings.json").read_text())
    jobs = {j["id"]: j for j in json.loads(gzip.decompress((HERE / chosen["source"]).read_bytes()))["jobs"]}
    resume = load_resume(HERE / "persona" / "aarav-patel.resume.example.json")
    targets = [p for p in chosen["postings"]
               if (not args.split or p["split"] == args.split) and (not args.sampling or p["sampling"])
               and (not args.job or p["job_id"] in args.job)]
    args.out.mkdir(parents=True, exist_ok=True)
    tasks = [(p, k) for p in targets for k in range(1, args.repeat + 1)
             if not (args.out / ("%s-r%d.json" % (p["job_id"], k))).exists()]

    def ask(task):
        p, k = task
        record = claude_judge.judgment(jobs[p["job_id"]], resume, claude_judge.ask_claude_cli, args.prompt)
        record.update(job_id=p["job_id"], split=p["split"], repeat=k)
        (args.out / ("%s-r%d.json" % (p["job_id"], k))).write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        return "%s r%d %s %s" % (p["job_id"], k, record["status"], record["verdict"] or record["rejected_because"])

    print("asking %d (skipping %d already saved)" % (len(tasks), len(targets) * args.repeat - len(tasks)))
    with ThreadPoolExecutor(args.workers) as pool:
        for line in pool.map(ask, tasks):
            print(" ", line, flush=True)


if __name__ == "__main__":
    main()
