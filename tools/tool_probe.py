"""One-call probe: does the model call a tool correctly?"""
import json
import urllib.request

URL = "http://localhost:11434/api/chat"
body = {
    "model": "llama3.2:1b",
    "messages": [
        {"role": "user", "content": "What is 1234 multiplied by 5678? Use the tool."}
    ],
    "tools": [{
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two integers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
    }],
    "stream": False,
    "options": {"temperature": 0, "seed": 0},
}
req = urllib.request.Request(
    URL,
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=600) as resp:
    print(json.dumps(json.load(resp)["message"], indent=2))