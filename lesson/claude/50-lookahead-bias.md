---
id: C50
title: 前視偏誤：一天的時差可以製造出 Sharpe 4.9
author_ai: Claude (Opus 5, Anthropic)
track: traps
status: verified
verified_by: scripts/run_honest_top5_robustness.py
updated: 2026-08-26
notebooklm_tags: [lookahead, leakage, shift, regime-overlay, verification]
---

# 前視偏誤：一天的時差可以製造出 Sharpe 4.9

> **證據**：實際重建某份宣稱 CAGR 65% 的報告，與其產出的報酬序列相關係數 = 1.0000

## 一句話

如果你的訊號用「第 t 日收盤價」判定，然後乘上「第 t 日的報酬」，你就是在下跌當天收盤前就知道要跑。這會把一個 Sharpe 2.1 的策略變成 Sharpe 4.2，而且看起來完全合理。

## 案例

一份報告宣稱三檔策略達到 CAGR 61–65%、Sharpe 4.2–4.96、最大回撤只有 -5.5% 到 -7.45%。機制是「動態狀態槓桿」：大盤在均線之上放大到 1.5x，跌破就縮到 0.2x。

問題出在這段：

```python
fast_ma = bm_close.rolling(fast_ma_d).mean()
slow_ma = bm_close.rolling(slow_ma_d).mean()
bull_regime = (bm_close > fast_ma) & (bm_close > slow_ma)

multiplier = pd.Series(np.where(bull_regime, bull_leverage, bear_exposure),
                       index=close.index)
r_lev = d_base.loc[idx] * multiplier.loc[idx]     # ← 沒有 shift(1)
```

`bull_regime` 在第 t 日用第 t 日的收盤價判定。`d_base` 在第 t 日是**第 t 日已經實現**的報酬。兩者相乘，等於你在今天收盤前就知道今天會跌，並且已經把曝險降到 0.2x。

## 測試方法：只改一件事

把訊號延後一天 —— 這是任何可交易系統的最低要求，因為你最早只能在明天開盤動作。

```python
bull = (bm > bm.rolling(20).mean()) & (bm > bm.rolling(200).mean())

for lag in (0, 1):
    b = bull.shift(lag).fillna(False)
    m = pd.Series(np.where(b, 1.5, 0.2), index=close.index)
    idx = base_returns.index.intersection(m.index)
    report(base_returns.loc[idx] * m.loc[idx])
```

實測結果（台股，2013–2026）：

| 策略 | 基礎組合（無疊加） | 同日訊號 | **落後 1 日（可交易）** |
|---|---|---|---|
| A | 33.02% / 2.559 / -16.75% | 62.93% / **4.963** / -5.51% | **31.85% / 2.598 / -11.61%** |
| B | 29.47% / 2.401 / -16.89% | 63.62% / **4.894** / -6.27% | **31.32% / 2.513 / -13.31%** |
| C | 26.67% / 2.104 / -16.88% | 60.47% / **4.269** / -7.45% | **26.14% / 1.992 / -15.67%** |

（CAGR / Sharpe / MDD）

## 最關鍵的讀法

**要跟「基礎組合」比，不是跟「同日訊號」比。**

很多人看到「延後後從 4.269 掉到 1.992」會說「還是有 1.992 嘛」。錯。1.992 要跟這個疊加**根本沒加上去之前**的 2.104 比 —— 加了槓桿疊加之後**變差了**。CAGR 也從 26.67% 掉到 26.14%。

策略 A 更明顯：Sharpe 從 2.559 動到 2.598（雜訊等級），但 CAGR 從 33.02% 掉到 31.85%。整個「動態槓桿」機制在可交易的前提下**沒有產生任何價值**。

## 怎麼一眼看出可疑

不用讀程式碼就能懷疑的指紋：

1. **MDD 太小**。台股純多頭、月頻換股，13 年 MDD 小於 -10% 是不可能的。真實範圍是 -12% 到 -50%。
2. **Sharpe 大於 3**。長期台股多頭策略的 Sharpe 上限實測在 2.2 附近。超過 3 幾乎一定是前視或成本沒算。
3. **Calmar 大於 4**。同上。
4. **回撤在市場崩盤年份反而縮小**。真策略在 2015、2018、2022 會痛。

## 另一種前視：停利也會偷看

同一份程式碼裡還有這個：

```python
r20 = curve.pct_change(20).fillna(0.0)
tp_scale = pd.Series(np.where(r20 > tp, 0.70, 1.0), index=curve.index)
r_daily = r_daily * tp_scale      # ← 第 t 日的 20 日報酬決定第 t 日的曝險
```

`curve.pct_change(20)` 在第 t 日**包含第 t 日的報酬**，卻拿來縮放第 t 日的報酬。同樣的病。

## 防呆做法

在策略契約層直接禁止同棒成交。這個 repo 的 `BacktestConfig` 就這樣做：

```python
if self.trade_at_price == "close":
    raise StrategyContractError(
        "trade_at_price='close' fills at the same bar that produced the "
        "signal. Use 'open' (next bar) or supply an explicit price frame."
    )
```

但這只擋得住「成交價」層級的前視。**疊加層（overlay / regime / 停利）的前視擋不住**，因為那是在報酬序列上做乘法，繞過了整個回測引擎。所以任何「乘在報酬上」的東西都要單獨做 shift(1) 測試。

## 記住

> 任何在 `backtest.sim` 之外、直接對報酬序列做乘法的疊加，都要被當成有罪推定，直到通過 shift(1) 測試。

相關：[C51 假驗證的四種形態](51-fake-validation.md)、[B10 shift(1) 前視測試](blocks/B10-shift1-lookahead-test.md)
