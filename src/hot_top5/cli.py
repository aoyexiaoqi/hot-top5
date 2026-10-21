"""Command-line interface for hot-top5."""

import argparse
import json
import sys

from . import core

HEADINGS = {"bilibili": "B站排行榜", "douyin": "抖音热榜"}
FAIL_LABELS = {"bilibili": "B站", "douyin": "抖音"}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hot-top5",
        description="获取抖音热榜与 B 站全站排行榜的 Top N（默认 Top 5）",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="每个平台取前 N 条，1–50（默认：5）",
    )
    parser.add_argument(
        "--platform",
        choices=["all", "douyin", "bilibili"],
        default="all",
        help="只看某个平台（默认：all）",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "text"],
        default="markdown",
        help="输出格式（默认：markdown）",
    )
    parser.add_argument(
        "--out",
        metavar="FILE",
        help="同时把结果写入该文件",
    )
    return parser


def _entry_line(name, entry, markdown):
    if name == "bilibili":
        if markdown:
            return (
                f"{entry['rank']}. [{entry['title']}]({entry['url']})"
                f" — {entry['author']} · 播放 {entry['plays_text']}"
            )
        return (
            f"{entry['rank']}. {entry['title']}"
            f" — {entry['author']} · 播放 {entry['plays_text']} · {entry['url']}"
        )
    if markdown:
        return (
            f"{entry['rank']}. [{entry['title']}]({entry['url']})"
            f" — 热度 {entry['heat_text']}"
        )
    return f"{entry['rank']}. {entry['title']} — 热度 {entry['heat_text']} · {entry['url']}"


def _render_sections(results, errors, top, markdown):
    sections = []
    for name in core.PLATFORM_ORDER:
        if name not in results:
            continue
        heading = f"{HEADINGS[name]} Top {top}"
        lines = [f"## {heading}" if markdown else heading]
        if results[name] is None:
            lines.append(
                f"（{FAIL_LABELS[name]}榜单本次获取失败：{errors.get(name, 'unknown error')}）"
            )
        else:
            lines.extend(
                _entry_line(name, entry, markdown) for entry in results[name]
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def render_markdown(results, errors, top):
    return _render_sections(results, errors, top, markdown=True)


def render_text(results, errors, top):
    return _render_sections(results, errors, top, markdown=False)


def render_json(results, errors):
    payload = {}
    for name in core.PLATFORM_ORDER:
        if name not in results:
            continue
        entries = results[name]
        if entries is None:
            payload[name] = None
        elif name == "bilibili":
            payload[name] = [
                {k: e[k] for k in ("rank", "title", "author", "plays", "url")}
                for e in entries
            ]
        else:
            payload[name] = [
                {k: e[k] for k in ("rank", "title", "heat", "url")} for e in entries
            ]
    if errors:
        payload["errors"] = errors
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not 1 <= args.top <= 50:
        parser.error("--top 必须在 1 到 50 之间")

    platforms = (
        core.PLATFORM_ORDER if args.platform == "all" else [args.platform]
    )
    results, errors = core.collect(platforms, args.top)

    if args.format == "json":
        output = render_json(results, errors)
    elif args.format == "text":
        output = render_text(results, errors, args.top)
    else:
        output = render_markdown(results, errors, args.top)

    print(output)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(output + "\n")

    succeeded = any(results[name] is not None for name in platforms)
    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
