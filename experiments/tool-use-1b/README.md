# Tool-use reliability of Llama 3.2 1B (3 tools)

## Question
Does Llama 3.2 1B choose the right tool, with the right arguments, and decline to use a tool when none is needed?

## Method
- Model: `llama3.2:1b` (Ollama 0.40.2, model ID baf6a787fdff)
- Tools: `multiply`, `add`, `get_weather` (distractor, never correct)
- 30 prompts written in advance (`prompts.json`): 10 multiply, 10 add, 10 needing no tool
- 5 samples per prompt (seeds 0 to 4), temperature 0, 150 calls
- Only the first tool call is scored
- Scoring rules fixed before the run (`tools/tool_test.py`):
  strict = integer arguments; lenient = numeric strings accepted

## Environment
- Intel Core i7-7600U, 16 GiB installed (15.88 GiB usable), no GPU
- Windows 10 (build 19045), Python 3.13.16
- Plugged in, Windows "Better performance" mode
- MetaTrader 5 and a browser were opened partway through the run

## Results (150 calls)
| Rule | Pass rate |
|---|---|
| Strict | 30.0% (45/150) |
| Lenient | 56.7% (85/150) |

| Group | Result |
|---|---|
| multiply | 50/50 right tool and numbers (15 strict, 35 as strings) |
| add | 30/50 correct; 20 called `multiply` instead |
| no tool needed | 5/50 correct; 45 called a tool (30 `get_weather`, 15 `multiply`) |

Raw data: `results-20261011-214853.json`

## Limits
- The 20 add failures come from 4 prompts (a04, a06, a08, a09) that failed on all 5 samples. Effective sample size is 30 prompts.
- Cause of the failures not identified.
- One model, one machine, one prompt set written by me.
- Timing not reported because the machine was in normal use.
- Only the first tool call is scored.

## Reproduce
1. `ollama pull llama3.2:1b`, then `pip install psutil`
2. `python tools\tool_test.py 5 0 30`

## Run 2: reworded `add` description

Same model, prompts, seeds, temperature and scorer as run 1. Only one thing changed: the `add` tool description, in `tools/tool_test_v2.py`.

- Run 1 (original description "Add two integers"): `results-20261011-214853.json`
- Run 2 (new description "Add two integers together. Use for plus, sum, total and addition. Do not use for multiplication."): `results-20261012-020332.json`

| | Run 1 | Run 2 |
|---|---|---|
| Strict pass | 30.0% (45/150) | 32.7% (49/150) |
| Lenient pass | 56.7% (85/150) | 70.0% (105/150) |
| add group correct | 30/50 | 50/50 |
| add group `wrong_tool` | 20 | 0 |
| no-tool group correct | 5/50 | 5/50 |

Conditions for run 2: plugged in, Windows "Better performance" mode, apps closed, sleep set to Never, laptop left alone apart from one mistyped command near the end. Timing is not reported.

What it shows:
- The 4 addition prompts that failed in run 1 (a04, a06, a08, a09) passed in run 2.
- The model still called a tool on 45 of 50 questions that needed none, so that failure is separate.
- Strict pass barely moved, because numbers still mostly arrive as strings.

Limits:
- I changed two things in one sentence (more detail, and "do not use for multiplication"). I did not test them separately, so I cannot say which mattered.
- Effective sample size is still 30 prompts. One model, one machine, one prompt set.
## Runs 3 and 4: token cap, then system message

Two earlier attempts at run 4 crashed with `TimeoutError` after a call got no reply for 600 seconds. They saved nothing and are not in the results. The cause was not identified. One stalled on prompt n04. After that, `tools/tool_test_v3.py` and `tools/tool_test_v3_base.py` use a 120-second timeout and a cap of 300 generated tokens per answer (`num_predict`).

- Baseline: run 2's `add` description plus the 300-token cap, no system message (`tools/tool_test_v3_base.py`): `results-20261013-044244.json`
- v3: the same, plus a system message (`tools/tool_test_v3.py`): `results-20261013-114941.json`

System message: "If the question can be answered without a tool, answer directly. Only use a tool for arithmetic or weather."

| | Run 2 (no cap) | Baseline (cap) | v3 (cap + system message) |
|---|---|---|---|
| Strict pass | 32.7% | 32.7% | 40.0% |
| Lenient pass | 70.0% | 70.0% | 66.7% |
| multiply group correct | 50/50 | 50/50 | 50/50 |
| add group correct | 50/50 | 50/50 | 50/50 |
| no-tool group correct | 5/50 | 5/50 | 0/50 |

What it shows:
- The 300-token cap did not change any scored category (baseline matches run 2).
- The system message did not stop the model calling a tool on questions that needed none. It called one on all 50 no-tool calls.
- Strict pass rose because numbers arrived as integers more often (60 strict-correct against 44), not because of better reasoning. I did not test why.
- Lenient pass fell only because the 5 correct no-tool calls became failures.

Conditions: the baseline started on battery and was plugged in partway through. The v3 run was plugged in, with other apps closed and the laptop left alone, apart from one message sent just after it started. Pass rates reported, timing not reported.

Limits:
- 5/50 to 0/50 is a small change on 10 prompts. The safe claim is that the system message did not help.
- One system message wording, one model, one machine, one prompt set. Other wordings were not tested.
- Only the first tool call is scored.