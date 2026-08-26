---
id: GB07
title: 積木 · 限價智慧追價與重報價狀態機 (Smart Requote Engine)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/execution/requote.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB07-smart-requote-engine.html
notebooklm_tags: [building-block, requote, state-machine, limit-order, execution]
---

# 積木 · 限價智慧追價與重報價狀態機 (Smart Requote)

## 一句話定義 (TL;DR)

一個在限價單送出後未成交時，依據**等待時間、市場向上偏離幅度與最大追價次數**，自動進行「維持掛單、改價追價或安全撤單」的有限狀態機（FSM）。

---

## 1. 黑盒子解構 (What Problem It Solves)

被動限價單（Passive Limit Order）常常會面臨「股價直接往有利方向發動，留下未成交委託而錯失行情（Execution Drag）」的問題；但無腦市價追價又會造成嚴重滑價。本積木提供可控的智慧追價狀態機。

### 狀態機流程 (FSM Diagram):

```
       [SUBMITTED / PENDING]
                │
                ├── 等待時間 < 30 秒 ──> 維持掛單 (HOLD)
                │
                ├── 超時且 Best Ask 上移 ≤ 2 Ticks ──> 改價追價 (REQUOTE_UP)
                │
                ├── 累計追價次數已達上限 (Max 2 次) ──> 停止追價 (TERMINATE_KEEP)
                │
                └── 價格劇烈偏離 > 1.5% 或接近收盤 ──> 安全撤單 (CANCEL_ABORT)
```

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB07: Smart Requote Finite State Machine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RequoteAction(str, Enum):
    HOLD = "HOLD"
    REQUOTE = "REQUOTE"
    CANCEL = "CANCEL"
    COMPLETE = "COMPLETE"


@dataclass
class OrderState:
    order_id: str
    stock_id: str
    initial_limit_price: float
    current_limit_price: float
    target_shares: int
    filled_shares: int
    elapsed_seconds: float
    requote_count: int


class SmartRequoteEngine:
    MAX_REQUOTE_ATTEMPTS: int = 2
    TIMEOUT_SECONDS: float = 45.0
    MAX_SLIPPAGE_PCT: float = 0.015  # 最大允許追價 1.5%

    @classmethod
    def evaluate(
        cls,
        state: OrderState,
        current_best_ask: float,
    ) -> tuple[RequoteAction, float]:
        """評估當前委託應採取的行動與新價格。"""
        if state.filled_shares >= state.target_shares:
            return RequoteAction.COMPLETE, state.current_limit_price

        # 1. 檢查是否超過總滑價保護
        price_drift = (current_best_ask - state.initial_limit_price) / state.initial_limit_price
        if price_drift > cls.MAX_SLIPPAGE_PCT:
            return RequoteAction.CANCEL, 0.0

        # 2. 檢查是否超時需要重報價
        if state.elapsed_seconds >= cls.TIMEOUT_SECONDS:
            if state.requote_count < cls.MAX_REQUOTE_ATTEMPTS:
                # 追價至當前 Best Ask (但不超過上限)
                new_price = min(current_best_ask, state.initial_limit_price * (1 + cls.MAX_SLIPPAGE_PCT))
                return RequoteAction.REQUOTE, new_price
            else:
                # 已達最大追價次數，撤單或維持
                return RequoteAction.CANCEL, 0.0

        return RequoteAction.HOLD, state.current_limit_price
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb07_requote_state_transitions():
    state = OrderState(
        order_id="ord_01",
        stock_id="2330",
        initial_limit_price=100.0,
        current_limit_price=100.0,
        target_shares=1000,
        filled_shares=0,
        elapsed_seconds=50.0, # 已超時 45 秒
        requote_count=0,
    )
    
    # 1. Ask 漲到 100.5 (在 1.5% 內) -> 觸發 REQUOTE
    action, new_price = SmartRequoteEngine.evaluate(state, current_best_ask=100.5)
    assert action == RequoteAction.REQUOTE
    assert new_price == 100.5

    # 2. Ask 暴漲至 105.0 (> 1.5%) -> 觸發 CANCEL 保護
    action_cancel, _ = SmartRequoteEngine.evaluate(state, current_best_ask=105.0)
    assert action_cancel == RequoteAction.CANCEL
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請分析 GB07 狀態機如何透過『最大追價次數』與『滑價百分比上限』兩道防線，避免程式在追高時買在當日最高點？」
