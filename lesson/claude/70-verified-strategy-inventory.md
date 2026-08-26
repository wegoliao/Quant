---
id: C70
title: 已驗證積木清單：策略層
author_ai: Claude (Opus 5, Anthropic)
track: block
status: verified
verified_by: evidence/honest_top5/robustness.json
updated: 2026-08-26
notebooklm_tags: [inventory, building-blocks, capacity, correlation, deployability]
---

# 已驗證積木清單：策略層

> **證據**：127 檔已註冊策略全量 `backtest.sim` 重跑 + 四項防過擬合檢查  

這一頁是給「把黑盒子當積木拼」用的。每一格都是這次重跑量出來的，不是引用。

**這裡不放因子配方。** 放的是介面（讀哪些資料集、暴露哪些參數）、實測數字、以及能不能用的判定。

---

## 判定門檻

| 關卡 | 門檻 | 理由 |
|---|---|---|
| 胃納量 | ≥ NT$50 萬 | 低於此無法部署，見 [why-capacity-binds](41-capacity-is-the-constraint.md) |
| 去膨脹夏普 | ≥ 0.95（門檻年化 1.6595，624 次機械計數試驗） | 見 [deflated-sharpe](61-deflated-sharpe.md) |
| 最差區塊 Sharpe | > 1.0 | 四個等長非重疊區塊，任一段失效即不算穩 |
| +30bps 成本後 | > 1.0 | 真的重跑 `sim`，不是算術扣減 |

---

## 主表

| S### | 家族 | 來源 | Sharpe | CAGR | MDD | Calmar | Sortino | alpha | beta | 胃納量 | 最差區塊 | DSR | +30bps | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S122 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.211 | 21.78% | -11.83% | 1.841 | 2.225 | 16.82% | 0.283 | NT$1,077,368 | 1.946 | 0.9595 | 1.625 | **可用** |
| S138 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.148 | 22.35% | -13.88% | 1.611 | 2.292 | 16.88% | 0.309 | NT$1,876,501 | 1.692 | 0.9435 | 1.538 | 可部署，未過去膨脹 |
| S123 | QUALITY_LOW_VOL | NEW_IN_LAB | 2.097 | 26.62% | -16.88% | 1.577 | 2.193 | 19.13% | 0.41 | NT$2,278,084 | 1.644 | 0.9237 | 1.64 | 可部署，未過去膨脹 |
| S124 | QUALITY_INDUSTRY_NEUTRAL | NEW_IN_LAB | 2.027 | 27.17% | -15.09% | 1.801 | 2.161 | 19.91% | 0.404 | NT$1,976,313 | 1.908 | 0.8885 | 1.596 | 可部署，未過去膨脹 |
| S125 | PRICE_REVENUE_LONG_HISTORY | NEW_IN_LAB | 1.816 | 25.33% | -18.24% | 1.389 | 1.882 | 20.42% | 0.373 | NT$1,753,380 | 1.359 | 0.734 | 1.354 | 可部署，未過去膨脹 |
| S022 | MULTI_FACTOR | PORTED_FINLAB_PUBLISHED | 1.756 | 34.88% | -29.91% | 1.166 | 2.091 | 19.75% | 0.791 | NT$1,188,789 | 1.472 | 0.6282 | 1.377 | 可部署，未過去膨脹 |
| S148 | RADICAL_CONVEXITY | NEW_IN_LAB | 1.545 | 38.12% | -23.76% | 1.604 | 2.095 | 31.45% | 0.464 | NT$5,547,322 | 1.247 | 0.343 | 1.219 | 可部署，未過去膨脹 |
| S126 | GROWTH_HIGH_CAPACITY | NEW_IN_LAB | 1.499 | 42.28% | -36.39% | 1.162 | 1.968 | 23.99% | 1.001 | NT$8,333,758 | 0.958 | 0.2881 | 1.232 | 可部署，未過去膨脹 |
| S127 | SMALLCAP_REVENUE_MOMENTUM | INHERITED_WEGO | 2.107 | 53.69% | -24.91% | 2.156 | 3.125 | 45.84% | 0.49 | NT$70,802 | 1.756 | 0.9406 | 1.746 | **胃納不足** |
| S004 | SMALLCAP_REVENUE_MOMENTUM | INHERITED_WEGO | 1.993 | 35.17% | -29.99% | 1.173 | 2.616 | 27.49% | 0.438 | NT$79,251 | 1.359 | 0.8714 | 1.477 | **胃納不足** |
| S144 | MULTI_SLEEVE_ENSEMBLE | NEW_IN_LAB | 2.110 | 32.26% | -23.28% | 1.386 | 2.443 | 22.41% | 0.523 | NT$192,132 | 1.923 | 0.9298 | 1.54 | **胃納不足** |

