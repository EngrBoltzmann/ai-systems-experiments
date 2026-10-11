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