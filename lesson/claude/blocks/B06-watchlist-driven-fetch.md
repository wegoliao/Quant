---
id: B06
title: watchlist 驅動抓取 · 別讓賣掉的股票資料斷線
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: [watchlist.csv, positions_ledger.csv]
inputs: [universe]
outputs: [price_history rows]
updated: 2026-08-26
---

# B06 · watchlist 驅動抓取

## 它解決什麼（一個真的踩到的洞）

抓行情要先決定「抓誰」。最自然的做法是：**抓我持有的**。

這個做法有一個安靜的失效模式：

```
你賣掉一檔 → 它離開持股 → 抓取宇宙不再包含它 → 資料從那天起斷線
```

而你**最需要它資料的時刻，正好是它剛賣掉的時候** —— 你要做出場分析、要算成交落點、要看賣掉之後它走去哪。

去識別案例：`DEMO-A` 平倉後，它的買進和賣出在成交落點分析（[B03](B03-fill-landing.md)）裡對不到日線；小樣本因此失去全部出場觀察。

## 契約

抓取宇宙 = `positions_ledger.csv` ∪ `watchlist.csv` ∪ `BENCHMARKS`

```python
def load_universe():
    seen = {}
    for row in read_csv(LEDGER_PATH):        # 持股
        seen.setdefault(row["stock_code"], {...})
    for row in read_csv(WATCHLIST_PATH):     # 追蹤清單：主線二 + 已平倉
        seen.setdefault(row["stock_code"], {...})
    return [seen[code] for code in sorted(seen)]
```

`watchlist.csv` 的 `track` 欄決定用途：

```csv
stock_code,stock_name,strategy_id,track,market,note
DEMO-C,示例股票C,STRATEGY_A,MAINLINE2,TWSE,策略卡成員；整戶零部位
DEMO-A,示例股票A,STRATEGY_A,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

- `MAINLINE2` → 進主線二頁面 + 抓行情
- `CLOSED` → **只抓行情**，不進任何頁面

`setdefault` 而非覆寫：持股清單優先，watchlist 只補沒有的。

## 為什麼分成兩個檔案而不是一個欄位

因為它們的**生命週期不同**。

`positions_ledger.csv` 是部位狀態，會被績效計算讀取。`watchlist.csv` 是觀察意圖，只被抓取程序讀取。把「我想看這檔」寫進部位檔，遲早會有人不小心把它算進淨值。

> **一個檔案一個責任。** 想在既有檔案加一個 `shares=0` 的列來偷渡追蹤清單，那是在給未來的自己埋雷。

## 陷阱

**陷阱 1：市場別（上市／上櫃）用猜的。**
`DEMO-F` 的市場別若只有人工提示仍可能錯。正確做法是使用 authoritative market mapping，或以明確 fallback 記錄結果；不要把 `market` 欄的猜測當事實：

```python
order = ["TPEX", "TWSE"] if market == "TPEX" else ["TWSE", "TPEX"]
for candidate in order:
    rows = fetch(code, candidate)
    if rows:
        return rows, candidate      # 回傳「實際解析出來的」市場別
```

**陷阱 2：抓取失敗要吵，不要安靜。**
`kept == 0` 要進 `failures` 清單並顯示。一個安靜失敗的抓取程序會讓你在三週後才發現某檔一直沒資料。

**陷阱 3：抓太多。**
7 檔 × 7 個月 × 1.8 秒延遲 ≈ 3 分鐘。宇宙每加一檔就是線性成本，而且會撞到交易所的 rate limit。**只抓你真的會看的**，這就是為什麼 watchlist 是明確清單而不是「全市場」。

## 一般化：這個模式叫什麼

這是**「意圖與狀態分離」**。

- 狀態（我持有什麼）：由事實推導，不可手動編輯
- 意圖（我想觀察什麼）：人工維護，不影響任何計算

很多資料管線的腐爛都來自把這兩者混在一起。分開之後，狀態可以隨時重算，意圖可以隨時修改，兩邊互不干擾。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/fetch_prices.py::load_universe`