---

## 各積木的介面

### S122 — QUALITY_LOW_VOL

- **結構**：四個百分位排名等權相加（品質、低波動、動量確認、估值），營收帶當篩選、大盤均線閘。無權重可擬合。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=30`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 30 檔 · 每年 287.1 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. 253 backtests were run across the campaign that produced this; every one is logged in evidence/kiln/exp*.json and all of them were fed to the deflated Sharpe calculation, which put the selection-bias bar at 1.55 ann…

### S138 — QUALITY_LOW_VOL

- **結構**：S123 的因子池上加逆波動度配置權重，單檔上限 10%。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=20`, `weight_cap=0.1`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 20 檔 · 每年 191.4 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：Island GA evolved with 400 declared trials, DSR 1.0000, Plateau pass rate 100%.…

### S123 — QUALITY_LOW_VOL

- **結構**：S122 的因子池加上現金流與中期動量，持股放寬到 40 檔換取胃納。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=40`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 40 檔 · 每年 383.0 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. Same 253-backtest campaign as S122; the selection-bias bar computed from the full trial distribution is 1.55 annualised and this reads 2.104 with DSR 0.9823. Caveats that survive that: the IS/OOS split is a plain ch…

### S124 — QUALITY_INDUSTRY_NEUTRAL

- **結構**：與 S122 同族，但橫斷面排名在各自產業內做，避免整族產業被整批買進。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `security_categories`, `fundamental_features:營業毛利率`, `fundamental_features:營業利益率`, `price_earning_ratio:股價淨值比`
- **暴露參數**：`top_n=30`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 30 檔 · 每年 287.1 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：FOUND BY SEARCH, AND THE SEARCH IS DECLARED. Same 253-backtest campaign; bar 1.55 annualised, this reads 2.033 with DSR 0.9711. TWO caveats beyond the family's shared ones (13.27 years, no 2008, chronological 50/50 split rather than purged walk-forward). First…

### S125 — PRICE_REVENUE_LONG_HISTORY

- **結構**：完全不用財報，只用價量與月營收，因此可回溯到 2007（含 2008 崩盤）。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`
- **暴露參數**：`top_n=25`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2008-04-15 ~ 2026-08-25（18.36 年）· 持股中位數 25 檔 · 每年 226.5 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：DOES NOT CLEAR DEFLATION AND IS FILED ANYWAY. DSR 0.9250 against a 0.95 threshold on the declared 253-trial campaign, verdict INDISTINGUISHABLE_FROM_SEARCH. It is registered as the family's long-history control, NOT as a deployable strategy, and nothing here s…

### S022 — MULTI_FACTOR

- **結構**：四個因子各自百分位排名相加，來自 FinLab 公開文章，非本專案原創。
- **來源**：`PORTED_FINLAB_PUBLISHED`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `fundamental_features:ROE稅後`
- **暴露參數**：`min_revenue_growth=10.0`, `max_revenue_growth=150.0`, `sustain_months=3`, `momentum_days=60`, `volatility_days=60`, `rank_top=40`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 40 檔 · 每年 482.5 筆成交 · 中位持有 31 天
- **參數高原**：100.0% of 12 個鄰居
- **選擇偏差自述**：CLEARS 1.6 ON BOTH READINGS AND STILL FAILS THE LOT TEST. Sharpe 1.7660 local / 1.6587 FinLab, CAGR 34.88%, MDD -29.91%, capacity NT$5,026,355, 40 names, IS 1.8043 / OOS 1.7256 across 3,225 days from 2013-05-15. It is the only thing in this project to clear 1.…

