---
id: GB05
title: 積木 · 券商手續費低消與損益平衡門檻計算器 (Fee Floor Calculator)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/execution/fee_floor.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB05-fee-floor-calculator.html
notebooklm_tags: [building-block, fee-floor, transaction-costs, break-even, odd-lot]
---

# 積木 · 券商手續費低消與損益平衡門檻計算器 (Fee Floor)

## 一句話定義 (TL;DR)

一個精確計算台股**券商單筆最低手續費（例如 NT$ 20 元）對交易損益平衡點影響**的評估積木，自動剔除因單筆金額過小而被手續費吃光利潤的無效標的。

---

## 1. 黑盒子解構 (What Problem It Solves)

台灣券商通常設有單筆委託手續費最低 NT$ 20 元的限制。若為追求等權重而在零股下單 NT$ 2,000 元，單趟實質手續費率高達 $1.0\%$，來回成本即高達 $2.3\%$，遠超大部分策略的單筆預期 Alpha。

### 契約不變量 (Invariants):
1. **實質手續費率計算**：$\text{Effective Fee} = \max(\text{Notional} \times \text{Discounted Rate}, \text{Min Fee})$。
2. **損益平衡門檻 (Break-even Move)**：買進後個股必須上漲多少百分比才能打平進出費稅。
3. **過濾機制**：若單筆部位金額低於損益平衡門檻，判定為 `BELOW_MIN_ECONOMIC_NOTIONAL`。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB05: Broker Fee Floor and Break-even Calculator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeBreakdown:
    notional: float
    raw_fee: float
    charged_fee: float
    effective_fee_rate: float
    roundtrip_total_cost: float
    breakeven_return_pct: float
    is_economically_viable: bool


class FeeFloorCalculator:
    BASE_FEE_RATE: float = 0.001425  # 0.1425%
    TAX_RATE: float = 0.003000       # 0.3% 證交稅
    DEFAULT_MIN_FEE: float = 20.0    # 最低 20 元

    def __init__(
        self,
        discount: float = 0.28,        # 2.8 折
        min_fee: float = DEFAULT_MIN_FEE,
        max_acceptable_cost_pct: float = 0.008,  # 單筆總成本不超過 0.8%
    ):
        self.discount = discount
        self.min_fee = min_fee
        self.fee_rate = self.BASE_FEE_RATE * discount
        self.max_acceptable_cost_pct = max_acceptable_cost_pct

    def evaluate(self, notional: float) -> FeeBreakdown:
        """計算給定交易金額之完整摩擦成本與可行性。"""
        if notional <= 0:
            return FeeBreakdown(0, 0, self.min_fee, 1.0, self.min_fee, 1.0, False)

        raw_buy_fee = notional * self.fee_rate
        charged_buy_fee = max(raw_buy_fee, self.min_fee)
        
        # 假設賣出金額相近
        charged_sell_fee = charged_buy_fee
        tax = notional * self.TAX_RATE
        
        total_roundtrip_cost = charged_buy_fee + charged_sell_fee + tax
        cost_ratio = total_roundtrip_cost / notional
        
        # 損益平衡所需漲幅
        breakeven_pct = (total_roundtrip_cost) / (notional - charged_sell_fee - tax)

        is_viable = cost_ratio <= self.max_acceptable_cost_pct

        return FeeBreakdown(
            notional=notional,
            raw_fee=raw_buy_fee,
            charged_fee=charged_buy_fee,
            effective_fee_rate=charged_buy_fee / notional,
            roundtrip_total_cost=total_roundtrip_cost,
            breakeven_return_pct=breakeven_pct,
            is_economically_viable=is_viable,
        )
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb05_fee_floor_viability():
    calc = FeeFloorCalculator(discount=0.28, min_fee=20.0, max_acceptable_cost_pct=0.01) # 上限 1%

    # 1. 極小金額 NT$ 2,000 (手續費 20 元佔 1%，來回成本破 2.3%) -> 不可行
    r1 = calc.evaluate(2000.0)
    assert not r1.is_economically_viable
    assert r1.charged_fee == 20.0

    # 2. 正常金額 NT$ 50,000 (手續費 20 元佔 0.04%，來回成本約 0.38%) -> 可行
    r2 = calc.evaluate(50000.0)
    assert r2.is_economically_viable
    assert r2.breakeven_return_pct < 0.005
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請利用 GB05 積木計算，在 2.8 折手續費與最低 20 元限制下，單筆下單金額至少需要多少元，才能使來回總摩擦成本控制在 0.5% 以內？」
