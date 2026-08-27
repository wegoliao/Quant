---
id: B05
title: 履約落差 · 策略卡報的價，帳戶付的價
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: [signal_fills.csv, price_history.csv OHLC]
inputs: [signal_ref_price, fill_price, day_bar]
outputs: [slippage_bps, range_position]
updated: 2026-08-26
---

# B05 · 訊號 → 成交 履約落差

## 它解決什麼

策略卡說「進場 97.1」。帳戶實際成交 **97.80**。

差 0.72%。聽起來沒事。但如果這個落差是**系統性的**，那麼一個年化 20% 的策略，一年進出 20 次，就會被吃掉 14 個百分點。

**這個落差在理論曲線裡看不到，在帳戶淨值裡也看不到** —— 帳戶淨值只知道你付了 97.80，不知道原本應該是 97.1。它只存在於「兩份資料的交集」，所以必須刻意去記錄。

## 契約

```python
build_slippage_ledger(path, ohlc) -> list[SlippageRow]
```

輸入 `signal_fills.csv`：

```csv
signal_date,effective_date,strategy_id,stock_code,stock_name,action,signal_ref_price,signal_basis,fill_date,fill_time,fill_price,shares,source
2026-01-09,2026-01-10,STRATEGY_A,DEMO-A,示例股票A,BUY,100.0,NEXT_OPEN,2026-01-10,10:00:00,100.8,100,synthetic_fixture
```

## 核心：方向要對

```python
# 買進成交在參考價「之上」是不利；賣出成交在「之下」是不利
direction = 1.0 if side == "BUY" else -1.0

def basis_points(reference):
    if not reference:
        return None
    return direction * (fill_price / reference - 1.0) * 10_000.0
```

**正的 bp 一律代表「對自己不利」**，不論買賣。這樣所有樣本可以直接平均，不需要分開處理。

這個小設計很重要：如果買賣用不同符號，你的統計會在買賣比例改變時漂移，而你不會發現。

## 三個參考價，全部都要記

同一筆成交要對照三個基準，因為它們回答不同的問題：

| 參考價 | 回答的問題 |
|---|---|
| `signal_ref_price` | 策略卡的報酬要打幾折 |
| 當日開盤 | 如果我無腦掛開盤會怎樣 |
| 當日收盤 | 我比「收盤價買」好還是差 |

只記一個的話，你之後想問另外兩個問題時，資料已經沒了。**紀錄的成本很低，事後補的成本是無限大。**

## 陷阱

**陷阱 1：`signal_basis` 一定要寫。**
「97.1」是收盤價？次日開盤預期？還是策略卡的進場欄？三者的落差意義完全不同。系統用 `NEXT_OPEN` 這種明確的 enum，不允許空白。

**陷阱 2：只記成交的，不記沒成交的。**
如果訊號發出但你沒買（掛單沒成交、或當天忘了），那也是履約落差的一部分 —— 而且是最貴的那一部分。**未執行的訊號要留紀錄**，否則你的落差統計只涵蓋「有成交的那些」，選擇性偏誤會讓數字好看。

（這一點目前的實作**還沒做到**，誠實記在這裡。）

**陷阱 3：樣本 1 筆就下結論。**
若目前只有一筆去識別成交，即使算出 0.8%，這個數字也**不能代表穩定執行品質**。

## 為什麼這是整個系統最重要的一張表

策略研究的終局問題只有一個：

> 這個策略能不能被執行？

回測告訴你「如果能買到訊號價會怎樣」。履約落差帳告訴你「你買不買得到」。**兩者相減才是真實可得報酬。**

大部分人的策略死在這裡，而且死了不知道 —— 因為他們從來沒有把訊號價和成交價放在同一張表上。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::build_slippage_ledger`