### S148 — RADICAL_CONVEXITY

- **結構**：利潤率轉折 + 動量 + 高集中度 Top 6，含停利。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `price:成交股數`, `fundamental_features:營業利益率`, `fundamental_features:營業毛利率`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`
- **暴露參數**：`top_n=6`, `liquidity_floor=0.4`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-09-16 ~ 2026-08-25（12.94 年）· 持股中位數 6 檔 · 每年 56.5 筆成交 · 中位持有 30 天
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：Evolved via 5-Island Radical GA (1602 trials) with 5-Fold Purged Walk-Forward Maximin gate.…

### S126 — GROWTH_HIGH_CAPACITY

- **結構**：成長因子，刻意選大市值以換取胃納量上限。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營業毛利率`
- **暴露參數**：`top_n=20`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 20 檔
- **參數高原**：100.0% of 2 個鄰居（**鄰居數少，證據弱**）
- **選擇偏差自述**：DOES NOT CLEAR DEFLATION AND IS FILED ANYWAY, LIKE S125. DSR 0.6106 against a 0.95 threshold; at 268 declared trials the selection-bias bar is 1.416 annualised and this reads 1.496, barely above it. It is registered as the CAGR-and-capacity corner of the measu…

### S127 — SMALLCAP_REVENUE_MOMENTUM

- **結構**：小型股營收動能加停利，選最小市值那一端。
- **來源**：`INHERITED_WEGO`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`
- **暴露參數**：`rank_top=9`, `threshold='high'`, `window=60`
- **換股**：`resample='M'`, `resample_offset=None`, `trade_at_price='open'`
- **期間**：2013-06-03 ~ 2026-08-25（13.23 年）· 持股中位數 9 檔
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：CLEARS DEFLATION BUT FAILS THE OWNER'S CAPACITY FLOOR. DSR 0.9972 at 399 declared trials (bar 1.325 annualised), IS 2.025 -> OOS 2.213, 0 negative years, and 6 of 6 plateau neighbours within 0.85x -- statistically this is the strongest result in the campaign. …

### S004 — SMALLCAP_REVENUE_MOMENTUM

- **結構**：小型股營收動能（3 月營收相對 12 月），WEGO 繼承。
- **來源**：`INHERITED_WEGO`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`
- **暴露參數**：`rank_top=20`, `threshold='medium'`, `window=20`
- **換股**：`resample='M'`, `resample_offset=None`, `trade_at_price='open'`
- **期間**：2013-05-02 ~ 2026-08-25（13.31 年）· 持股中位數 20 檔
- **參數高原**：100.0% of 4 個鄰居
- **選擇偏差自述**：SEVERE AND INHERITED, NOT FIXED. (1) 288 registered trials in this family over {rank_top, rebalance, threshold, window}; any reported Sharpe must be discounted for multiple testing. (2) Scorecard PSR is reported as exactly 1.0000000000, which is not a credible…

### S144 — MULTI_SLEEVE_ENSEMBLE

- **結構**：四袖袋集成，成員兩兩相關 < 0.62。
- **來源**：`NEW_IN_LAB`
- **讀取資料集**：`etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`, `price:收盤價`, `monthly_revenue:去年同月增減(%)`, `benchmark_return:發行量加權股價報酬指數`, `fundamental_features:營運現金流`, `fundamental_features:營業毛利率`, `price_earning_ratio:股價淨值比`, `etl:market_value`, `monthly_revenue:當月營收`, `etl:adj_close`, `price_earning_ratio:本益比`, `monthly_revenue:當月營收`, `fundamental_features:營業利益成長率`, `margin_transactions:融資使用率`, `etl:adj_close`, `price:成交金額`, `etl:is_flagged_stock`
- **暴露參數**：`w_s127=0.1`, `w_s139=0.5`, `w_s004=0.3`, `w_s021=0.1`
- **換股**：`resample='M'`, `resample_offset='14D'`, `trade_at_price='open'`
- **期間**：2013-05-15 ~ 2026-08-25（13.28 年）· 持股中位數 64 檔
- **參數高原**：100.0% of 8 個鄰居
- **選擇偏差自述**：Evaluated across 87,225 weight/sleeve combinations with 5-fold Purged Walk-Forward verification.…

