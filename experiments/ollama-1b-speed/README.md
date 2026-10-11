# Llama 3.2 1B generation speed on a 2-core laptop CPU

## Question
How many tokens per second does Llama 3.2 1B generate on an i7-7600U with no GPU?

## Method
- Model: `llama3.2:1b` (Ollama model ID baf6a787fdff, 1.3 GB)
- Prompt: "Explain what a CPU cache is in three sentences."
- Settings: temperature 0, seed 0, non-streaming API call
- 1 warm-up run (not counted), then 20 counted runs
- Speed = eval_count / eval_duration, as reported by Ollama
- Script: `tools/bench_ollama.py`

## Environment
- CPU: Intel Core i7-7600U @ 2.80 GHz (2 physical cores, 4 logical)
- RAM: 16 GiB installed (15.88 GiB usable)
- GPU: none used (Intel HD 620)
- OS: Windows 10 (build 19045)
- Python 3.13.16, psutil 7.2.2
- Ollama 0.40.2
- Power: plugged in, battery at 100%, Windows "Better performance" mode
- Other apps closed before the run. An unidentified app named Flow
  may have been open.

## Runs
- Counted runs: 20
- Raw per-run data: `results-20261011-133022.json`

## Results (tokens per second)
| Median | Mean | Std dev | Min | Max |
|---|---|---|---|---|
| 17.02 | 17.12 | 0.25 | 16.83 | 17.50 |

## Limits
- One model, one prompt, one machine, one session.
- Earlier manual runs through the command line gave 13.93 to 17.18
  tokens/s (n = 5, mixed conditions). The cause of the slowest run was
  not identified.
- CPU temperature was not recorded.
- Results apply to this configuration only.

## Reproduce
1. Install Ollama and run `ollama pull llama3.2:1b`
2. Create a Python virtual environment and run `pip install psutil`
3. Run `python tools\bench_ollama.py 20`