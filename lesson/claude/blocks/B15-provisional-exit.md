---
id: B15
title: 暫計出場 · 一筆待確認不該讓整頁空白
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: scripts/build_dashboard.py::load_unrecorded_exits + provisional_banner
depends_on: [unrecorded_events.csv, price_history.csv]
inputs: [snapshot_diff, session_bar]
outputs: [provisional_fill, uncertainty_band]
updated: 2026-09-08
---

# B15 · 暫計出場

## 它解決什麼

庫存快照顯示某個部位不見了，但成交回報還沒到。**賣出價格是真的不知道** —— 快照只記還在手上的東西，賣出的現金流從裡面反推不出來。

成交簿正確地拒絕對帳，然後**整個儀表板建不出來**。

這是錯的失敗方式。一個待確認的數字，不該讓幾百個已經確認的數字一起消失。

## 兩種都不對的做法

**做法 A：猜一個價格填進去。**
用收盤價當成交價寫進成交簿，然後假裝它是真的。三個月後沒有人記得那筆是猜的。

**做法 B：整個 build 失敗。**
Owner 打開頁面看到 500，什麼都看不到。他不會因此更快拿到回報單，只會失去今天所有其他資訊。

## 契約

```python
load_unrecorded_exits(path) -> list[Fill]   # 帶 provisional=True 旗標
provisional_banner(exits) -> str            # 醒目、不可忽略的說明
```

`unrecorded_events.csv` 的一列：

```csv
detected_date,event,strategy_id,stock_code,stock_name,shares,
last_known_cost_twd,session_open,session_high,session_low,session_close,status,note
```

`status` 只有兩個值：`WAITING_FILL_CONFIRMATION` / `RESOLVED_BY_CONFIRMATION`

## 做法：暫計 + 不確定區間

部位**暫時以當日官方收盤價計價**，並且：

1. **旗標隨資料跑。** `provisional=True` 掛在 fill 上，FIFO 對沖時傳給 lot，每一個顯示它的表格都能標「暫計」
2. **印出當日高低區間**，那才是它真正的不確定範圍
3. **排除在所有執行品質統計之外** —— 履約落差、成交落點都不收它，因為那兩張表衡量的是執行，而這裡沒有執行紀錄可衡量
4. **頁面上寫明**收盤價不是對成交價的猜測，是一個公開、中性的替代值

```python
consideration = shares * close
fee = math.floor(consideration * 0.001425)
tax = math.floor(consideration * 0.003)
rows.append({
    "trade_id": f"PROVISIONAL-{code}-{day:%Y%m%d}",
    ...,
    "provisional": True,
    "range_low": low, "range_high": high,   # 不確定帶
})
```

## 為什麼收盤價是可接受的替代值

它有三個性質：

- **公開**：任何人都能查證，不是我編的
- **中性**：不偏向對 owner 有利或不利的方向
- **可被推翻**：回報一到就換掉，而且看得出換掉了

猜一個「大概成交在這裡」的價格，三個性質一個都沒有。

## 驗證：它真的被推翻了

合成案例 `SYN-EXIT-1`：暫計用收盤 `C`，實際回報是 `C + 7.00`。

**暫計低估了實收約 `7.00 × shares`。**

這正是這個設計要的結果 —— 暫計值**錯了**，但它：

1. 讓頁面能建
2. 全程標著「待確認」
3. 被真實資料取代，而不是被相信

> 一個標著「暫計」而且後來被證明錯了的數字，比一個沒標、剛好對了的數字，價值高得多。
> 前者訓練你去追回報單；後者訓練你相信猜測。

## 陷阱

**陷阱 1：旗標沒有傳到底。**
FIFO 對沖會產生新的 lot 物件。如果 `provisional` 沒有跟著複製過去，逐筆平倉表就會把暫計顯示成已確認。這一條要寫測試。

**陷阱 2：暫計進了執行品質統計。**
成交落點、履約落差如果收了暫計值，等於在用收盤價評估你的下單技巧 —— 那是在量測一個從未發生的行為。

**陷阱 3：`RESOLVED` 之後忘了刪暫計列。**
真實回報寫進 `actual_fills.csv` 之後，`unrecorded_events.csv` 那一列的 status 必須改掉，否則會有兩筆賣出。

## 一般化

這個模式適用於**任何「事件已確定發生、數值尚未到達」**的情況：

- 配息已除息，但入帳金額還沒收到
- 交易已成交，但費用還沒結算
- 訂單已送出，但回報延遲

規則一樣：**用一個公開中性的替代值、標記它、印出不確定範圍、排除在依賴精確值的統計之外、被真實資料取代時要看得出來。**

---

**作者：Claude (Opus 5, Anthropic)**
