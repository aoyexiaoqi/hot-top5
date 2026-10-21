import pytest

from hot_top5 import core


class TestFmtCount:
    def test_small_numbers(self):
        assert core.fmt_count(0) == "0"
        assert core.fmt_count(9999) == "9999"

    def test_wan(self):
        assert core.fmt_count(10000) == "1万"
        assert core.fmt_count(1234567) == "123.5万"
        assert core.fmt_count(4620949) == "462.1万"
        assert core.fmt_count(2149941) == "215万"

    def test_yi(self):
        assert core.fmt_count(123456789) == "1.23亿"
        assert core.fmt_count(100000000) == "1亿"

    def test_invalid_input_passthrough(self):
        assert core.fmt_count("abc") == "abc"
        assert core.fmt_count(None) == "None"


class TestBilibili:
    def test_parsing_order_and_fields(self, stub_fetch):
        entries = core.fetch_bilibili(5)
        assert len(entries) == 5
        first = entries[0]
        assert first["rank"] == 1
        # Title whitespace is stripped.
        assert first["title"] == "城市夜市探访：带着100万吃遍一条街"
        assert first["author"] == "影视飓风"
        assert first["url"] == "https://www.bilibili.com/video/BV1pGnn67EbB"
        # List order from the API is the ranking order.
        assert [e["rank"] for e in entries] == [1, 2, 3, 4, 5]
        assert entries[4]["title"] == "官方MV正式上线"

    def test_raw_and_formatted_plays(self, stub_fetch):
        entries = core.fetch_bilibili(5)
        assert entries[0]["plays"] == 4620949
        assert entries[0]["plays_text"] == "462.1万"
        assert entries[1]["plays"] == 123456789
        assert entries[1]["plays_text"] == "1.23亿"

    def test_top_slicing(self, stub_fetch):
        entries = core.fetch_bilibili(3)
        assert len(entries) == 3
        assert entries[-1]["title"] == "十分钟学会一道家常菜"

    def test_nonzero_code_raises(self, stub_fetch):
        stub_fetch(bilibili={"code": -404, "data": {}})
        with pytest.raises(RuntimeError, match="code=-404"):
            core.fetch_bilibili(5)


class TestDouyin:
    def test_sorted_by_position(self, stub_fetch):
        entries = core.fetch_douyin(5)
        assert [e["title"] for e in entries] == [
            "城市夜市美食节开幕",
            "台风正向我国方向靠近",
            "冬天第一串糖葫芦",
            "新片首日票房破纪录",
            "本地球队夺冠游行",
        ]
        assert [e["rank"] for e in entries] == [1, 2, 3, 4, 5]

    def test_fields(self, stub_fetch):
        first = core.fetch_douyin(5)[0]
        # Title comes from `word`, heat from `hot_value`, URL from sentence_id.
        assert first["title"] == "城市夜市美食节开幕"
        assert first["heat"] == 11434269
        assert first["heat_text"] == "1143.4万"
        assert first["url"] == "https://www.douyin.com/hot/2705737"

    def test_top_slicing(self, stub_fetch):
        entries = core.fetch_douyin(2)
        assert len(entries) == 2
        assert entries[-1]["title"] == "台风正向我国方向靠近"

    def test_missing_sentence_id_falls_back_to_hot_home(self, stub_fetch):
        payload = {
            "data": {
                "word_list": [
                    {"word": "无ID话题", "hot_value": 12345, "position": 1}
                ]
            }
        }
        stub_fetch(douyin=payload)
        (entry,) = core.fetch_douyin(5)
        assert entry["url"] == "https://www.douyin.com/hot"


class TestCollect:
    def test_partial_failure(self, stub_fetch):
        stub_fetch(fail=("douyin",))
        results, errors = core.collect(["bilibili", "douyin"], 5)
        assert results["douyin"] is None
        assert "boom-douyin" in errors["douyin"]
        assert results["bilibili"] is not None
        assert len(results["bilibili"]) == 5
        assert "bilibili" not in errors
