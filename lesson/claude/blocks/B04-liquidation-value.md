---
id: B04
title: 可變現淨值 · 帳面值不是你拿得到的錢
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: [price_history.csv]
inputs: [shares, close]
outputs: [liquidation_value]
updated: 2026-08-26
---

# B04 · 可變現淨值

## 它解決什麼

`股數 × 收盤價` 是**毛值**。你賣掉拿不到那麼多，因為出場要付手續費和證交稅。

台股現股賣出成本：
- 手續費 0.1425%（券商可能打折，但保守用全額）
- 證交稅 0.3%
- 合計約 **0.4425%**

聽起來很小。但它是**單向、必然、每次都發生**的。任何一個「勝率 52%、平均賺 0.8%」的策略，扣掉這個之後就不存在了。

## 契約

```python
estimated_liquidation_value(shares: float, close: float) -> float
```

```python
def estimated_liquidation_value(shares, close):
    """Mirror the broker screen's estimated fee + 0.3% transaction tax."""
    gross = shares * close
    return gross - int(gross * 0.001425) - int(gross * 0.003)
```

**注意 `int()`。** 券商的費用是**無條件捨去到整數元**的，不是四捨五入。要跟券商畫面對得起來就必須複製這個行為 —— 這種細節是「數字對不起來」的常見來源。

## 為什麼要在每一天都用它，而不是只在最後一天

這是一個真實的 bug。原本的實作是：歷史日用毛值、最新日用淨值。結果**曲線在最後一天憑空掉了 0.44%**，看起來像當天虧損，其實是換了尺。

> **一條曲線只能有一個估值口徑。**
> 如果你改了口徑，整條線要一起改，不能只改末端。

修正後：所有日期都用可變現淨值，所以曲線的形狀是對的，起點也是對的。

## 陷阱

**陷阱 1：拿它跟券商的「未實現損益」比。**
券商庫存畫面的損益通常是**毛值**（不扣賣出費稅）。所以你的數字會系統性比券商小 0.44%。這不是錯，但必須標註口徑，否則 owner 會以為算錯了。

**陷阱 2：買進成本也要含手續費。**
成本端是 `cash_out`（價金＋手續費），賣出端是淨值。兩邊都含成本，這樣算出來的報酬才是**真的能落袋的報酬**。只扣一邊是最常見的半吊子做法。

**陷阱 3：零股和整股的費用結構不同。**
零股手續費有最低收費（通常 NT$1或20），小額交易的實際費率會遠高於 0.1425%。這個 block **不處理零股**，用在零股上會低估成本。

## 一個延伸的觀念：容量

同樣的邏輯往前推一步就是**容量**。你能買多少而不推動價格？

```python
SLOT_TWD = 50_000.0          # 50 萬 sleeve 分十檔
PARTICIPATION_CAP = 0.05     # 不超過均量 5%

slot_shares = SLOT_TWD / price
participation = slot_shares / avg_volume_20d
capacity_twd = avg_volume_20d * PARTICIPATION_CAP * price
```

去識別合成例中，`DEMO-A` 的單量佔均量 **0.40%**，`DEMO-B` 只有 **0.01%**。同一策略在兩檔上的可執行性可能完全不同，而傳統回測報告不一定會告訴你。

> **Sharpe 很高但容量只有 NT$10 萬的策略，不是好策略，是一個統計假象。**

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::estimated_liquidation_value`
