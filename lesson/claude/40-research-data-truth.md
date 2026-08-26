---
id: C40
title: 資料的真相：你的回測期間由最短的那個資料集決定
author_ai: Claude (Opus 5, Anthropic)
track: context
status: verified
verified_by: evidence/honest_top5/all_metrics.json
updated: 2026-08-26
notebooklm_tags: [finlab, data-history, point-in-time, factor-alignment, sample-size]
---

# 資料的真相：你的回測期間由最短的那個資料集決定

> **證據**：直接查詢 FinLab 各資料集的 index 首尾（離線快取）

## 實測的歷史深度

| 資料集 | 起 | 迄 | 筆數 | 頻率 |
|---|---|---|---|---|
| `price:收盤價` | 2007-04-23 | 2026-08-26 | 4,756 | 日 |
| `price:成交股數` | 2007-04-23 | 2026-08-26 | 4,756 | 日 |
| `benchmark_return:發行量加權股價報酬指數` | 2003-01-02 | 2026-08-26 | 5,821 | 日 |
| `price_earning_ratio:股價淨值比` | 2010-01-04 | 2026-08-25 | 4,079 | 日 |
| `monthly_revenue:當月營收` | 2005-02-10 | 2026-08-10 | 259 | 月 |
| **`fundamental_features:*`** | **2013-Q1** | **2026-Q2** | **54** | **季** |

## 最重要的一條

**`fundamental_features` 只有 54 個季度資料點，從 2013 年開始。**

任何用到營業毛利率、營業利益率、ROE、營運現金流的策略，回測期間就被鎖死在 2013 年之後 —— 也就是說：

- 沒看過 2008 金融海嘯
- 沒看過 2011 歐債
- 有效樣本是 54 個季度觀測，不是 3,200 個交易日

第二點特別容易被忽略：你的回測曲線有 3,200 個日報酬點，看起來樣本很大，但驅動它的基本面因子只更新了 54 次。**統計檢定力來自因子的更新次數，不是報酬序列的長度。**

實測案例：某檔策略 Sharpe 2.211、MDD -11.83%、每個分段都 ≥1.95，數字很漂亮 —— 但它依賴 `fundamental_features:營業毛利率`，所以這一切都建立在 13.28 年、54 個季度觀測之上，而且完全沒看過 2008。

## 對應的取捨

如果你需要長歷史，就得放棄財報因子，只用價量。實測代價：

| | 期間 | 因子 | Sharpe | DSR |
|---|---|---|---|---|
| 有財報因子 | 13.28 年（無 2008） | 毛利、股價淨值比… | 2.211 | 0.9595 通過 |
| 純價量長歷史 | **18.36 年（含 2008）** | 價、量、營收 | 1.816 | 0.7340 未過 |

沒有免費午餐：多看 5 年（含一次真正的崩盤）換來 Sharpe 掉 0.4。哪個比較可信？看你怕的是什麼。

## 因子對齊：不是細節，會改變結論

季頻和月頻的資料要先 **ffill 到日頻再做橫斷面排名**，不能在原始頻率上排完再對齊。

原因：財報是滾動公布的，不同公司在不同日期揭露。如果你在季頻格點上排名，等於假設所有公司同時公布。

實測影響：把對齊方式從「排名後對齊」改成「ffill 到日再排名」，某檔策略的 Calmar 從 **1.496 變成 1.867**。這不是雜訊，是方法錯誤被修正。

```python
def sc(d):
    """把任何頻率的資料對齊到日頻的價格格點。"""
    if hasattr(d, "index_str_to_date"):
        d = d.index_str_to_date()
    if not isinstance(d.index, pd.DatetimeIndex):
        d.index = pd.to_datetime(d.index)
    d = d[d.index.notna()]
    if d.index.has_duplicates:
        d = d[~d.index.duplicated(keep="last")]
    return d.sort_index().reindex(index=close.index, columns=close.columns, method="ffill")

score = sc(gross_margin).rank(axis=1, pct=True) + sc(ocf).rank(axis=1, pct=True)
#      ^^^^^^^^^^^^^^^^ 先對齊                    ^^^^^^^^^^^^^^^^^^ 再排名
```

## 公布日對齊（resample_offset）

月營收在次月 10 日前公布。如果你在月底換股，你用的是「還沒公布的營收」或「已經舊了一個月的營收」。

`resample_offset="14D"` 把換股日推到月中，對齊公布節奏。實測這一項**單獨貢獻 0.358 個 Sharpe** —— 純粹是時序對齊，沒有增加任何資訊。

```python
backtest=BacktestConfig(
    resample="M",
    resample_offset="14D",   # 對齊月營收公布日，不是隨便選的
    trade_at_price="open",
)
```

這件事的意義超過它本身：**免費的 0.358 Sharpe 代表這個領域裡「對齊」比「找新因子」更值得先做。**

## 檢查清單

寫任何策略之前先問：

1. 我用到的資料集裡，最短的那個從哪年開始？→ 那就是我的回測期間。
2. 這個因子一年更新幾次？→ 那才是我的有效樣本數。
3. 它是否經歷過至少一次真正的崩盤？
4. 我有沒有在原始頻率上做橫斷面排名？（有 → 錯了）
5. 我的換股日對齊了資料的公布節奏嗎？

相關：[為什麼胃納量是真正的約束](41-capacity-is-the-constraint.md)、[成本模型](42-cost-model.md)
