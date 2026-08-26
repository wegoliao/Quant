---
id: GB02
title: 積木 · PIT 財報與營收防偷看對齊器 (PIT & Lag Aligner)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/strategies/claude_core.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB02-pit-lag-aligner.html
notebooklm_tags: [building-block, pit, point-in-time, lag, lookahead, finlab]
---

# 積木 · PIT 財報與營收防偷看對齊器 (PIT Aligner)

## 一句話定義 (TL;DR)

一個確保財務報表與月營收資料在回測時**嚴格依據法定發布日期（而非財務期間標籤）遞延生效**的對齊器，徹底消除 Lookahead Bias（偷看未來資料）。

---

## 1. 黑盒子解構 (What Problem It Solves)

財務報表（例如 2024Q1 季報）涵蓋期間至 3/31，但法定申報截止日是 5/15；月營收（4月營收）統計至 4/30，但申報截止日是 5/10。若直接將資料以 3/31 或 4/30 作為生效日，回測將在市場知曉前提前交易，產生虛假高報酬。

### 契約不變量 (Invariants):
1. **月營收遞延**：$M$ 月的營收數字，最早只能在 $M+1$ 月 11 日的開盤價生效。
2. **季報遞延**：第 $Q$ 季財報，一律遞延至法定申報截止日之次一交易日生效。
3. **無未來行**：任何 $T$ 日產生的選股遮罩，其依賴的特徵矩陣在 $T$ 日之後的數值一律不可被讀取。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB02: Point-In-Time (PIT) & Lag Aligner for Fundamental Data."""

from __future__ import annotations

import pandas as pd


def align_monthly_revenue_pit(
    revenue_df: pd.DataFrame,
    trading_calendar: pd.DatetimeIndex,
    release_day_of_month: int = 11,
) -> pd.DataFrame:
    """將月營收資料對齊至法定發布日（次月 11 日）的 PIT 時間軸。

    Args:
        revenue_df: 原始月營收 DataFrame (Index 為月份標籤，如 2024-04-30)
        trading_calendar: 每日交易日曆 Index
        release_day_of_month: 法定公告截止日的次日 (預設 11 號)

    Returns:
        pd.DataFrame: 展開至日頻且經過 PIT 遞延的營收矩陣
    """
    pit_records = {}
    
    for dt, row in revenue_df.iterrows():
        dt = pd.to_datetime(dt)
        # 次月 11 號作為最早生效日期
        if dt.month == 12:
            effective_dt = pd.Timestamp(year=dt.year + 1, month=1, day=release_day_of_month)
        else:
            effective_dt = pd.Timestamp(year=dt.year, month=dt.month + 1, day=release_day_of_month)
        
        pit_records[effective_dt] = row

    pit_sparse = pd.DataFrame.from_dict(pit_records, orient="index")
    pit_sparse = pit_sparse.sort_index()

    # 重新對齊至全體交易日曆，並以前值填充 (Forward Fill)
    daily_pit = pit_sparse.reindex(trading_calendar).ffill()
    return daily_pit
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb02_monthly_revenue_pit_no_lookahead():
    # 建立 2024-04-30 的 4 月營收
    dates = pd.date_range("2024-05-01", "2024-05-15", freq="D")
    raw_rev = pd.DataFrame({"2330": [100.0]}, index=[pd.Timestamp("2024-04-30")])
    
    pit_rev = align_monthly_revenue_pit(raw_rev, dates, release_day_of_month=11)
    
    # 在 5/10 (含) 之前，PIT 營收必須為 NaN (尚未公佈)
    assert pd.isna(pit_rev.loc["2024-05-10", "2330"])
    
    # 在 5/11 當天開始，PIT 營收正式生效
    assert pit_rev.loc["2024-05-11", "2330"] == 100.0
    assert pit_rev.loc["2024-05-15", "2330"] == 100.0
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請解釋 GB02 積木是如何透過日曆重對齊（Reindex & FFill）防止回測程式在 5 月 1 日偷看到 4 月營收數據的？」
