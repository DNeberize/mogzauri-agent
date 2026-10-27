"""Command-line chat with the agent.  Run:  python main.py"""

from agent.agent import Agent


def main():
    agent = Agent()
    print("\nMogzauri is ready. Ask about a trip in Georgia (type 'exit' to quit).\n")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"exit", "quit"}:
            break
        if text:
            print(f"Agent: {agent.ask(text)}\n")


if __name__ == "__main__":
    main()
