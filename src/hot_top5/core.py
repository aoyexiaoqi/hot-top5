"""Core fetching and parsing for hot-top5.

Data sources (public endpoints, no login required):

- Bilibili: ``https://api.bilibili.com/x/web-interface/ranking/v2`` — a true
  video ranking. The returned list order is the composite ranking order and
  every entry carries a raw view count.
- Douyin: ``https://www.douyin.com/aweme/v1/web/hot/search/list/`` — the
  public hot chart. Its entries are trending *topics* (each topic is driven
  by its videos), ordered by the ``position`` field, and each carries a
  ``hot_value`` heat index. Douyin does not publish a per-video view-count
  ranking.

Only the Python standard library is used. ``fetch_json`` is the single
network entry point, which keeps the parsing layer trivially testable
offline by stubbing that one function.
"""

import json
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

BILIBILI_API = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
BILIBILI_REFERER = "https://www.bilibili.com/"
DOUYIN_API = (
    "https://www.douyin.com/aweme/v1/web/hot/search/list/"
    "?device_platform=webapp&aid=6383&channel=channel_pc_web"
)
DOUYIN_REFERER = "https://www.douyin.com/"

# Display/processing order for the platforms.
PLATFORM_ORDER = ["bilibili", "douyin"]


def fetch_json(url, referer, timeout=20):
    """Fetch *url* with a browser-like UA and decode the JSON body."""
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Referer": referer}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fmt_count(n):
    """Format a raw count Chinese-style: 1234567 -> '123.5万', 1.2e8 -> '1.2亿'."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return str(n)
    if n >= 1e8:
        return f"{n / 1e8:.2f}".rstrip("0").rstrip(".") + "亿"
    if n >= 1e4:
        return f"{n / 1e4:.1f}".rstrip("0").rstrip(".") + "万"
    return str(int(n))


def fetch_bilibili(top=5):
    """Return the Bilibili ranking as a list of entry dicts (at most *top*).

    Each entry: {rank, title, author, plays, plays_text, url}, where
    ``plays`` is the raw view count and ``plays_text`` its formatted form.
    """
    data = fetch_json(BILIBILI_API, BILIBILI_REFERER)
    if data.get("code") != 0:
        raise RuntimeError(f"bilibili api code={data.get('code')}")
    items = data.get("data", {}).get("list", [])[:top]
    entries = []
    for i, v in enumerate(items, 1):
        plays = v.get("stat", {}).get("view", 0)
        entries.append(
            {
                "rank": i,
                "title": (v.get("title") or "").strip(),
                "author": v.get("owner", {}).get("name", ""),
                "plays": plays,
                "plays_text": fmt_count(plays),
                "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
            }
        )
    return entries


def fetch_douyin(top=5):
    """Return the Douyin hot chart as a list of entry dicts (at most *top*).

    Each entry: {rank, title, heat, heat_text, url}, where ``heat`` is the
    raw ``hot_value`` heat index and ``heat_text`` its formatted form.
    Entries are sorted by the API's ``position`` field.
    """
    data = fetch_json(DOUYIN_API, DOUYIN_REFERER)
    words = data.get("data", {}).get("word_list", [])
    words = sorted(words, key=lambda w: w.get("position", 999))[:top]
    entries = []
    for i, w in enumerate(words, 1):
        heat = w.get("hot_value", 0)
        sid = w.get("sentence_id", "")
        entries.append(
            {
                "rank": i,
                "title": (w.get("word") or "").strip(),
                "heat": heat,
                "heat_text": fmt_count(heat),
                "url": (
                    f"https://www.douyin.com/hot/{sid}"
                    if sid
                    else "https://www.douyin.com/hot"
                ),
            }
        )
    return entries


FETCHERS = {"bilibili": fetch_bilibili, "douyin": fetch_douyin}


def collect(platforms, top=5):
    """Fetch every platform in *platforms*.

    Returns ``(results, errors)``: ``results`` maps each platform to its
    entry list, or ``None`` if that platform failed; ``errors`` maps each
    failed platform to its error message. A failing platform never raises
    and never fabricates entries.
    """
    results, errors = {}, {}
    for name in platforms:
        try:
            results[name] = FETCHERS[name](top)
        except Exception as exc:  # noqa: BLE001 - report, never fabricate
            results[name] = None
            errors[name] = str(exc)
    return results, errors
