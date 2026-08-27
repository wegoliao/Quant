---
id: B09
title: 推導式狀態 · 能算出來的絕不另存一份
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: [latest_strategy_signals.csv, actual_fills.csv]
inputs: [signals, fills]
outputs: [mainline2_roster]
updated: 2026-08-26
---

# B09 · 推導式狀態

## 它解決什麼

「我想追蹤那些有訊號但我沒買的股票。」

**業餘做法**：開一個 `mainline2.csv`，手動維護名單。

**問題**：這份名單有三種方式會腐爛。
- 你買了一檔，忘了從名單刪掉 → 重複計算
- 你賣光一檔，忘了加回名單 → 追蹤斷線
- 策略卡換成分股，名單沒跟上 → 追蹤了一檔已經不在策略裡的股票

三個月後這份名單和現實完全脫節，而且**沒有任何機制會告訴你**。

## 契約

不要存名單。**每次重算。**

```
主線二 = { 今日策略卡的成員 } − { 成交簿推導出的整戶持股 }
```

```python
def held_positions(fills):
    held = defaultdict(float)
    for fill in fills:
        held[fill["stock_code"]] += fill["shares"] * (1 if fill["side"] == "BUY" else -1)
    return {code: shares for code, shares in held.items() if shares > 1e-9}


def build_roster(signals, bars, held):
    roster = []
    for (strategy_id, code), signal in sorted(signals.items()):
        if code in held:           # 有部位 → 不是主線二
            continue
        roster.append({...})
    return roster
```

持股本身也是推導的 —— 從成交簿加總，不是另外存一份庫存表。

**唯一的真相是成交簿。** 其他都是它的函數。

## 效果

名單自己浮現、自己消失：

- 合成例買進 `DEMO-A` → 它隔天自動離開主線二
- 假設賣光 `DEMO-B` → 它自動回到主線二（如果還在卡上）
- 策略卡拿掉某檔 → 它自動消失，不會變成孤兒

**沒有第三個地方需要同步。** 這是這個系統最值得抄走的一個想法。

## 陷阱

**陷阱 1：`> 0` 要用 `> 1e-9`。**
浮點數加減後不會剛好等於 0。一檔完全賣光的股票可能留下 `-4.5e-16`，用 `> 0` 判斷會讓它憑空消失或憑空出現。

**陷阱 2：同一檔在不同策略。**
`DEMO-C` 同時出現在 `STRATEGY_A` 與 `STRATEGY_B` 卡上，但部位只歸屬 `STRATEGY_A`。

問題：`STRATEGY_B` 的 `DEMO-C` 算不算「沒買」？

系統的決定是**用整戶零部位當判準**（`code in held`，不看 strategy_id），因為主線二問的是「這個名字我有沒有曝險」，而曝險是整戶的。但這個決定必須寫下來，否則三個月後沒有人記得為什麼。

> **推導規則本身就是需要文件的東西。** 程式碼說明「怎麼算」，文件說明「為什麼這樣算」。

**陷阱 3：推導很慢的時候會有人想快取。**
現在 23 筆成交，重算是瞬間的事。等到 10,000 筆的時候會有人想存中間結果。

那時候的正確做法是**存快照 + 存推導版本號**，並且有一個測試比對快照和重算結果。不是放棄推導。

## 一般化

這個模式在資料庫世界叫 **derived state / materialized view**，在函數式程式設計叫 **single source of truth**。

判斷準則很簡單：

> **如果 A 可以從 B 算出來，那 A 不應該被儲存。**
> 如果非存不可（效能），那必須有一個測試證明存的和算的一樣。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::build_roster`
