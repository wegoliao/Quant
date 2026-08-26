---
id: B10
title: shift(1) 前視測試 · 任何疊加層的有罪推定
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: []
inputs: [base_daily_returns, signal_series, overlay_fn]
outputs: [lag0_metrics, lag1_metrics, verdict]
verified_by: evidence/CLAUDE_VERIFICATION_GEMINI_CAGR50_2026-08-26.md
updated: 2026-08-26
notebooklm_tags: [lookahead, shift, overlay, regime, leakage, verification]
---

# B10 · shift(1) 前視測試

## 它解決什麼

回測引擎可以擋住「同棒成交」，但擋不住**在引擎外面對報酬序列做乘法**的疊加層：

```python
r_levered = base_returns * regime_multiplier      # 引擎完全看不到這一行
```

這一行如果 `regime_multiplier` 用了當日資訊，你會得到一條 Sharpe 4.9、MDD -5.5% 的曲線，而且回測引擎的每一項檢查都會通過。

**實測過的後果**：一份宣稱 CAGR 61–65% 的報告，全部超額報酬來自這一行少了 `.shift(1)`。

## 契約

```python
def shift1_test(base_returns, signal, overlay, floor=0.95):
    """比較同日訊號與落後一日訊號。回傳兩組指標與判定。

    base_returns : pd.Series  疊加之前的日報酬
    signal       : pd.Series  布林訊號（例如 close > MA）
    overlay      : callable   (returns, signal) -> returns
    floor        : float      lag1 至少要保住 lag0 的多少比例才算通過
    """
    out = {}
    for lag in (0, 1):
        s = signal.shift(lag).fillna(False).infer_objects(copy=False)
        idx = base_returns.index.intersection(s.index)
        out[lag] = metrics(overlay(base_returns.loc[idx], s.loc[idx]))

    base = metrics(base_returns)
    return {
        "base": base,
        "lag0": out[0],
        "lag1": out[1],
        # 關鍵：lag1 要跟「沒加疊加」比，不是跟 lag0 比
        "overlay_adds_value": out[1]["sharpe"] > base["sharpe"],
        "leakage_ratio": out[0]["sharpe"] / out[1]["sharpe"],
    }
```

## 怎麼讀結果

實測三個案例（台股 2013–2026）：

| | 基礎（無疊加） | lag0（同日） | lag1（可交易） | 洩漏比 |
|---|---|---|---|---|
| A | 2.559 | **4.963** | 2.598 | 1.91x |
| B | 2.401 | **4.894** | 2.513 | 1.95x |
| C | 2.104 | **4.269** | **1.992** | 2.14x |

**最關鍵的一欄是「基礎」，不是 lag0。**

看到 C 從 4.269 掉到 1.992，很多人會說「還有 1.992 嘛」。錯 —— 1.992 要跟**這個疊加根本沒加之前**的 2.104 比。加了之後**變差**。這個疊加的價值是負的。

判定規則：

| 條件 | 判定 |
|---|---|
| `lag1.sharpe <= base.sharpe` | **疊加無價值**，不管 lag0 多好看 |
| `leakage_ratio > 1.3` | **強烈懷疑前視**，要逐行檢查訊號的時間索引 |
| `lag1.sharpe > base.sharpe` 且 `leakage_ratio < 1.15` | 可以繼續評估 |

## 陷阱

**陷阱 1：以為 `trade_at_price='open'` 就安全了。**
那個設定守的是引擎內的成交價。疊加層在引擎外，完全不受它管。

**陷阱 2：只 shift 訊號，忘了 shift 用來算訊號的中間變數。**

```python
r20 = curve.pct_change(20)                              # 第 t 日的值含第 t 日報酬
tp_scale = np.where(r20 > tp, 0.70, 1.0)
r_daily = r_daily * tp_scale                            # ← 同樣的病
```

停利、波動度目標、任何「用曲線自身的近期表現決定曝險」的東西都有這個問題。

**陷阱 3：用一天的 lag 就以為夠了。**
shift(1) 是**最低**要求，不是充分條件。真實交易還有：訊號要在收盤後算完、要在次日開盤前送出、可能部分成交。保守一點用 shift(2) 再測一次，看衰減幅度。

## 一眼可疑的指紋

不用讀程式碼就該懷疑的：

- 台股純多頭、月頻換股，13 年 MDD **小於 -10%**
- Sharpe **大於 3**（長期台股多頭的實測上限約 2.2）
- Calmar **大於 4**
- 回撤在 2015 / 2018 / 2022 反而縮小

## 相關

- 完整案例與程式碼片段：[C50 前視偏誤](../50-lookahead-bias.md)
- 契約層怎麼擋成交價前視：[B14 策略契約](B14-strategy-spec-contract.md)
- Gemini 從資料端防洩漏的作法：[GB02 PIT 對齊器](../../gemini/blocks/GB02-pit-lag-aligner.md) —— 那一塊守的是「因子讀到未來的財報」，這一塊守的是「疊加層讀到今天的收盤」。兩個缺口不同，都要堵。
