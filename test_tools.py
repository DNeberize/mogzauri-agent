"""Quick check that every tool works on its own (no LLM, no GPU needed).  Run:  python test_tools.py"""

from agent.tools import convert_currency, get_weather, search_wikipedia

print(get_weather("Tbilisi", 2), "\n")
print(convert_currency(100, "USD", "GEL"), "\n")
print(search_wikipedia("Gergeti Trinity Church"), "\n")
# error handling
print(get_weather("Xyzqwertyville"))
print(convert_currency(10, "ABC", "GEL"))
