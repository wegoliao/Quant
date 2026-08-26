---
id: B02
title: 分價分布 · 用日線做出 volume-at-price
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: output/mainline2_receipt.json (7 names profiled)
depends_on: [price_history.csv OHLCV]
inputs: [bars]
outputs: [poc, value_area, percentile]
updated: 2026-08-26
---

# B02 · 分價分布（volume-at-price）

## 它解決什麼

「這個價格算高還是低？」

一般人用均線、用 52 週高低。這兩個都只用了收盤價，丟掉了**成交量在價格上的分布**。真正的問題不是「離最高點多遠」，是「有多少人在這個價位附近真的成交過」。

分價分布給你三個數字：

- **POC（Point of Control）**：成交量最大的那個價位
- **價值區（Value Area）**：涵蓋 70% 成交量的價格帶
- **現價分位**：有多少比例的成交量發生在現價以下

## 關鍵限制：交易所不給你逐筆分價

真正的分價表需要逐筆成交（tick）。TWSE / TPEx 的公開 API 只給**日線 OHLCV**。所以只能近似。

**唯一誠實的假設：把當天的成交量在 `[最低, 最高]` 之間均勻分攤。**

這個假設一定是錯的（實際成交會集中在某幾個價位），但它是**無偏的** —— 它不偏向任何價位。任何比它「更聰明」的分攤（例如假設集中在收盤價附近）都是在猜，而猜錯會讓 POC 系統性偏移。

> 這就是為什麼這個系統**從來不把 POC 叫做「合理價」**。
> 它是「過去半年成交量最大的價位」，句號。用日線近似算出來的東西，沒有資格承擔規範性的名字。

## 契約

```python
volume_profile(bars, bins=44) -> {
    "low", "high", "edges", "volume",     # 直方圖本體
    "poc", "poc_index",                   # 最大量價位
    "value_low", "value_high",            # 70% 量能帶
    "total", "bars", "first", "last",     # 稽核用
}
percentile_of(profile, price) -> float    # 0..1，price 以下的量佔比
```

`bars` 需要 `low, high, close, volume`。**只有 close 是做不出來的** —— 這是很多人存資料時省掉 OHLC，事後才發現的坑。

## 演算法

**第一步：分攤。** 對每根日線，把成交量按重疊比例分給每個價格 bin。

```python
for bar in bars:
    span = bar["high"] - bar["low"]
    if span <= 0 or bar["volume"] <= 0:
        # 一字板／無量：整筆塞進收盤價那格
        index = min(int((bar["close"] - low) / width), bins - 1)
        volume[max(index, 0)] += bar["volume"]
        continue
    for index in range(bins):
        overlap = min(edges[index + 1], bar["high"]) - max(edges[index], bar["low"])
        if overlap > 0:
            volume[index] += bar["volume"] * overlap / span
```

**第二步：價值區。** 從 POC 出發，每次往量比較大的那一側擴一格，直到累積 70%。

```python
poc_index = max(range(bins), key=lambda i: volume[i])
low_index = high_index = poc_index
covered = volume[poc_index]
while covered < total * 0.70 and (low_index > 0 or high_index < bins - 1):
    below = volume[low_index - 1] if low_index > 0 else -1.0
    above = volume[high_index + 1] if high_index < bins - 1 else -1.0
    if above >= below:
        high_index += 1;  covered += volume[high_index]
    else:
        low_index -= 1;   covered += volume[low_index]
```

**第三步：分位。** 線性內插，不要只回傳所在 bin 的編號 —— bin 邊界會造成鋸齒。

```python
def percentile_of(profile, price):
    if price <= profile["low"]:  return 0.0
    if price >= profile["high"]: return 1.0
    below = 0.0
    for i, edge in enumerate(profile["edges"][:-1]):
        upper = profile["edges"][i + 1]
        if price >= upper:
            below += profile["volume"][i]
        elif price > edge:
            below += profile["volume"][i] * (price - edge) / (upper - edge)  # 內插
            break
        else:
            break
    return below / profile["total"]
```

## 陷阱

**陷阱 1：bin 數量沒有正確答案，但要固定。**
用了 44。太少（<20）看不出結構，太多（>100）每格都是雜訊。重點是**所有標的用同一個數字**，否則跨標的比較沒有意義。

**陷阱 2：一字板會讓 span=0，除以零。**
台股有漲跌停。必須有 `span <= 0` 的分支，直接把量塞進收盤價那格。

**陷阱 3：把分位當成訊號。**
「現價分位 99%」的意思是「過去半年只有 1% 的量成交在更高的位置」。它**不代表**貴、不代表該賣、不代表會回檔。它只是描述統計。真實產出裡 6213 聯茂分位 99%、POC 271.88、現價 530 —— 這在強勢突破股身上是常態，不是異常。

**陷阱 4：視窗長度會改變答案。**
6 個月和 1 年的 POC 可能差很遠。**視窗長度必須顯示在畫面上**，不能只在程式碼裡。

## 真實產出（6 個月，134 個交易日）

| 股票 | 收盤 | POC | 現價分位 | 在價值區 |
|---|---:|---:|---:|:--:|
| 1714 和桐 | 16.50 | 9.89 | 62% | 在 |
| 2030 彰源 | 23.65 | 18.36 | 99% | 外 |
| 3046 建基 | 57.20 | 57.73 | 59% | 在 |
| 3605 宏致 | 116.50 | 89.40 | 91% | 外 |
| 6213 聯茂 | 530.00 | 271.88 | 99% | 外 |
| 6570 維田 | 52.90 | 59.34 | 43% | 在 |
| 6603 富強鑫 | 26.25 | 25.69 | 70% | 在 |

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::volume_profile`
