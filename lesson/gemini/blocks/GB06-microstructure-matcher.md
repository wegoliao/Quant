---
id: GB06
title: 積木 · 五檔微結構與衝擊成本評級器 (Microstructure Matcher)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/execution/strategy_microstructure_matcher.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB06-microstructure-matcher.html
notebooklm_tags: [building-block, microstructure, orderbook, bid-ask-spread, order-routing]
---

# 積木 · 五檔微結構與衝擊成本評級器 (Microstructure Matcher)

## 一句話定義 (TL;DR)

一個依據即時**買賣五檔深度（Order Book Depth）、買賣價差（Bid-Ask Spread）與即時成交筆數**，自動為策略委託分級並推薦最佳掛單策略（例如 Buy1 排隊、TWAP 拆單、市價快速吃單）的微結構評級引擎。

---

## 1. 黑盒子解構 (What Problem It Solves)

不同的股票具有截然不同的盤口微結構：
- **高流動性大型股（如台積電、鴻海）**：五檔掛單厚實、Spread 僅 1 Tick，適合直接在 Best Bid 排隊爭取零滑價。
- **中小型成長飆股**：五檔極薄、Spread 常達 3~5 Ticks，直接市價吃單會造成巨大滑價，必須採用 TWAP 分批掛單。

### 契約不變量 (Invariants):
1. **Spread 比例**：$\text{Spread Ratio} = (\text{Ask}_1 - \text{Bid}_1) / \text{Mid Price}$。
2. **深度比率 (Depth Ratio)**：$\text{Order Shares} / \text{Top 3 Bids Volume}$。
3. **策略推薦**：
   - 若 Spread $\le 0.1\%$ 且深度充裕 $\rightarrow$ `PASSIVE_LIMIT_QUEUE`（被動排隊）。
   - 若 Spread 較大但欲搶進 $\rightarrow$ `SPLIT_TWAP`（智慧拆單）。
   - 若流動性枯竭 $\rightarrow$ `REJECT_ILLIQUID`（拒絕下單）。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB06: Real-time Orderbook Microstructure Matcher."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class LevelQuote:
    bid_prices: Sequence[float]
    bid_volumes: Sequence[int]
    ask_prices: Sequence[float]
    ask_volumes: Sequence[int]


@dataclass(frozen=True)
class MicrostructureVerdict:
    spread: float
    spread_bps: float
    top3_bid_volume: int
    top3_ask_volume: int
    recommended_action: str  # "PASSIVE_QUEUE" | "TWAP_SPLIT" | "REJECT_ILLIQUID"
    suggested_limit_price: float


class MicrostructureMatcher:
    MAX_SPREAD_BPS = 25.0  # 25 bps (0.25%)
    
    @classmethod
    def evaluate(
        cls,
        quote: LevelQuote,
        order_shares: int,
        side: str = "BUY",
    ) -> MicrostructureVerdict:
        if not quote.bid_prices or not quote.ask_prices:
            return MicrostructureVerdict(0, 0, 0, 0, "REJECT_ILLIQUID", 0.0)

        bid1, ask1 = quote.bid_prices[0], quote.ask_prices[0]
        mid = (bid1 + ask1) / 2.0
        spread = ask1 - bid1
        spread_bps = (spread / mid) * 10000.0

        top3_bid_vol = sum(quote.bid_volumes[:3])
        top3_ask_vol = sum(quote.ask_volumes[:3])

        if spread_bps > 50.0 or top3_ask_vol == 0:
            return MicrostructureVerdict(
                spread, spread_bps, top3_bid_vol, top3_ask_vol, "REJECT_ILLIQUID", bid1
            )

        # 若買進量大於第 1 檔賣量，但小於前 3 檔
        if order_shares > quote.ask_volumes[0]:
            action = "TWAP_SPLIT"
            limit_price = ask1
        else:
            action = "PASSIVE_QUEUE"
            limit_price = bid1

        return MicrostructureVerdict(
            spread=spread,
            spread_bps=spread_bps,
            top3_bid_volume=top3_bid_vol,
            top3_ask_volume=top3_ask_vol,
            recommended_action=action,
            suggested_limit_price=limit_price,
        )
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb06_microstructure_matching():
    # 建立深度充足之盤口
    quote = LevelQuote(
        bid_prices=[100.0, 99.5, 99.0],
        bid_volumes=[50, 100, 200],
        ask_prices=[100.5, 101.0, 101.5],
        ask_volumes=[10, 50, 100],
    )
    
    # 1. 小單 (5 股 <= ask1 10 股) -> 被動掛單
    v1 = MicrostructureMatcher.evaluate(quote, order_shares=5)
    assert v1.recommended_action == "PASSIVE_QUEUE"
    assert v1.suggested_limit_price == 100.0

    # 2. 較大單 (30 股 > ask1 10 股) -> 建議 TWAP 拆單
    v2 = MicrostructureMatcher.evaluate(quote, order_shares=30)
    assert v2.recommended_action == "TWAP_SPLIT"
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請解釋 GB06 積木如何透過五檔委託簿深度（Level 2 Quotes）判斷是否需要將一筆大單切分為 TWAP 拆單執行？」
