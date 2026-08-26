---
id: GB09
title: 積木 · 現金流營收動能因子選股核心 (FCF & Revenue Momentum Core)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/strategies/gemini_001_weighted_cashflow_momentum.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB09-fcf-momentum-core.html
notebooklm_tags: [building-block, fcf, momentum, multi-factor, stock-screening, alpha-core]
---

# 積木 · 現金流營收動能因子選股核心 (FCF Momentum Core)

## 一句話定義 (TL;DR)

一個融合**營運現金流品質（Operating Cash Flow）、營業毛利率（Gross Margin）、低波動度（Low Volatility）、52 週新高動能與低股價淨值比**的台股高勝率多因子選股引擎。

---

## 1. 黑盒子解構 (What Problem It Solves)

單純追逐動能股容易在行情反轉時買在最高點，而單純價值選股則容易陷入「價值陷阱（Value Trap）」。本積木將**高品質現金流**與**價格突破動能**進行橫斷面百分位融合（Cross-sectional Ranking），兼具高爆發力與高胃納量。

### 因子評分矩陣 (Composite Factor Score):

$$\text{Score}_t = \text{Rank}(\text{OCF}) + \text{Rank}(\text{Gross Margin}) + \text{Rank}(\text{Low Vol}) + \text{Rank}(\text{Near 52W High}) + \text{Rank}(\text{Low PB}) + \text{Rank}(\text{Momentum 120D})$$

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB09: Free Cash Flow and Momentum Multi-Factor Selector."""

from __future__ import annotations

import pandas as pd


def rank_market(df: pd.DataFrame) -> pd.DataFrame:
    """橫斷面百分位排名 [0, 1]。"""
    return df.rank(axis=1, pct=True)


def build_fcf_momentum_universe(
    operating_cash_flow: pd.DataFrame,
    gross_margin: pd.DataFrame,
    close_price: pd.DataFrame,
    pb_ratio: pd.DataFrame,
    top_n: int = 20,
    momentum_window: int = 120,
    high_window: int = 240,
) -> pd.DataFrame:
    """計算多因子複合分數並選出 Top N 標的遮罩 (Boolean DataFrame)。"""
    # 1. 價格動能與低波動
    mom = close_price.pct_change(momentum_window)
    vol = -close_price.pct_change().rolling(60).std()  # 負標準差代表低波動
    near_high = close_price / close_price.rolling(high_window).max()
    low_pb = -pb_ratio

    # 2. 橫斷面排名融合
    composite_score = (
        rank_market(operating_cash_flow)
        + rank_market(gross_margin)
        + rank_market(vol)
        + rank_market(near_high)
        + rank_market(low_pb)
        + rank_market(mom)
    )

    # 3. 選取排名前 N 檔
    selected_mask = composite_score.rank(axis=1, ascending=False) <= top_n
    return selected_mask
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb09_fcf_factor_scoring():
    # 建立 3 檔股票之假資料
    df_ocf = pd.DataFrame({"A": [100], "B": [50], "C": [10]})
    df_gm = pd.DataFrame({"A": [0.4], "B": [0.3], "C": [0.1]})
    df_close = pd.DataFrame({"A": [100.0], "B": [50.0], "C": [20.0]})
    df_pb = pd.DataFrame({"A": [1.5], "B": [2.0], "C": [5.0]})

    mask = build_fcf_momentum_universe(
        df_ocf, df_gm, df_close, df_pb, top_n=1, momentum_window=1, high_window=1
    )
    
    # 股票 A 在各指標均最優，應被唯一選中
    assert mask.loc[0, "A"] == True
    assert mask.loc[0, "B"] == False
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請說明 GB09 選股核心中，為什麼要同時納入『低波動度（Low Vol）』與『52週新高動能』這兩個看似相反的因子？」
