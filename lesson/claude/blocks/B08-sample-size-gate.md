---
id: B08
title: 樣本量門檻 · 敢顯示 N/A 才是專業
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: []
inputs: [daily_returns]
outputs: [metric or None + status code]
updated: 2026-08-26
---

# B08 · 樣本量門檻

## 它解決什麼

Sharpe = 平均日報酬 / 日報酬標準差 × √252

用 11 筆日報酬算，這個公式**會給你一個數字**。它可能是 3.2，看起來很棒。它毫無意義。

標準差在小樣本下極不穩定，年化又乘上 √252 ≈ 15.9 倍，把雜訊放大成一個看起來很專業的數字。**這是量化領域最常見的自我欺騙。**

## 契約

```python
MIN_RISK_RETURN_OBS = 20

def sharpe(returns):
    if len(returns) < MIN_RISK_RETURN_OBS:
        return None
    ...

def beta(portfolio, benchmark):
    common = align(portfolio, benchmark)
    if len(common) < MIN_RISK_RETURN_OBS + 1:   # 迴歸需要多一點
        return None
    ...
```

回傳 `None`，畫面顯示 `N/A`，**並且顯示為什麼**：

```
Sharpe   N/A    WAITING_MIN_20_RETURNS (目前 11 筆)
MDD      -0.76% OK
```

## 三個設計決定

**1. 門檻是常數，不是參數。**
如果它是參數，某天有人會為了讓畫面好看而調小它。常數放在模組頂端，改它需要改程式碼、過 code review、跑測試。

**2. 不同指標門檻可以不同。**
MDD 只需要一條曲線，2 筆就能算，而且意義明確 —— 所以 MDD **不設門檻**。Sharpe、Sortino、Alpha、Beta、IR、TE 需要分布的穩定性，全部設門檻。

分清楚「需要樣本量」和「不需要樣本量」的指標，比統一設一個門檻更誠實。

**3. 狀態碼要出現在畫面上，不是只在 log。**
`WAITING_MIN_20_RETURNS` 這個字串是給**人**看的。它告訴 owner：不是壞了，是還沒到。沒有這個字串，空白的 Sharpe 欄位會被當成 bug，然後有人會「修好它」。

## 陷阱

**陷阱 1：用月報酬或週報酬繞過門檻。**
「日報酬只有 11 筆，那我用週報酬吧」—— 週報酬只會更少。改變頻率不會創造資訊。

**陷阱 2：用回測填補實績。**
「實際只有 11 天，那我把回測的 500 天接上去」—— 這會產生一條在接點處性質完全改變的曲線，而且回測那段沒有滑價、沒有費用、沒有執行失敗。

系統的作法是**兩條線並排畫，只在共同截止日比較差異**，永遠不接在一起。

**陷阱 3：把「不夠」當成「不好」。**
N/A 不是負面評價。它是「還不知道」。這兩者的差別是專業和業餘的分界線。

## 更深的一層：Deflated Sharpe

即使樣本夠了，還有第二個問題：**你試了幾種策略才找到這一個？**

如果你測了 200 個參數組合，最好的那個的 Sharpe 有很大一部分是選擇偏誤。Deflated Sharpe Ratio 就是在扣這個。

兩個實務上踩過的坑：

- **DSR 顯示 1.0000 代表有 bug**，不是代表完美。通常是試驗次數沒有正確傳入
- **長期只做多的台股組合，成分間相關性 |ρ| ≤ 0.5 是不可能達到的**。任何用這個當門檻的篩選會回傳空集合

## 一句話

> 一個誠實的 N/A，比一個不誠實的 3.2 有價值一萬倍。
> 因為 N/A 讓你繼續蒐集資料，3.2 讓你下注。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::MIN_RISK_RETURN_OBS`
