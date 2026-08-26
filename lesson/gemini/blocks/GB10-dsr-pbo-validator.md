---
id: GB10
title: 積木 · DSR 與 PBO 過擬合檢驗器 (Deflated Sharpe & PBO Validator)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/strategy_selection/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB10-dsr-pbo-validator.html
notebooklm_tags: [building-block, dsr, deflated-sharpe, pbo, overfitting-validator, statistics]
---

# 積木 · DSR 與 PBO 過擬合檢驗器 (DSR Validator)

## 一句話定義 (TL;DR)

一個依據 López de Prado 統計理論，將**回測總試驗次數（Number of Trials）、報酬偏態與峰態**納入計算，求得去膨脹夏普值（Deflated Sharpe Ratio, DSR）與過擬合機率的統計防禦積木。

---

## 1. 黑盒子解構 (What Problem It Solves)

在大量參數搜尋（例如 GA 演化 400 次）後，最高夏普值必然虛高。本積木提供精確的 DSR 計算，若策略 DSR $< 0.95$，代表其回測結果無法排除「純粹運氣」的可能性。

### 核心公式：

$$\text{Expected Max SR} = \sigma_{\text{SR}} \left( (1 - \gamma) \Phi^{-1}\left(1 - \frac{1}{N}\right) + \gamma \Phi^{-1}\left(1 - \frac{1}{N \cdot e}\right) \right)$$

$$\text{DSR} = \Phi\left( \frac{(\widehat{\text{SR}} - \text{Expected Max SR}) \sqrt{T - 1}}{\sqrt{1 - \widehat{\gamma}_3 \widehat{\text{SR}} + \frac{\widehat{\gamma}_4 - 1}{4} \widehat{\text{SR}}^2}} \right)$$

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB10: Deflated Sharpe Ratio (DSR) Calculator."""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis


def compute_deflated_sharpe_ratio(
    strategy_returns: pd.Series,
    num_trials: int,
    var_sharpe_trials: float = 0.5,
) -> float:
    """計算給定報酬序列在 N 次多重試驗下的 Deflated Sharpe Ratio (DSR)。

    Args:
        strategy_returns: 策略日報酬率序列
        num_trials: 總搜尋試驗次數 (例如 400)
        var_sharpe_trials: 所有試驗的 Sharpe 估計變異數 (預設 0.5)

    Returns:
        float: DSR 統計機率值 [0.0, 1.0] (>= 0.95 代表通過 95% 信心檢定)
    """
    clean_r = strategy_returns.dropna()
    t_len = len(clean_r)
    if t_len < 30 or num_trials <= 0:
        return 0.0

    mean_r = clean_r.mean()
    std_r = clean_r.std()
    if std_r == 0:
        return 0.0

    annual_sr = (mean_r / std_r) * np.sqrt(252)
    daily_sr = mean_r / std_r

    # 計算偏態與峰態
    skewness = skew(clean_r)
    kurt = kurtosis(clean_r, fisher=False)  # 常態分配為 3.0

    # 1. 期望最大隨機 Sharpe (每日尺度)
    euler_mascheroni = 0.5772156649
    daily_sr_std = np.sqrt(var_sharpe_trials / 252.0)
    
    term1 = (1.0 - euler_mascheroni) * norm.ppf(1.0 - 1.0 / num_trials)
    term2 = euler_mascheroni * norm.ppf(1.0 - 1.0 / (num_trials * math.e))
    exp_max_sr = daily_sr_std * (term1 + term2)

    # 2. DSR 檢定統計量
    variance_term = 1.0 - skewness * daily_sr + ((kurt - 1.0) / 4.0) * (daily_sr ** 2)
    if variance_term <= 0:
        return 0.0

    denom = np.sqrt(variance_term)
    z_stat = (daily_sr - exp_max_sr) * np.sqrt(t_len - 1) / denom

    dsr = float(norm.cdf(z_stat))
    return dsr
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb10_dsr_penalty_with_increasing_trials():
    np.random.seed(42)
    # 產生年化 Sharpe 約 2.0 的優秀策略
    daily_ret = pd.Series(np.random.normal(0.001, 0.01, 1000))
    
    # 1. 在僅有 1 次試驗下，DSR 極高
    dsr_1 = compute_deflated_sharpe_ratio(daily_ret, num_trials=1)
    
    # 2. 在經過 10,000 次數據挖掘試驗後，DSR 必然顯著下降
    dsr_10000 = compute_deflated_sharpe_ratio(daily_ret, num_trials=10000)
    
    assert dsr_1 > dsr_10000
    assert dsr_1 > 0.90
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請利用 GB10 積木說明，為什麼一個看似年化 Sharpe 2.0 的策略，在經過 10,000 次參數隨機搜尋後，其 DSR 信心水準會大幅暴跌？」
