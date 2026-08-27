---
id: CDX02
title: 主線一 · 從 FinLab 資料到可否證的策略候選
author_ai: OpenAI Codex
track: research
status: verified
verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/strategy_selection + experiment_lifecycle.py
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [mainline-1, finlab, hypothesis, position, champion, research]
---

# 主線一：研究不是「找最高 Sharpe」

## Interface

```text
輸入：有時間語意的資料、預註冊假說、參數空間、成本/容量假設、benchmark
輸出：position、官方 SIM evidence bundle、驗證裁決、候選/Champion receipt
權限：只能研究與產生唯讀 target；不能讀帳戶、不能建立委託
```

## 標準流水線

1. **資料可用性**：先確認欄位、歷史長度、公告日與 refresh 狀態。
2. **假說轉 position**：因子只描述為什麼選；position 才是可回測契約。
3. **官方 SIM**：`upload=False`，保存 metrics、equity、HTML、receipt 與 hash。
4. **成本與可成交性**：費率、稅、滑價、換手、流動性、整股/零股、容量。
5. **抗過擬合**：IS/OOS、purged walk-forward、plateau、trial count、DSR/PBO。
6. **組合價值**：和 benchmark、既有策略的相關、邊際 Sharpe、容量一起看。
7. **裁決**：`PROMOTE`、`HOLD` 或 `KILL`；沒有通過者是合法結果。

## 研究模組真正隱藏的複雜度

深 module 的 interface 應該只讓研究者交付「假說 + position + preregistration」。資料對齊、成本、切分、報告、hash、receipt 由 implementation 統一處理，避免每支策略各自偷換口徑。

## 失敗狀態

- `HOLD_DATA_INSUFFICIENT`：歷史、欄位或 PIT 語意不足。
- `HOLD_RESEARCH_ONLY_NO_PROMOTION`：能研究但不能升格。
- `KILL_OVERFIT`：trial/plateau/PWF 顯示不穩健。
- `KILL_CAPACITY`：績效高但資金規模無法實現。
- `UNVALIDATED_CONFLICT`：不同 runner 或報告對同一關得出矛盾。

## 不可跨越的 seam

主線一最多輸出 `TargetPortfolioSnapshot`。`Champion`、`PROMOTE` 或高 Sharpe 都不是訂單授權。
