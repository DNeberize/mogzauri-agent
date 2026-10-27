"""Currency tool — uses official National Bank of Georgia (NBG) exchange rates."""

import requests

NBG_URL = "https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json/"


def _gel_rate(code: str) -> float:
    """Return how many GEL one unit of `code` costs (GEL itself = 1)."""
    if code == "GEL":
        return 1.0
    data = requests.get(NBG_URL, params={"currencies": code}, timeout=10).json()
    items = data[0]["currencies"] if data else []
    if not items:
        raise ValueError(f"unknown currency code '{code}'")
    return items[0]["rate"] / items[0]["quantity"]


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert money between currencies using today's National Bank of Georgia rates.

    Args:
        amount: Amount of money to convert (e.g. 100).
        from_currency: ISO code of the source currency (e.g. "USD", "EUR", "GEL").
        to_currency: ISO code of the target currency (e.g. "GEL", "USD").

    Returns:
        A sentence with the converted amount and the rate used,
        or an error message starting with "ERROR".
    """
    src, dst = from_currency.strip().upper(), to_currency.strip().upper()
    try:
        result = float(amount) * _gel_rate(src) / _gel_rate(dst)
    except ValueError as e:
        return f"ERROR: {e}."
    except requests.RequestException as e:
        return f"ERROR: NBG service unavailable ({e})."
    return f"{amount} {src} = {result:.2f} {dst} (NBG official rate)"
