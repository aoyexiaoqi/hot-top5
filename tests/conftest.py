"""Offline fixtures: recorded-shaped API payloads + a fetch_json stub.

No test ever touches the network: ``hot_top5.core.fetch_json`` (the single
network entry point) is monkeypatched with a fake that dispatches on the
URL and returns the payloads below, or raises for platforms in ``fail``.
"""

import pytest

from hot_top5 import core

BILIBILI_PAYLOAD = {
    "code": 0,
    "data": {
        "list": [
            {
                "title": " 城市夜市探访：带着100万吃遍一条街 ",
                "bvid": "BV1pGnn67EbB",
                "owner": {"name": "影视飓风"},
                "stat": {"view": 4620949},
            },
            {
                "title": "新游戏实况：第一章全流程",
                "bvid": "BV1SknF6KE5g",
                "owner": {"name": "游戏UP主"},
                "stat": {"view": 123456789},
            },
            {
                "title": "十分钟学会一道家常菜",
                "bvid": "BV1Jonu6mEwN",
                "owner": {"name": "厨房小白"},
                "stat": {"view": 98765},
            },
            {
                "title": "不是AI特效！这才是真功夫",
                "bvid": "BV1MHJB63Emv",
                "owner": {"name": "含亮老师"},
                "stat": {"view": 5000},
            },
            {
                "title": "官方MV正式上线",
                "bvid": "BV1j5nj68E48",
                "owner": {"name": "游戏官方"},
                "stat": {"view": 2149941},
            },
            {
                "title": "第六名视频",
                "bvid": "BV1extra0006",
                "owner": {"name": "UP主六"},
                "stat": {"view": 111},
            },
            {
                "title": "第七名视频",
                "bvid": "BV1extra0007",
                "owner": {"name": "UP主七"},
                "stat": {"view": 100},
            },
        ]
    },
}

# word_list is deliberately NOT in position order: sorting must fix it.
DOUYIN_PAYLOAD = {
    "data": {
        "word_list": [
            {
                "word": "冬天第一串糖葫芦",
                "hot_value": 10998645,
                "sentence_id": "2705763",
                "position": 3,
            },
            {
                "word": "城市夜市美食节开幕",
                "hot_value": 11434269,
                "sentence_id": "2705737",
                "position": 1,
            },
            {
                "word": "台风正向我国方向靠近",
                "hot_value": 11101735,
                "sentence_id": "2706231",
                "position": 2,
            },
            {
                "word": "新片首日票房破纪录",
                "hot_value": 8000000,
                "sentence_id": "2705800",
                "position": 4,
            },
            {
                "word": "本地球队夺冠游行",
                "hot_value": 50000,
                "sentence_id": "2705690",
                "position": 5,
            },
            {
                "word": "第六名话题",
                "hot_value": 40000,
                "sentence_id": "2705006",
                "position": 6,
            },
            {
                "word": "第七名话题",
                "hot_value": 30000,
                "sentence_id": "2705007",
                "position": 7,
            },
        ]
    },
}


def _make_fake(fail=(), bilibili=None, douyin=None):
    def fake_fetch_json(url, referer, timeout=20):
        if "bilibili" in url:
            if "bilibili" in fail:
                raise RuntimeError("boom-bilibili")
            return BILIBILI_PAYLOAD if bilibili is None else bilibili
        if "douyin" in url:
            if "douyin" in fail:
                raise RuntimeError("boom-douyin")
            return DOUYIN_PAYLOAD if douyin is None else douyin
        raise AssertionError(f"unexpected url: {url}")

    return fake_fetch_json


@pytest.fixture
def stub_fetch(monkeypatch):
    """Install the fake fetch_json. Default: both platforms succeed.

    Call the returned installer again with ``fail=(...)`` or custom
    payloads to reconfigure within a test.
    """

    def install(**kwargs):
        monkeypatch.setattr(core, "fetch_json", _make_fake(**kwargs))

    install()
    return install
