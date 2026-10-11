"""Tool-use test: prompts x repeats, scored by rules fixed in advance."""
import collections
import datetime
import json
import os
import sys
import time
import urllib.request

URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"
DIR = os.path.join("experiments", "tool-use-1b")


def tool(name, desc, props, required):
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object", "properties": props,
                       "required": required}}}


INT2 = {"a": {"type": "integer"}, "b": {"type": "integer"}}
TOOLS = [
    tool("multiply", "Multiply two integers", INT2, ["a", "b"]),
    tool("add", "Add two integers", INT2, ["a", "b"]),
    tool("get_weather", "Get the current weather for a city",
         {"city": {"type": "string"}}, ["city"]),
]


def chat(text, temperature, seed):
    body = {"model": MODEL, "messages": [{"role": "user", "content": text}],
            "tools": TOOLS, "stream": False,
            "options": {"temperature": temperature, "seed": seed}}
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)["message"]


def to_int(v, strict):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if not strict and isinstance(v, str):
        try:
            return int(v.strip())
        except ValueError:
            return None
    return None


def args_ok(given, want, strict):
    if not isinstance(given, dict):
        return False
    a = to_int(given.get("a"), strict)
    b = to_int(given.get("b"), strict)
    if a is None or b is None:
        return False
    return sorted([a, b]) == sorted([want["a"], want["b"]])


def score(p, calls):
    if p["tool"] is None:
        return "ok_no_tool" if not calls else "tool_called_unneeded"
    if not calls:
        return "no_call"
    c = calls[0].get("function", {})
    if c.get("name") != p["tool"]:
        return "wrong_tool"
    g = c.get("arguments")
    if isinstance(g, str):
        try:
            g = json.loads(g)
        except ValueError:
            g = None
    if args_ok(g, p["args"], True):
        return "correct_strict"
    if args_ok(g, p["args"], False):
        return "correct_lenient_only"
    return "wrong_args"


def main():
    repeats = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    temperature = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    with open(os.path.join(DIR, "prompts.json")) as f:
        prompts = json.load(f)[:limit]
    rows = []
    t0 = time.time()
    for p in prompts:
        for r in range(repeats):
            msg = chat(p["text"], temperature, r)
            calls = msg.get("tool_calls") or []
            cat = score(p, calls)
            rows.append({"id": p["id"], "repeat": r, "category": cat,
                         "calls": calls, "content": msg.get("content", "")})
            print(p["id"], r, cat)
    cats = collections.Counter(x["category"] for x in rows)
    groups = {}
    for x in rows:
        groups.setdefault(x["id"][0], collections.Counter())[x["category"]] += 1
    good = ("correct_strict", "ok_no_tool")
    strict = sum(cats[c] for c in good)
    lenient = strict + cats["correct_lenient_only"]
    n = len(rows)
    varied = 0
    for p in prompts:
        seen = {json.dumps(x["calls"], sort_keys=True)
                for x in rows if x["id"] == p["id"]}
        varied += len(seen) > 1
    summary = {
        "calls": n, "prompts": len(prompts), "repeats": repeats,
        "temperature": temperature,
        "strict_pass_pct": round(100 * strict / n, 1),
        "lenient_pass_pct": round(100 * lenient / n, 1),
        "categories": dict(cats),
        "by_group": {k: dict(v) for k, v in groups.items()},
        "prompts_with_varying_repeats": varied,
        "minutes": round((time.time() - t0) / 60, 1),
    }
    print(json.dumps(summary, indent=2))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(DIR, f"results-{stamp}.json")
    with open(path, "w") as f:
        json.dump({"model": MODEL, "summary": summary, "rows": rows}, f, indent=2)
    print("Saved", path)


if __name__ == "__main__":
    main()