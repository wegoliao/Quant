---
id: GB04
title: 積木 · ADV20 流動性與容量守門員 (ADV20 Capacity Guard)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/execution/capacity_guard.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB04-adv-capacity-guard.html
notebooklm_tags: [building-block, capacity, adv20, liquidity, market-impact, risk-guard]
---

# 積木 · ADV20 流動性與容量守門員 (Capacity Guard)

## 一句話定義 (TL;DR)

一個在訂單送出前自動比對個股近 20 日成交金額（ADV20）的**剛性流動性守門員**：超過 2% 發出警報，超過 5% 直接阻擋下單，防止流動性幻覺與過大市場衝擊成本。

---

## 1. 黑盒子解構 (What Problem It Solves)

許多回測策略透過頻繁交易成交量極低的微型股創造出驚人報酬率，但在實盤中，單筆下單若超過日成交量的 5%，將直接推動市場造成巨大滑價，甚至完全無法出清部位。

### 契約不變量 (Invariants):
1. **硬限制 (Hard Block)**：$\text{Order Notional} / \text{ADV20} > 5\%$ 時，狀態判定為 `BLOCKED`，禁止下單。
2. **警示限制 (Warning)**：$2\% < \text{Participation Rate} \le 5\%$ 時，狀態為 `WARNING`。
3. **安全限制 (OK)**：$\le 2\%$ 時為 `OK`。
4. **Fail-Closed**：若 ADV20 數據缺失或 $\le 0$，一律判定為 `BLOCKED`。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB04: 20-Day Average Daily Volume (ADV20) Capacity Guard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class CapacityExceededError(RuntimeError):
    """當訂單超過 5% ADV20 硬上限時拋出。"""


@dataclass(frozen=True)
class CapacityVerdict:
    stock_id: str
    shares: int
    price: float
    order_notional: float
    adv20_notional: float
    participation_rate: float
    status: str  # "OK" | "WARNING" | "BLOCKED"
    warning: Optional[str] = None
    suggested_max_shares: Optional[int] = None


class CapacityGuard:
    WARN_RATIO: float = 0.02  # 2%
    HARD_LIMIT_RATIO: float = 0.05  # 5%

    @classmethod
    def evaluate(
        cls,
        stock_id: str,
        shares: int,
        price: float,
        adv20_notional: float,
    ) -> CapacityVerdict:
        """評估單筆委託之流動性與容量安全度。"""
        order_notional = shares * price

        # 異常防禦 (Fail-Closed)
        if adv20_notional <= 0:
            return CapacityVerdict(
                stock_id=stock_id,
                shares=shares,
                price=price,
                order_notional=order_notional,
                adv20_notional=adv20_notional,
                participation_rate=1.0,
                status="BLOCKED",
                warning="ADV20 資料無效或為零，拒絕下單。",
                suggested_max_shares=0,
            )

        rate = order_notional / adv20_notional
        suggested_shares = int((adv20_notional * cls.HARD_LIMIT_RATIO) // price)

        if rate > cls.HARD_LIMIT_RATIO:
            return CapacityVerdict(
                stock_id=stock_id,
                shares=shares,
                price=price,
                order_notional=order_notional,
                adv20_notional=adv20_notional,
                participation_rate=rate,
                status="BLOCKED",
                warning=f"參與率 {rate:.1%} 超過 5% 硬限制，恐造成嚴重衝擊成本。",
                suggested_max_shares=suggested_shares,
            )
        elif rate > cls.WARN_RATIO:
            return CapacityVerdict(
                stock_id=stock_id,
                shares=shares,
                price=price,
                order_notional=order_notional,
                adv20_notional=adv20_notional,
                participation_rate=rate,
                status="WARNING",
                warning=f"參與率 {rate:.1%} 介於 2%~5%，建議分批掛單。",
                suggested_max_shares=suggested_shares,
            )

        return CapacityVerdict(
            stock_id=stock_id,
            shares=shares,
            price=price,
            order_notional=order_notional,
            adv20_notional=adv20_notional,
            participation_rate=rate,
            status="OK",
        )
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb04_capacity_guard_thresholds():
    adv20 = 10_000_000.0  # 日均 1000 萬
    price = 100.0

    # 1. 1% (1000 股 = 10 萬) -> OK
    v1 = CapacityGuard.evaluate("2330", 1000, price, adv20)
    assert v1.status == "OK"

    # 2. 3% (3000 股 = 30 萬) -> WARNING
    v2 = CapacityGuard.evaluate("2330", 3000, price, adv20)
    assert v2.status == "WARNING"

    # 3. 6% (6000 股 = 60 萬) -> BLOCKED
    v3 = CapacityGuard.evaluate("2330", 6000, price, adv20)
    assert v3.status == "BLOCKED"
    assert v3.suggested_max_shares == 5000  # 建議上限 5% = 50 萬 = 5000 股
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請解釋為什麼在量化實盤交易中，單筆下單參與率（Participation Rate）超過 5% ADV20 會被列為致命風險？」
