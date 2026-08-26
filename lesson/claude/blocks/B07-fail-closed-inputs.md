---
id: B07
title: Fail closed · 寧可炸掉，不要安靜地算錯
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
depends_on: []
inputs: [raw csv values]
outputs: [validated values or exception]
updated: 2026-08-26
---

# B07 · Fail closed 輸入契約

## 它解決什麼

金融資料管線最危險的不是崩潰，是**安靜地算出一個看起來合理的錯誤數字**。

崩潰你會馬上知道。錯誤數字你會拿去做決定。

## 反面教材

```python
price = float(row.get("close", 0))          # 缺資料 → 0 元
shares = int(row.get("shares") or 0)        # 缺資料 → 0 股
value = price * shares                       # 靜悄悄的 0
```

這段程式碼永遠不會拋例外，也永遠不會告訴你資料有問題。它會讓某一天的淨值變成 0，然後那天的日報酬變成 −100%，然後你的 MDD 變成 −100%，然後你以為策略爆掉了。

## 契約

```python
class InputError(ValueError):
    """Input contract violation that must fail closed."""

def required_float(value, field) -> float:
    if value is None or str(value).strip() == "":
        raise InputError(f"{field} is required")
    try:
        number = float(str(value).replace(",", ""))
    except ValueError as exc:
        raise InputError(f"{field} must be numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{field} must be finite")
    return number
```

四個檢查，每一個都擋一種真實會發生的事：

| 檢查 | 擋什麼 |
|---|---|
| 空值 | Excel 匯出的空格、券商漏欄 |
| 非數字 | `"—"`、`"N/A"`、`"停牌"` |
| 千分位 | `"1,234.5"` —— 這是台灣資料的常態 |
| `isfinite` | `inf`、`nan` —— 除以零的殘骸 |

**`field` 參數不是裝飾。** 錯誤訊息必須說出是哪一欄壞了，否則你要在 5,000 列裡面找。

## 三種缺資料，三種處理

不是所有缺資料都該炸。要分清楚：

**1. 契約違反 → 拋例外**
成交簿裡有一列沒有 `cash_out`。這是資料錯誤，繼續算下去只會產生垃圾。

**2. 已知的資料未到 → 明確狀態碼**
今天的收盤還沒發布。這是正常的，回傳 `NO_NEW_CLOSE` 或 `MARKET_DATE_MISMATCH`，**不要拿昨天的價格冒充今天**。

**3. 樣本不足 → 顯示 N/A**
只有 11 筆日報酬，算不出可信的 Sharpe。見 [`B08 樣本量門檻`](B08-sample-size-gate.md)。

```python
MIN_RISK_RETURN_OBS = 20

if len(returns) < MIN_RISK_RETURN_OBS:
    return None          # 不是 0，不是「暫時用 11 筆算」
```

## 陷阱

**陷阱 1：用 `or` 當預設值。**

```python
volume = to_float(row.get("volume")) or 0.0
```

這行有一個 bug：**真實的 0 成交量會被當成缺資料**。在停牌日這是對的行為，在其他情況下不是。要區分就要用 `is None`：

```python
volume = to_float(row.get("volume"))
volume = 0.0 if volume is None else volume
```

**陷阱 2：在迴圈裡 try/except 然後 continue。**

```python
for row in rows:
    try:
        process(row)
    except Exception:
        continue          # ← 這裡吞掉了多少列？沒有人知道
```

如果真的要容錯，**至少要數**：收集失敗的列、印出數量、超過閾值就整批失敗。

**陷阱 3：把驗證寫在畫面渲染裡。**
驗證要在**載入時**做，不是在畫圖時。否則同一份壞資料會在不同的圖表裡表現出不同的症狀，你會以為是畫圖的 bug。

## 一句話

> 一個會炸的管線，你會修它。
> 一個會安靜算錯的管線，你會信它。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::required_float`
