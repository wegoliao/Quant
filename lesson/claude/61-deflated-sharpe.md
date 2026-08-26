---
id: C61
title: 去膨脹夏普：怎麼算才算數
author_ai: Claude (Opus 5, Anthropic)
track: validation
status: verified
verified_by: src/quant_grill_lab/search/deflated.py
updated: 2026-08-26
notebooklm_tags: [dsr, deflated-sharpe, overfitting, skew, kurtosis]
---

# 去膨脹夏普：怎麼算才算數

> **證據**：624 次機械計數的試驗 + 12 檔候選的實際計算

## 它在回答什麼

> 就算所有策略都毫無價值，你試了 N 次之後，最好的那一個仍然會呈現多高的 Sharpe？

在純噪音上跑 500 組參數，最好的那組一定會有可觀的 Sharpe。不是有時候，是**必然** —— N 個零均值抽樣的期望最大值隨 N 成長。所以「我們找到 1.6」在你說出「我們看了幾個」之前沒有意義。

參考：Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*。

## 兩個數字

**`expected_max_sharpe(n_trials, variance_of_trial_sharpes)`**
即使每個策略都沒價值，最好的 N 個之一仍會呈現的 Sharpe。這是門檻。它隨試驗數上升，也隨試驗結果的**離散度**上升 —— 一群表現接近的試驗門檻低；一群結果天差地遠的試驗門檻高，因為那個離散度本身就是噪音在主導的證據。

**`deflated_sharpe_ratio(...)`**
在修正偏度與峰度之後，觀測 Sharpe 真的高於那個門檻的機率。

DSR = 0.95 的意思是：考慮你試了幾次、以及這些報酬的形狀，有 95% 的機率真實 Sharpe 高於選擇偏差門檻。低於 0.95 就是「和搜尋夠久之後的運氣分不出來」。

## 完整實作

```python
def compute_dsr(candidate_returns, trial_sharpes_annualised, n_trials):
    # 陷阱一：模組內部用日頻 Sharpe，試驗紀錄通常是年化的
    ann = np.sqrt(252)
    trial_sharpes_daily = np.asarray(trial_sharpes_annualised) / ann

    d = deflated_sharpe_ratio(
        candidate_returns,                       # 日報酬序列
        n_trials=n_trials,                       # 機械計數，不是手填
        trial_sharpes=trial_sharpes_daily.tolist(),   # 全部試驗，不只存活者
    )
    return {
        "dsr": d.deflated_probability,
        "bar_annualised": d.annualised_benchmark,
        "observed_annualised": d.annualised_observed,
        "passes": d.passes,
        "skew": d.skew,
        "kurtosis": d.kurtosis,
    }
```

## 三個必須做對的地方

### 一、試驗數要機械計數

```python
def kiln_trials():
    sh = []
    for f in sorted(glob.glob("evidence/kiln/exp*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, list):
            continue
        for row in d:
            v = row.get("sharpe_local")
            if isinstance(v, (int, float)) and np.isfinite(v):
                sh.append(float(v))
    return len(sh), np.array(sh)
```

實測：機械計數得到 **624**，而人工填的紀錄寫 134（另一份寫 253）。門檻差 0.26 個 Sharpe（1.401 → 1.660），足以翻轉判定。

**設計準則**：搜尋程式在跑的時候就要把每一次試驗寫進紀錄檔，DSR 從紀錄檔數，不接受任何呼叫端手動提供的 `n_trials`。

### 二、單位不能混

模組內部：

```python
observed = float(series.mean()) / standard_deviation      # 日頻，約 0.14
```

如果你餵年化的 `trial_sharpes`，門檻會用年化尺度算（1.660），拿去和日頻觀測值（0.139）比 —— **所有 DSR 都會是 0.0000**。

**症狀對照表**：

| 現象 | 病因 |
|---|---|
| 所有 DSR 都是 0.0000 | 門檻是年化、觀測是日頻 |
| 所有 DSR 都是 1.0000 | 反過來，或門檻算成 0 |
| DSR 恰好等於某個漂亮的整數 | 沒真的算，是填的 |

### 三、要餵全部試驗，包括爛的

只餵通過門檻的存活者，離散度被低估，門檻跟著低估，結果被高估。

## 實測結果

門檻：624 次試驗、年化 **1.660**。

| S### | Sharpe | DSR | 偏度 | 峰度 | 判定 |
|---|---|---|---|---|---|
| S122 | 2.211 | **0.9595** | -1.52 | 16.8 | 通過 |
| S138 | 2.148 | 0.9435 | — | — | 差 0.007 |
| S127 | 2.107 | 0.9406 | -0.27 | 5.5 | 未過 |
| S144 | 2.110 | 0.9298 | -1.10 | 13.9 | 未過 |
| S123 | 2.097 | 0.9237 | -1.20 | 12.1 | 未過 |
| S124 | 2.027 | 0.8885 | -1.06 | 10.6 | 未過 |
| S004 | 1.993 | 0.8714 | -0.70 | 8.7 | 未過 |
| S125 | 1.816 | 0.7340 | -0.83 | 10.9 | 未過 |
| S022 | 1.756 | 0.6282 | -0.82 | 9.2 | 未過 |
| S148 | 1.545 | 0.3430 | +0.05 | 5.5 | 未過 |
| S126 | 1.499 | 0.2881 | -0.53 | 5.3 | 未過 |

注意偏度那一欄：**S127 的 Sharpe（2.107）低於 S144（2.110），但 DSR 反而比較高（0.9406 vs 0.9298）**。因為 S127 的偏度只有 -0.27、峰度 5.5，而 S144 是 -1.10 / 13.9。左尾越厚，同樣的 Sharpe 越不值錢。

DSR 的分母正是在做這件事：

```python
denominator_squared = 1.0 - skew * observed + ((kurtosis - 1.0) / 4.0) * observed**2
```

負偏度會放大分母，讓左尾策略需要更高的 Sharpe 才能達到同樣的 DSR。

## 兩種讀法都要報

| 讀法 | N | 離散度來源 | 門檻（年化） | 通過 |
|---|---|---|---|---|
| 已宣告的搜尋活動 | 624 | 該次 campaign 的試驗 | 1.660 | 1 / 12 |
| 整個 catalog 當一次搜尋 | 127 | 跨家族（大得多） | **2.713** | **0 / 12** |

兩個都對，在回答不同問題。第二種問的是「如果你是從這 127 檔裡挑最好的那一個呢」—— 答案是沒有一檔站得住。

**誠實的報告要並列，不能只挑好看的那個。**

## 它修正不了什麼

1. **沒申報的試驗**。624 是有 JSON 紀錄的，手動試的、外部繼承的（例如從公開文章移植的策略，發表者自己的搜尋成本未知）都不在裡面。真實門檻只會更高。
2. **前視偏誤**。DSR 假設你的回測至少是誠實的。一個有前視的 Sharpe 4.9 會輕鬆通過任何 DSR 門檻。**要先做 shift(1) 測試，再做 DSR。**
3. **樣本外**。DSR 修正「你找了多少次」，不修正「你有沒有看過答案」。

## 記住

> DSR 是必要條件，不是充分條件。順序是：先確認沒有前視 → 再確認成本誠實 → 才輪到 DSR。

相關：[試驗計數](52-trial-counting.md)、[前視偏誤](50-lookahead-bias.md)、[參數高原](62-parameter-plateau.md)
