---
id: C01
title: 資料契約 · 四個 CSV 就是全部
author_ai: Claude (Opus 5, Anthropic)
track: context
status: verified
updated: 2026-08-26
---

# 資料契約 · 四個 CSV 就是全部

積木之間不靠函式呼叫溝通，靠**檔案格式**。這是刻意的：CSV 可以被人眼檢查、被 git diff、被任何語言讀，而且不會因為你換了框架就壞掉。

## 契約設計的三條規則

**1. 一個檔案一個事實層級。**
成交是成交、行情是行情、訊號是訊號。不要有一個「總表」把三種東西混在一起 —— 那個總表會變成沒有人敢改的東西。

**2. 每一列都要能回答「你從哪來」。**
每個 CSV 都有 `source` 欄。不是裝飾，是當數字對不起來時唯一能查的線索。

**3. 缺資料要留成缺資料。**
空字串就是空字串。不要填 0，不要 forward fill，不要「合理推估」。下游看到空值會 fail closed；看到假的 0 會安靜地算出錯的答案。

---

## `actual_fills.csv` · 成交簿（唯一不會騙人的檔案）

```csv
trade_id,strategy_id,stock_code,stock_name,side,fill_date,fill_time,fill_price,shares,consideration_twd,fee_twd,tax_twd,cash_out_twd,cash_in_twd,currency,source
SYN-001,STRATEGY_A,DEMO-A,示例股票A,BUY,2026-01-02,,100.0,100,10000,20,0,10020,0,TWD,synthetic_fixture.csv
SYN-002,STRATEGY_A,DEMO-A,示例股票A,SELL,2026-01-10,,95.0,100,9500,20,29,0,9451,TWD,synthetic_fixture.csv
```

| 欄位 | 契約 |
|---|---|
| `trade_id` | 券商委託單號。**不保證唯一** —— 不同日可能重複，需要時自己加日期後綴 |
| `strategy_id` | `TRUST` / `YOY` / `MARGIN` / `BREAKOUT`。歸屬是人工決定，同一檔可以拆給兩個策略 |
| `side` | `BUY` / `SELL` |
| `cash_out_twd` | 買進實付＝價金＋手續費 |
| `cash_in_twd` | 賣出實收＝價金−手續費−證交稅 |

**關鍵：`cash_out` / `cash_in` 才是真相，不是 `fill_price × shares`。**
所有損益計算都必須從這兩欄出發。用價差算出來的損益永遠比實際好看。

**同一檔可以掛在不同策略。** 合成例：`DEMO-B` 有 100 股在 `STRATEGY_A`、20 股在 `STRATEGY_B`。所以持股要用 `(strategy_id, stock_code)` 當 key，不能只用 `stock_code`。

---

## `price_history.csv` · 官方行情

```csv
asof_date,stock_code,open,high,low,close,volume,market,source
2026-01-10,DEMO-A,94.0,97.0,93.0,95.0,1000000,TWSE,SYNTHETIC_FIXTURE
```

- 來源：TWSE `STOCK_DAY`、TPEx `daily_close_quotes`，都是官方公開 API
- **休市、資料未發布、日期不符 → 不寫入。** 寧可缺一天，不可拿舊價冒充今天收盤
- OHLC 四個都要。只存 close 的話，分價分布（B02）和成交落點（B03）都做不了 —— 這是很多人事後才發現的坑

---

## `latest_strategy_signals.csv` · 每日策略卡

```csv
asof_date,effective_date,strategy_id,stock_code,stock_name,industry,entry_display,entry_price,close,magnitude_pct,direction,signed_return_pct,signal,source,quality_note
2026-01-10,,STRATEGY_A,DEMO-C,示例股票C,示例產業,90.0,90.0,95.0,5.6,+,5.6,抱,synthetic_strategy_card,
```

- `magnitude_pct` 恆為正、`direction` 是 `+`/`-`、`signed_return_pct` 才是帶號的。這是為了如實保存卡面（卡面只印絕對值加符號）
- `quality_note` 記錄**來源自相矛盾**的地方，例如：

```
PRINTED_PCT_VS_ENTRY_CLOSE_GAP:printed=37.8+,implied=+36.4
```

> 卡面印 37.8%，但用它自己印的進場價和收盤價回推是 36.4%。
> **不改任何一格，只標註。** 資料的矛盾是資訊，抹平它就是銷毀證據。

---

## `watchlist.csv` · 誰的行情要繼續抓

```csv
stock_code,stock_name,strategy_id,track,market,note
DEMO-C,示例股票C,STRATEGY_A,MAINLINE2,TWSE,策略卡成員；整戶零部位
DEMO-A,示例股票A,STRATEGY_A,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

這個檔案解決一個真實踩到的洞：**持股清單驅動抓取時，一檔賣掉就等於資料斷線。**

`DEMO-A` 平倉後從持股消失，行情停止更新，結果它的兩筆合成成交在成交落點分析裡完全對不到日線。加進 watchlist 後才補回來。

詳見 [`B06 watchlist 驅動抓取`](blocks/B06-watchlist-driven-fetch.md)。

---

## 為什麼是 CSV 不是資料庫

- 可以 `git diff`。資料改了什麼，PR 裡看得見
- 可以用 Excel 開。owner 要臨時補一列不需要問工程師
- 不需要 migration。加一欄就是加一欄
- 壞掉的時候看得出來哪一列壞了

代價是沒有交易、沒有索引、沒有型別。在**單人、每天幾十列**的規模下，這些代價是零，好處是全部。規模上去再換 —— 但那時候你已經知道 schema 該長什麼樣了，因為它已經被真實使用磨過一年。

---

**本目錄作者：Claude (Opus 5, Anthropic)。**
