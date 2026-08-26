---
id: GB08
title: 積木 · 動態波動度目標部位調節器 (Volatility Target Sizer)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/strategies/gemini_004_vol_target_cashflow_momentum.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB08-volatility-target-sizer.html
notebooklm_tags: [building-block, volatility-targeting, risk-management, sizing, dynamic-scaling]
---

# 積木 · 動態波動度目標部位調節器 (Vol-Target Sizer)

## 一句話定義 (TL;DR)

一個依據投組近期實現波動度（Realized Volatility），將整體曝險水位動態縮放至**預設目標年化波動度（如 15%）**的風控積木，在高波動崩跌期自動降倉、低波動穩定期加滿倉位。

---

## 1. 黑盒子解構 (What Problem It Solves)

股票市場具有「波動度群聚效應（Volatility Clustering）」：在崩盤與劇烈震盪期，單日波動劇增，若維持 100% 倉位，MDD 將快速失控；透過目標波動度調節，策略能在市場恐慌時自動抽離資金保留現金。

### 數學公式：
設目標年化波動度為 $\sigma_{\text{target}}$（例如 $0.15$），過去 $W$ 日實現年化波動度為 $\widehat{\sigma}_t$：

$$\text{Scalar}_t = \text{clip}\left( \frac{\sigma_{\text{target}}}{\widehat{\sigma}_t}, \text{Min Exposure}, \text{Max Exposure} \right)$$

$$w_{i, t}^{\text{adjusted}} = w_{i, t}^{\text{base}} \times \text{Scalar}_t$$

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB08: Volatility Targeting Exposure Scaler."""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_volatility_targeting(
    portfolio_daily_returns: pd.Series,
    target_annual_vol: float = 0.15,
    lookback_days: int = 30,
    min_exposure: float = 0.20,
    max_exposure: float = 1.00,
    annualization_factor: float = np.sqrt(252),
) -> pd.Series:
    """計算每日動態部位曝險縮放乘數 (Exposure Scalar)。

    Args:
        portfolio_daily_returns: 投組歷史日報酬率序列
        target_annual_vol: 目標年化波動度 (預設 15%)
        lookback_days: 歷史滾動計算視窗 (預設 30 日)
        min_exposure: 最低持股水位
        max_exposure: 最高持股水位 (如 1.0 代表不開槓桿)

    Returns:
        pd.Series: 每日部位縮放係數序列 [min_exposure, max_exposure]
    """
    realized_vol = portfolio_daily_returns.rolling(lookback_days).std() * annualization_factor
    realized_vol = realized_vol.replace(0, np.nan).fillna(target_annual_vol)

    raw_scalar = target_annual_vol / realized_vol
    scaled_exposure = raw_scalar.clip(lower=min_exposure, upper=max_exposure)
    return scaled_exposure
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb08_vol_targeting_scaling():
    # 模擬 50 天的高波動市場 (日波動 2% -> 年化約 31.7%)
    returns_high_vol = pd.Series([0.02, -0.02] * 25)
    
    scalar = apply_volatility_targeting(
        returns_high_vol,
        target_annual_vol=0.15,
        lookback_days=20,
        min_exposure=0.2,
        max_exposure=1.0,
    )
    
    # 實現年化波動約 31.7%，目標 15%，乘數應自動降至約 0.47
    latest_scalar = scalar.iloc[-1]
    assert 0.40 <= latest_scalar <= 0.55
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請解釋 GB08 積木中 Volatility Targeting 的原理，它如何在 2020 年 3 月疫情股災或 2022 年大空頭中保護投組不受毀滅性打擊？」
