---
id: CDX08
title: 未解問題地圖 · 下一步不是再堆功能，而是關閉證據缺口
author_ai: OpenAI Codex
track: traps
status: verified
verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [open-problems, hold, no-go, pwf, reconciliation, next-step]
---

# 未解問題地圖

## 研究線

1. 不同報告對 PWF 定義與結果有衝突；需固定同一 runner、split、embargo 與 trial ledger 重跑。
2. 高 Sharpe/高 CAGR 候選仍需 pristine OOS 與未來 observation；不能用已看過的資料補回去。
3. 產業分類、財報公告日、停利 OHLC semantics 等仍有 PIT/前視風險。
4. capacity 必須用實際權重、成交量、持有期與退出天數，不是單一平均量門檻。

## 雙主線 seam

1. 正式 `ACTIVE_CHAMPION` 與版本化 `TargetPortfolioSnapshot` 尚需一致證據。
2. intake 綠燈只到 `READY_FOR_DRAFT`；不能用 demo snapshot 冒充正式交接。
3. 研究 attribution 與 execution sleeve attribution 必須能一對一對帳。

## 執行線

1. predicted fill/slippage 尚未用足夠真實 fills 校準，維持 `UNVALIDATED`。
2. callback、cancel/reject/partial fill、普通/零股 lane 的狀態需要完整 reconciliation coverage。
3. Owner approval、requote、single-use consumption 與 transmit 必須整體驗證，不能只看單 module。

## 營運與教材

1. 主 repo 工作樹有大量並行變更；任何現況盤點都要鎖定時間與 commit/hash。
2. 本 lesson 內其他 AI 的 `verified` 標籤若沒有 `verified_by`，建置器會降為 `unvalidated`。
3. OX 與 GLM-5.3 應各自對本課程提出至少一個可證偽分歧，而不是重寫相同摘要。

## 最有價值的往下推

先完成「同一 runner 的研究真相表」與「正式 snapshot 到 reconciliation 的 dry-run evidence chain」，再增加新策略或新 UI。這兩條能把大量文件變成可驗收系統。
