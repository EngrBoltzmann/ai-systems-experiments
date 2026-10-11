"""Repeat an Ollama generation test and record eval rate per run."""
import datetime
import json
import os
import statistics
import sys
import urllib.request

import psutil

URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"
PROMPT = "Explain what a CPU cache is in three sentences."
OUT_DIR = os.path.join("experiments", "ollama-1b-speed")


def run_once():
    body = json.dumps({
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False,
        "options": {"temperature": 0, "seed": 0},
    }).encode()
    req = urllib.request.Request(
        URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        d = json.load(resp)
    freq = psutil.cpu_freq()
    return {
        "eval_count": d["eval_count"],
        "eval_rate_tps": round(d["eval_count"] / d["eval_duration"] * 1e9, 2),
        "load_s": round(d.get("load_duration", 0) / 1e9, 3),
        "cpu_mhz_after": round(freq.current) if freq else None,
    }


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print("Warm-up run (not counted)...")
    run_once()
    runs = []
    for i in range(1, n + 1):
        r = run_once()
        runs.append(r)
        print(i, r)
    rates = [r["eval_rate_tps"] for r in runs]
    summary = {
        "n": n,
        "median": round(statistics.median(rates), 2),
        "mean": round(statistics.mean(rates), 2),
        "stdev": round(statistics.stdev(rates), 2) if n > 1 else None,
        "min": min(rates),
        "max": max(rates),
    }
    print(summary)
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(OUT_DIR, f"results-{stamp}.json")
    with open(path, "w") as f:
        json.dump(
            {"model": MODEL, "prompt": PROMPT, "summary": summary, "runs": runs},
            f,
            indent=2,
        )
    print("Saved", path)


if __name__ == "__main__":
    main()