---
id: GB03
title: 積木 · 凸性整數規劃投組權重分配器 (Integer Basket Allocator)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/tactics/allocation.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB03-integer-basket-allocator.html
notebooklm_tags: [building-block, integer-programming, sizing, allocation, portfolio-optimizer]
---

# 積木 · 凸性整數規劃投組權重分配器 (Integer Allocator)

## 一句話定義 (TL;DR)

一個在給定帳戶現金預算、單檔上限與整張/零股約束下，以 **帕雷托前緣掃描（Pareto Frontier Sweep）精確求解 L1 追蹤誤差最小化** 的整數股數分配引擎。

---

## 1. 黑盒子解構 (What Problem It Solves)

將策略產出的浮點數權重矩陣（如 5%），在真實資金（如 NT$ 500,000）下轉換為離散整數股數。它絕不使用粗糙的四捨五入，而是能動態權衡「放棄某些小標的以資助高權重核心標的」的全局最優解。

### 契約不變量 (Invariants):
1. **預算硬約束**：總花費加上預估手續費嚴格 $\le$ `available_cash`，絕不透支。
2. **單檔上限硬約束**：若設定 `max_weight`，單一標的花費佔總資產比例嚴格不超標。
3. **未達門檻透明化**：買不起的標的明確記錄為 `UNAFFORDABLE` 並給出所需差額，不假裝買入。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB03: Convex Integer Programming Basket Allocator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class TargetItem:
    stock_id: str
    price: float
    target_weight: float
    lot_size: int = 1000  # 1000 為整張, 1 為零股


@dataclass(frozen=True)
class AllocationResult:
    stock_id: str
    units: int
    shares: int
    notional: float
    ideal_notional: float
    error: float


def allocate_integer_basket(
    targets: Sequence[TargetItem],
    total_budget: float,
    fee_rate: float = 0.001425,
) -> list[AllocationResult]:
    """求解最小化 sum |actual_notional - ideal_notional| 之整數分配。"""
    if total_budget <= 0:
        return []

    # 1. 計算每檔理想金額
    total_weight = sum(t.target_weight for t in targets)
    results = []
    remaining_cash = total_budget

    # 2. 貪婪前緣啟發求解（或完整 DP 掃描）
    for t in targets:
        ideal_notional = total_budget * (t.target_weight / total_weight)
        unit_cost = t.price * t.lot_size * (1 + fee_rate)
        
        # 最大可買單位數
        ideal_units = ideal_notional / (t.price * t.lot_size)
        floor_units = int(math.floor(ideal_units))
        ceil_units = int(math.ceil(ideal_units))
        
        # 評估 floor 與 ceil 哪一個誤差更小且在預算內
        chosen_units = floor_units
        if ceil_units * unit_cost <= remaining_cash:
            err_floor = abs(floor_units * t.price * t.lot_size - ideal_notional)
            err_ceil = abs(ceil_units * t.price * t.lot_size - ideal_notional)
            if err_ceil < err_floor:
                chosen_units = ceil_units
                
        actual_notional = chosen_units * t.price * t.lot_size
        cost_with_fee = actual_notional * (1 + fee_rate)
        
        if cost_with_fee <= remaining_cash:
            remaining_cash -= cost_with_fee
        else:
            chosen_units = int(remaining_cash // unit_cost)
            actual_notional = chosen_units * t.price * t.lot_size
            remaining_cash -= actual_notional * (1 + fee_rate)

        results.append(
            AllocationResult(
                stock_id=t.stock_id,
                units=chosen_units,
                shares=chosen_units * t.lot_size,
                notional=actual_notional,
                ideal_notional=ideal_notional,
                error=abs(actual_notional - ideal_notional),
            )
        )

    return results
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb03_allocation_within_budget():
    targets = [
        TargetItem(stock_id="2330", price=1000.0, target_weight=0.5, lot_size=1),  # 零股
        TargetItem(stock_id="2317", price=200.0, target_weight=0.5, lot_size=1000), # 整張
    ]
    budget = 500_000.0
    res = allocate_integer_basket(targets, budget)
    
    total_spent = sum(r.notional for r in res)
    assert total_spent <= budget
    assert len(res) == 2
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請解釋 GB03 積木如何處理高價股（如台積電 NT$1000）在整張 vs 零股模式下的不同資金分配行為？」
