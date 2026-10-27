"""The agent loop: the LLM decides whether to call a tool or answer the user."""

import json
import re
from datetime import date

from .llm import LocalLLM
from .tools import TOOLS, TOOLS_BY_NAME

SYSTEM_PROMPT = f"""You are Mogzauri, a helpful travel assistant for trips in Georgia (the country).
Today is {date.today().isoformat()}.
Use the available tools when you need real data (weather, money conversion, facts about places).
Never invent weather or exchange rates — call the tool. If a tool returns ERROR, tell the user honestly.
Answer briefly and practically, in the same language the user writes in."""

TOOL_CALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.DOTALL)
MAX_STEPS = 5  # max tool calls per user question, so the agent can't loop forever


def parse_tool_calls(text: str) -> list[dict]:
    """Extract tool calls in Qwen's <tool_call>{"name": ..., "arguments": {...}}</tool_call> format."""
    calls = []
    for raw in TOOL_CALL_RE.findall(text):
        try:
            calls.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return calls


def run_tool(name: str, arguments: dict) -> str:
    if name not in TOOLS_BY_NAME:
        return f"ERROR: unknown tool '{name}'."
    try:
        return TOOLS_BY_NAME[name](**arguments)
    except TypeError as e:  # wrong / missing arguments chosen by the model
        return f"ERROR: bad arguments for {name}: {e}"


class Agent:
    def __init__(self, llm: LocalLLM | None = None, verbose: bool = True):
        self.llm = llm or LocalLLM()
        self.verbose = verbose
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]  # memory = chat history

    def ask(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})

        for _ in range(MAX_STEPS):
            reply = self.llm.generate(self.messages, tools=TOOLS)
            calls = parse_tool_calls(reply)

            if not calls:  # the model decided to answer directly
                self.messages.append({"role": "assistant", "content": reply.strip()})
                return reply.strip()

            self.messages.append({
                "role": "assistant",
                "tool_calls": [{"type": "function", "function": c} for c in calls],
            })
            for call in calls:
                name, args = call.get("name", ""), call.get("arguments", {})
                result = run_tool(name, args)
                if self.verbose:
                    print(f"  [tool] {name}({args}) -> {result[:200]}")
                self.messages.append({"role": "tool", "name": name, "content": result})

        return "Sorry, I could not finish this request (too many tool steps)."
