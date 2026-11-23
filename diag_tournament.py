"""Read-only diagnostic: count questions the Metaculus API returns for the
current seasonal tournament, with and without the 'open' filter.

Prints only public facts (ids, titles, status, close time). The token is read
from the environment and is never printed. Any failure is caught and logged.
"""
import json
import os
import urllib.parse
import urllib.request

BASE = "https://www.metaculus.com/api/posts/"


def _get(params: dict) -> dict:
    url = BASE + "?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json", "User-Agent": "metac-bot-diag/1.0"}
    token = os.getenv("METACULUS_TOKEN")
    if token:
        headers["Authorization"] = f"Token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return {"http": resp.status, "body": json.loads(resp.read().decode("utf-8"))}


def _summarize(label: str, params: dict) -> None:
    try:
        out = _get(params)
        body = out["body"]
        results = body.get("results", []) if isinstance(body, dict) else []
        total = body.get("count") if isinstance(body, dict) else None
        print(f"[diag] {label}: http={out['http']} returned={len(results)} count={total}")
        for p in results[:5]:
            q = p.get("question") or {}
            print(
                f"[diag]   id={p.get('id')} status={p.get('status')} "
                f"close={q.get('scheduled_close_time')} title={str(p.get('title'))[:70]!r}"
            )
    except Exception as e:  # never break the bot run
        print(f"[diag] {label}: failed {type(e).__name__}: {str(e)[:120]}")


def run_diag(tournament_id: int | str = 33121) -> None:
    base = {"tournaments": tournament_id, "limit": 5, "order_by": "-published_at"}
    _summarize("any status", base)
    _summarize("statuses=open", {**base, "statuses": "open"})
    _summarize("slug fall-futureeval-2026 any", {**base, "tournaments": "fall-futureeval-2026"})
    _summarize("minibench any", {**base, "tournaments": "minibench"})
