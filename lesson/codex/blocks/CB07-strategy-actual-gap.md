---
id: CB07
title: 策略卡 vs 實際帳戶 · 八鏡頭落差診斷
author_ai: OpenAI Codex
track: block
status: verified
verified_by: D:/Quant_Grill_Lab/66.performance_accumulation_dashboard/tests/test_strategy_gap.py + output/build_receipt.json
updated: 2026-08-31
source_repo: D:/Quant_Grill_Lab/66.performance_accumulation_dashboard
notebooklm_tags: [strategy-card, actual-performance, implementation-gap, coverage, cash-drag, benchmark]
---

# CB07 · 策略卡 vs 實際帳戶

## 先把兩個黑盒子拆開

策略卡與實際帳戶不是同一種報酬序列：

| 物件 | 分子 | 分母／權重 | 包含什麼 |
|---|---|---|---|
| 策略卡 | 每檔顯示報酬 | 當日成員等權 | 訊號價到卡片現價；通常不含現金、費稅與實際成交 |
| 實際 sleeve | 可變現價值與成交現金流 | 固定策略預算 | 實際股數、成交價、閒置現金、費稅、已實現與未實現 |

所以 `實際報酬 − 卡片報酬` 是 implementation gap，但不是 alpha，也不能直接解讀成「交易做差了」。

## 積木契約

```text
analyze(
  bridge,
  latest_signals,
  actual_curves,
  card_curves,
  benchmark_curves,
  slippage_rows,
  asof,
) -> strategy_actual_gap_report
```

必要不變量：

- 每個策略的 `actual − card` 必須等於 bridge 三項加總，容許誤差小於 `1e-12`。
- 卡片有、帳戶沒有的標的只列為 `missing_codes`；不得產生 counterfactual P&L。
- 計畫進出與實際成交分開；沒有 fill 就維持 `WAITING_ACTUAL_FILL`。
- 訊號成交樣本未滿 30 筆時，只報樣本與觀察值，不下執行品質結論。
- benchmark 必須使用同一起訖日；日期對不上就回傳缺值。

## 八個診斷鏡頭

| 鏡頭 | 問題 | 需要的資料 | 能說什麼 | 不能說什麼 |
|---|---|---|---|---|
| 成員覆蓋 | 卡片成員買了幾檔？ | 卡片、在庫 | 缺席與離卡持有 | 未買標的若買了會賺多少 |
| 資金投入 | 50 萬用了多少？ | 在庫成本、預算 | 現金曝險程度 | 現金一定是錯誤 |
| 訊號到成交 | 實付相對參考價？ | 可對上的 signal/fill | 執行落點 | 最佳進場價 |
| 費稅 | 進出成本吃掉多少？ | cash in/out | 已發生成本 | 未來固定成本率 |
| 已／未實現 | 錢已落袋還是在庫？ | FIFO lot、估值 | 損益所在狀態 | 把兩種分母直接平均 |
| 貢獻 | 哪些持股貢獻最大？ | 股數、價格、預算 | 帳戶貢獻集中度 | 因果選股能力 |
| 基準 | 有沒有勝過市場？ | 同期 TAIEX、0050 | 同期相對報酬 | 長期 alpha |
| 待成交 | 哪些只是計畫？ | signal state、fills | 作業待辦與證據缺口 | 把訊號冒充成交 |

## 描述性 bridge

目前使用的 bridge 是代數恆等式：

```text
gap
= actual_return - card_return
= (deployed_weight * held_return - deployed_weight * card_return)
 + (deployed_weight - 1) * card_return
 + realized_pnl / fixed_budget
```

三項可命名為：

1. 在庫組合與進場
2. 現金／未投入
3. 已實現貢獻

它們會精確加總，但第一項混合了成員、權重、進場時點、成交價與估值成本。因此方法標籤必須是 `DESCRIPTIVE_EXACT_ALGEBRA_NOT_CAUSAL_ATTRIBUTION`。

## 去識別合成例

假設策略卡有 5 檔、顯示 +8%，帳戶只持有其中 2 檔，投入 40%，實際 sleeve +1%。正確說法是：

- 覆蓋率 2/5。
- 投入率 40%。
- implementation gap 為 −7pp。
- bridge 可指出現金與在庫組合是下一步檢查方向。

錯誤說法是：「沒買的三檔造成 −X 元損失。」因為那需要明確的下單時間、數量、成交規則與成本；現在並不存在這筆交易。

## 驗證方式

```powershell
cd D:\Quant_Grill_Lab\66.performance_accumulation_dashboard
..\.venv\Scripts\python.exe -m pytest -q tests\test_strategy_gap.py
..\.venv\Scripts\python.exe scripts\build_dashboard.py
```

驗收時同時檢查：代數恆等式、缺席標的不產生假損益、共同日期 benchmark、樣本門檻，以及 HTML 沒有未替換模板標記。

## 可直接丟給 AI 的提問

> 請根據 strategy_actual_gap_report，依成員覆蓋、資金投入、訊號成交、費稅、已未實現、貢獻、benchmark、pending 八個鏡頭分析。先說資料口徑，再說差異；不得把卡片等權報酬當成可投資 NAV，不得替未成交標的建立假損益，也不得把描述性 bridge 寫成因果歸因。
