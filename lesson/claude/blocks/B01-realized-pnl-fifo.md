---
id: B01
title: 已實現損益 · FIFO 對沖，只認落袋現金
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: tests/test_realized.py (5 tests)
depends_on: [actual_fills.csv]
inputs: [fills]
outputs: [closed_lots, realized_by_strategy, open_lots]
updated: 2026-08-26
---

# B01 · 已實現損益（FIFO）

## 它解決什麼

賣掉的部位會從庫存表消失。庫存表消失 → 畫面上找不到 → 你以為沒發生。

真實案例：3702 大聯大 8/11 買 546 股、8/19 賣掉，**虧 NT$11,003**。這筆錢確實不在庫存裡了，但它從帳戶流出去了。而整個系統的每一個標籤都寫著「未實現損益」，所以 owner 讀了三天畫面，問出一句：「你是不是漏算了？」

**數學沒有漏 —— sleeve 曲線一直是對的**（賣出的現金回到 sleeve，報酬自然含這筆虧損）。漏的是**名字**。一個你指不出來的虧損，等於沒有發生過，你不會從它身上學到任何事。

## 契約

```python
closed_lots(fills: Sequence[Fill]) -> list[Lot]
open_lots(fills: Sequence[Fill]) -> dict[(strategy_id, stock_code), shares]
by_strategy(lots: Iterable[Lot]) -> dict[strategy_id, Summary]
as_of(lots, day) -> list[Lot]        # 只取 day 以前結算的
```

`Fill` 必要欄位：`strategy_id, stock_code, side, date, fill_price, shares, cash_out, cash_in`

`Lot` 產出：`shares, buy_date, buy_price, sell_date, sell_price, cost_twd, proceeds_twd, realized_pnl_twd, return_pct, holding_days`

**不變量**
- `realized_pnl = proceeds − cost`，其中 cost/proceeds 都來自現金欄，不是價差
- 已平倉的股數必須離開 `open_lots`，兩邊永遠不重複計算同一股
- 賣出找不到對應買進 → `raise`，不是回傳 0

## 核心：為什麼一定要 FIFO 而不是均價

均價法會算出**正確的總損益、錯誤的每一件事**：

| | FIFO | 均價 |
|---|---|---|
| 總已實現 | 對 | 對 |
| 進場價 | 真實的那一筆 | 虛構的加權平均 |
| 持有天數 | 真實 | 無法定義 |
| 一賣跨多買 | 拆成多列，各自有天數 | 壓成一列 |

你要的不是「我總共賺多少」，那個看銀行帳戶就好。你要的是**「哪一種進場活得久、哪一種活不久」**，那需要每一筆的持有期是真的。

## 陷阱

**陷阱 1：用價差算損益。**
`(賣價 − 買價) × 股數` 少算手續費和證交稅。3702 的價差答案是 −10,647，真實答案是 −11,003。差 356 元不多，但**它永遠往好的方向錯**，累積 100 筆之後你的策略評估會系統性偏樂觀。

**陷阱 2：把已實現和未實現加起來當「總報酬率」時分母搞錯。**
已實現的分母是已經退出的成本，未實現的分母是還在裡面的成本。兩者不能直接平均。系統的作法是各自報，合計只報**金額**和**對固定預算的百分比**（分母是 NT$50 萬，不是浮動成本）。

**陷阱 3：把 realized 算進「未實現損益」那張卡。**
首頁「累積未實現損益 +40,107」是券商庫存快照，**確實不含** −11,003。這不是 bug，是定義。但如果沒有另一張卡把 realized 寫出來，讀者一定會把它當成「我的總損益」。

## 程式碼

```python
def closed_lots(fills):
    books = defaultdict(deque)
    lots = []
    for fill in sorted(fills, key=lambda r: (r["date"], r.get("trade_id", ""))):
        key = (fill["strategy_id"], fill["stock_code"].strip())
        shares = float(fill["shares"])

        if fill["side"] == "BUY":
            books[key].append({
                "date": fill["date"],
                "shares": shares,
                "unit_cost": float(fill["cash_out"]) / shares,   # 含手續費
                "price": float(fill["fill_price"]),
            })
            continue

        unit_proceeds = float(fill["cash_in"]) / shares          # 已扣費稅
        remaining = shares
        while remaining > 1e-9:
            if not books[key]:
                raise RealizedError(f"{key} 賣出沒有對應買進")
            lot = books[key][0]
            matched = min(remaining, lot["shares"])
            lots.append({
                "strategy_id": key[0], "stock_code": key[1],
                "shares": matched,
                "buy_date": lot["date"], "sell_date": fill["date"],
                "cost_twd": matched * lot["unit_cost"],
                "proceeds_twd": matched * unit_proceeds,
                "realized_pnl_twd": matched * (unit_proceeds - lot["unit_cost"]),
                "return_pct": unit_proceeds / lot["unit_cost"] - 1.0,
                "holding_days": (fill["date"] - lot["date"]).days,
            })
            lot["shares"] -= matched
            remaining -= matched
            if lot["shares"] <= 1e-9:
                books[key].popleft()
    return lots
```

30 行。沒有相依套件。可以直接複製到任何專案。

## 驗證

`tests/test_realized.py`，5 個測試，每一個都在擋一種特定的自我欺騙：

1. **`test_realized_uses_settled_cash_not_price_difference`** —— 斷言答案比「價差答案」更差。如果有人偷偷改回價差法，這個測試會炸
2. **`test_the_real_3702_round_trip_reconciles_to_the_fill_book`** —— 用真實成交簿對帳，並斷言 `realized_pnl < 0`。註解寫著「3702 closed at a loss; never round it away」
3. **`test_a_sell_without_a_matching_buy_fails_closed`** —— 資料錯要炸，不要回傳 0
4. **`test_one_sell_across_two_buys_splits_into_two_lots`** —— 斷言持有天數是 `[9, 7]` 兩個不同的值
5. **`test_realized_and_unrealized_never_double_count_the_same_share`** —— 斷言平倉部位的成本已完全離開在庫帳面成本

> 測試的價值不在「證明現在是對的」，在「未來有人改壞的時候會叫」。
> 第 2 個測試會在 3702 這筆虧損被任何形式抹掉時失敗，這才是它存在的理由。

## 真實產出

| 策略 | 已實現 | 未實現 | 合計 |
|---|---:|---:|---:|
| 投信 | — | +15,330 | +15,330 |
| YOY | **−11,003** | +14,145 | **+3,142** |
| 融資 | — | −4,354 | −4,354 |
| 突破 | — | +25,073 | +25,073 |

YOY 的 +0.63% 長這樣：一筆虧 11,003 的平倉，加上還在手上的 +14,145。分開看才知道這個策略發生過什麼事。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/realized.py`
