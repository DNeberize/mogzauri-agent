"""All tools the agent can use. Add a new tool here and the LLM will see it automatically."""

from .currency import convert_currency
from .weather import get_weather
from .wikipedia import search_wikipedia

TOOLS = [get_weather, convert_currency, search_wikipedia]
TOOLS_BY_NAME = {fn.__name__: fn for fn in TOOLS}