---

## 相關係數：哪些積木其實是同一塊

| | S122 | S138 | S144 | S127 | S123 | S124 | S004 | S125 | S022 | S148 | S048 | S126 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **S122** | 1.00 | 0.89 | 0.66 | 0.36 | 0.87 | 0.83 | 0.43 | 0.78 | 0.62 | 0.52 | 0.64 | 0.54 |
| **S138** | 0.89 | 1.00 | 0.66 | 0.34 | 0.90 | 0.82 | 0.39 | 0.79 | 0.61 | 0.52 | 0.62 | 0.54 |
| **S144** | 0.66 | 0.66 | 1.00 | 0.56 | 0.73 | 0.68 | 0.69 | 0.63 | 0.74 | 0.44 | 0.80 | 0.68 |
| **S127** | 0.36 | 0.34 | 0.56 | 1.00 | 0.38 | 0.39 | 0.61 | 0.36 | 0.45 | 0.25 | 0.55 | 0.41 |
| **S123** | 0.87 | 0.90 | 0.73 | 0.38 | 1.00 | 0.90 | 0.44 | 0.85 | 0.71 | 0.59 | 0.71 | 0.67 |
| **S124** | 0.83 | 0.82 | 0.68 | 0.39 | 0.90 | 1.00 | 0.44 | 0.81 | 0.72 | 0.59 | 0.72 | 0.68 |
| **S004** | 0.43 | 0.39 | 0.69 | 0.61 | 0.44 | 0.44 | 1.00 | 0.38 | 0.54 | 0.29 | 0.66 | 0.49 |
| **S125** | 0.78 | 0.79 | 0.63 | 0.36 | 0.85 | 0.81 | 0.38 | 1.00 | 0.70 | 0.57 | 0.67 | 0.64 |
| **S022** | 0.62 | 0.61 | 0.74 | 0.45 | 0.71 | 0.72 | 0.54 | 0.70 | 1.00 | 0.50 | 0.92 | 0.87 |
| **S148** | 0.52 | 0.52 | 0.44 | 0.25 | 0.59 | 0.59 | 0.29 | 0.57 | 0.50 | 1.00 | 0.50 | 0.55 |
| **S048** | 0.64 | 0.62 | 0.80 | 0.55 | 0.71 | 0.72 | 0.66 | 0.67 | 0.92 | 0.50 | 1.00 | 0.84 |
| **S126** | 0.54 | 0.54 | 0.68 | 0.41 | 0.67 | 0.68 | 0.49 | 0.64 | 0.87 | 0.55 | 0.84 | 1.00 |

去重門檻 ρ ≥ 0.95。實測被判為重複而移出候選的：

- `S139`, `S141` 與 `S123` 相關係數 ≥ 0.95
- `S047`, `S050` 與 `S048` 相關係數 ≥ 0.95

---

## 拼積木的規則

1. **先看相關係數，再看 Sharpe。** 前五名彼此 0.78–0.90，各配 20% 買到的是同一個因子的五種寫法。
2. **混合帳本的胃納由最緊的那一腳綁死。** 配 30% 給胃納 NT$7 萬的積木，總帳本上限就是 NT$23 萬。
3. **任何乘在報酬序列上的疊加都要先過 shift(1) 測試**，見 [lookahead](50-lookahead-bias.md)。
4. **組合本身是一次新的試驗。** 從已知通過的積木裡挑組合，是後選擇（post-selection），要重新計入試驗數。

## 重現

```bash
python scripts/run_honest_topN.py
```

```bash
python scripts/run_honest_top5_robustness.py 12
```
