import json

import pytest

from hot_top5 import cli


class TestMarkdown:
    def test_default_output(self, stub_fetch, capsys):
        rc = cli.main([])
        out = capsys.readouterr().out
        assert rc == 0
        assert "## B站排行榜 Top 5" in out
        assert "## 抖音热榜 Top 5" in out
        assert (
            "[城市夜市探访：带着100万吃遍一条街]"
            "(https://www.bilibili.com/video/BV1pGnn67EbB)"
            " — 影视飓风 · 播放 462.1万" in out
        )
        assert (
            "[城市夜市美食节开幕](https://www.douyin.com/hot/2705737)"
            " — 热度 1143.4万" in out
        )

    def test_top_flag_slices_both_platforms(self, stub_fetch, capsys):
        rc = cli.main(["--top", "3"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "## B站排行榜 Top 3" in out
        assert "## 抖音热榜 Top 3" in out
        assert "十分钟学会一道家常菜" in out  # bilibili #3 kept
        assert "不是AI特效！这才是真功夫" not in out  # bilibili #4 cut
        assert "新片首日票房破纪录" not in out  # douyin #4 cut

    def test_platform_filter(self, stub_fetch, capsys):
        rc = cli.main(["--platform", "douyin"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "抖音热榜" in out
        assert "B站排行榜" not in out


class TestTextFormat:
    def test_plain_lines_without_markdown_links(self, stub_fetch, capsys):
        rc = cli.main(["--format", "text"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "B站排行榜 Top 5" in out
        assert "## " not in out
        assert "](" not in out
        assert (
            "1. 城市夜市探访：带着100万吃遍一条街 — 影视飓风 · 播放 462.1万"
            " · https://www.bilibili.com/video/BV1pGnn67EbB" in out
        )
        assert "1. 城市夜市美食节开幕 — 热度 1143.4万" in out


class TestJsonFormat:
    def test_structure(self, stub_fetch, capsys):
        rc = cli.main(["--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert set(payload) == {"bilibili", "douyin"}
        bili = payload["bilibili"]
        assert len(bili) == 5
        assert set(bili[0]) == {"rank", "title", "author", "plays", "url"}
        assert bili[0]["rank"] == 1
        assert bili[0]["plays"] == 4620949  # raw count, not formatted
        assert bili[0]["url"] == "https://www.bilibili.com/video/BV1pGnn67EbB"
        dy = payload["douyin"]
        assert len(dy) == 5
        assert set(dy[0]) == {"rank", "title", "heat", "url"}
        assert dy[0]["heat"] == 11434269
        assert dy[0]["title"] == "城市夜市美食节开幕"

    def test_top_and_platform(self, stub_fetch, capsys):
        rc = cli.main(
            ["--format", "json", "--platform", "bilibili", "--top", "2"]
        )
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert set(payload) == {"bilibili"}
        assert len(payload["bilibili"]) == 2


class TestFailures:
    def test_one_platform_failure_markdown(self, stub_fetch, capsys):
        stub_fetch(fail=("douyin",))
        rc = cli.main([])
        out = capsys.readouterr().out
        assert rc == 0  # at least one platform succeeded
        assert "城市夜市探访" in out  # bilibili unaffected
        assert "抖音榜单本次获取失败" in out
        assert "boom-douyin" in out

    def test_one_platform_failure_json(self, stub_fetch, capsys):
        stub_fetch(fail=("douyin",))
        rc = cli.main(["--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert payload["douyin"] is None
        assert "boom-douyin" in payload["errors"]["douyin"]
        assert len(payload["bilibili"]) == 5

    def test_both_fail_exit_1_markdown(self, stub_fetch, capsys):
        stub_fetch(fail=("bilibili", "douyin"))
        rc = cli.main([])
        out = capsys.readouterr().out
        assert rc == 1
        assert "B站榜单本次获取失败" in out
        assert "抖音榜单本次获取失败" in out

    def test_both_fail_exit_1_json(self, stub_fetch, capsys):
        stub_fetch(fail=("bilibili", "douyin"))
        rc = cli.main(["--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert rc == 1
        assert payload["bilibili"] is None
        assert payload["douyin"] is None
        assert set(payload["errors"]) == {"bilibili", "douyin"}


class TestOutFile:
    def test_out_file_written(self, stub_fetch, capsys, tmp_path):
        target = tmp_path / "hot.md"
        rc = cli.main(["--out", str(target)])
        printed = capsys.readouterr().out
        assert rc == 0
        content = target.read_text(encoding="utf-8")
        assert "## 抖音热榜 Top 5" in content
        assert "城市夜市美食节开幕" in content
        assert content.strip() == printed.strip()


class TestUsageErrors:
    def test_top_out_of_range(self, stub_fetch):
        for bad in ("0", "51"):
            with pytest.raises(SystemExit) as excinfo:
                cli.main(["--top", bad])
            assert excinfo.value.code == 2

    def test_bad_format_choice(self, stub_fetch):
        with pytest.raises(SystemExit) as excinfo:
            cli.main(["--format", "yaml"])
        assert excinfo.value.code == 2
