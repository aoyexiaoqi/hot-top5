# hot-top5

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

一条命令获取今天的**抖音热榜 Top 5** 和 **B 站全站排行榜 Top 5**。纯 Python 标准库实现，零第三方依赖，支持 Markdown / JSON / 纯文本输出，某个平台获取失败时只标注失败、绝不编造数据。

[English](#english)

## 数据来源说明（请先看这里）

两个平台的榜单口径**不一样**，本工具如实标注，不做加工：

- **B 站**：官方公开排行榜接口，是真正的**视频排行榜**，每条带 UP 主和原始播放量。
- **抖音**：公开的是**热榜话题榜**——每条是一个热点话题（由相关视频驱动），带的是抖音的**热度值**，不是单个视频的播放量。抖音没有公开单视频播放量排行榜，所以本工具给的是热榜话题 Top 5，链接指向对应的热点详情页。

## 安装

```bash
pip install git+https://github.com/aoyexiaoqi/hot-top5.git
```

或从源码安装：

```bash
git clone https://github.com/aoyexiaoqi/hot-top5.git
cd hot-top5
pip install .
```

需要 Python 3.9 及以上版本，无任何第三方依赖。

## 用法

```bash
hot-top5                                # 两个平台的 Top 5（Markdown）
hot-top5 --top 10                       # 每个平台取前 10 条（1–50）
hot-top5 --platform bilibili            # 只看 B 站（或 douyin）
hot-top5 --format json                  # JSON 输出，方便程序处理
hot-top5 --format text                  # 纯文本（不带 Markdown 链接）
hot-top5 --out today.md                 # 同时把结果写入文件
```

| 选项 | 说明 | 默认 |
| --- | --- | --- |
| `--top N` | 每个平台取前 N 条（1–50） | `5` |
| `--platform` | `all` / `douyin` / `bilibili` | `all` |
| `--format` | `markdown` / `json` / `text` | `markdown` |
| `--out FILE` | 同时把结果写入文件 | 不写 |

退出码：`0` 至少一个平台获取成功；`1` 两个平台都失败；`2` 参数错误。

## 示例输出

Markdown（某次真实运行的结果节选）：

```markdown
## B站排行榜 Top 5
1. [带着100万，我们见了成人网红...](https://www.bilibili.com/video/BV1pGnn67EbB) — 影视飓风 · 播放 462.3万
2. [《绝区零》菲欧妮EP | 1% Battery Girl 低电量女孩](https://www.bilibili.com/video/BV1SknF6KE5g) — 绝区零 · 播放 242万
3. [每一位认真谋生的人都值得被仰望](https://www.bilibili.com/video/BV1Jonu6mEwN) — 李炮炮儿 · 播放 252.5万

## 抖音热榜 Top 5
1. [国台办回应张凌赫赴台交流被拒](https://www.douyin.com/hot/2705737) — 热度 1143.4万
2. [台风蔷琵正向我国方向靠近](https://www.douyin.com/hot/2706231) — 热度 1110.2万
3. [长征文物资源家底基本摸清](https://www.douyin.com/hot/2705763) — 热度 1099.9万
```

JSON 结构（`plays` / `heat` 为原始数值）：

```json
{
  "bilibili": [
    {"rank": 1, "title": "…", "author": "影视飓风", "plays": 4620949, "url": "https://www.bilibili.com/video/BV1pGnn67EbB"}
  ],
  "douyin": [
    {"rank": 1, "title": "…", "heat": 11434269, "url": "https://www.douyin.com/hot/2705737"}
  ]
}
```

某个平台失败时，Markdown/文本模式下该平台的位置会标注「获取失败」及原因；JSON 模式下该平台为 `null`，并多一个 `errors` 字段说明原因。

## 每天自动获取

本工具只负责「运行一次、获取一次」。想每天自动收到榜单，可以自己在系统里挂一个定时任务，例如 Linux/macOS 的 cron（每天 12:50 把结果写进文件）：

```cron
50 12 * * * hot-top5 --out ~/hot-top5-$(date +\%F).md
```

Windows 用户可以用「任务计划程序」定时运行 `hot-top5`，配合 `--out` 保存到文件。

## English

`hot-top5` is a tiny, dependency-free CLI that fetches today's top 5 entries from two Chinese video platforms:

- **Bilibili**: the official public ranking — a true video chart with authors and raw view counts.
- **Douyin**: the public hot chart. Note the different caliber: its entries are trending *topics* (each driven by its videos) carrying a heat index, not per-video view counts — Douyin publishes no per-video view ranking.

```bash
pip install git+https://github.com/aoyexiaoqi/hot-top5.git
hot-top5                     # both platforms, Markdown
hot-top5 --top 10 --platform douyin --format json
hot-top5 --out today.md
```

Options: `--top N` (1–50, default 5), `--platform all|douyin|bilibili`, `--format markdown|json|text`, `--out FILE`. Exit codes: `0` at least one platform succeeded, `1` both failed, `2` usage error. If one platform fails, the other is still printed and the failed one is clearly marked (in JSON mode it becomes `null` with an `errors` field) — data is never fabricated. Requires Python 3.9+, standard library only. To get the chart daily, schedule it yourself with cron or Windows Task Scheduler (see the Chinese section above).

## License

MIT
