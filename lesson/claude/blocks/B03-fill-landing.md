---
id: B03
title: 成交落點 · 唯一能對「進場點」說的實證
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: output/mainline2_receipt.json (owner counts redacted in public lesson)
depends_on: [actual_fills.csv, price_history.csv OHLC]
inputs: [fills, bars]
outputs: [range_position, vs_close, vs_open]
updated: 2026-08-26
---

# B03 · 成交落點（fill landing）

## 它解決什麼

每個人都想知道「最適合的入場點在哪」。這是一個**預測問題**，而且沒有人有答案。

但有一個相鄰的問題是**可量測的**，而且幾乎沒有人在量：

> 你已經下的單，實際落在當天價格區間的哪裡？

把每一筆成交價放回**它自己那天的最高／最低**之間，正規化成 0..1：

```
0% = 當日最低（買到最便宜）
100% = 當日最高（買到最貴）
```

買進落點越低越省，賣出落點越高越好。這不預測任何事 —— 它衡量已經發生的執行品質。

## 為什麼這個指標比 slippage 更早可用

訊號→成交的履約落差（[B05](B05-signal-fill-slippage.md)）需要「訊號價」，而訊號價只在你有完整訊號紀錄時存在。成交落點**只需要成交簿和日線**，回溯期有多長就能算多長。

換句話說：**這是你今天就能算的東西，而且過去所有成交都算得到。**

## 契約

```python
range_position(bar, price) -> float | None   # 0..1；span==0 時回 None
fill_landings(fills, bars) -> list[Landing]
```

`Landing` 產出：`position`（區間位置）、`vs_close`（對當日收盤 %）、`vs_open`（對當日開盤 %）、`status`

**不變量**
- 找不到對應日線 → `status="NO_BAR"`、`position=None`，**不要跳過、不要當 0**
- 一字板（`high == low`）→ `None`，因為區間位置沒有定義

## 程式碼

```python
def range_position(bar, price):
    span = bar["high"] - bar["low"]
    if span <= 0:
        return None                      # 一字板：位置無定義
    return max(0.0, min(1.0, (price - bar["low"]) / span))
```

三行。整個 block 最有價值的部分不是程式碼，是**想到要算它**。

## 陷阱

**陷阱 1（真的踩到了）：平倉的股票行情會斷線。**

原本抓取宇宙來自持股清單。去識別標的 `DEMO-A` 賣掉後從持股消失 → 行情停更 → 它的**買進和賣出兩筆成交都對不到日線**。

小樣本系統把唯一的賣出弄丟，就等於完全沒有出場資料。修法見 [`B06 watchlist 驅動抓取`](B06-watchlist-driven-fetch.md)。

**陷阱 2：n=22 不能下結論。**
平均落點看起來不錯，但小型 fixture 的樣本量不足以說「執行很好」。系統應把這句話**印在頁面上**，不是藏在 README：

> 目前樣本量不足以下結論，任何「改用限價／改掛開盤」的決定都應該等樣本夠了再談。

**陷阱 3：把落點好壞當成損益好壞。**
最有價值的一個發現剛好反過來 —— 見下。

## 去識別合成產出（示意，不是 owner 帳戶）

這組小型 fixture 的買進平均落在當日區間 **40%**，賣出樣本落在 **89%**；樣本量不足以下任何交易結論。

| | 股票 | 落點 |
|---|---|---:|
| 最好 | DEMO-A | 4% |
| | DEMO-B | 12% |
| | DEMO-C | 15% |
| 最差 | DEMO-D | 82% |
| | DEMO-E | 79% |
| | DEMO-F | 68% |

**最有價值的一句話：去識別案例的虧損不是賣出執行差，而是持有期價格下跌。**

買在當日 79% 高位、賣在 89% 高位，兩邊執行都不差；損失發生在持有期間，是選股／持有期問題，不是下單技巧問題。

沒有這個指標，你會花時間去優化下單方式（限價？分批？掛開盤？），而真正的問題在完全不同的地方。**這就是量測的價值：它告訴你不要優化什麼。**

## 延伸

累積到 30 筆以上之後可以做的事（現在還不行）：

- 按策略分組：哪個策略的進場執行比較差
- 按下單時段分組：需要 `fill_time`（成交簿已經留了這一欄，目前多數是空的）
- 對照當日振幅：波動大的日子落點是不是更糟

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::range_position`
