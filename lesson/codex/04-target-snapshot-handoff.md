---
id: CDX04
title: 雙主線 seam · TargetPortfolioSnapshot 為什麼是唯一合法交接
author_ai: OpenAI Codex
track: architecture
status: verified
verified_by: 2026-08-27 focused pytest 95 passed; includes target snapshot, handoff, approval, requote, settlement
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [target-portfolio-snapshot, handoff, seam, ready-for-draft, fail-closed]
---

# TargetPortfolioSnapshot：研究與執行的 seam

## 為什麼不能直接傳「買哪些股票」

自然語言清單缺少版本、來源、時點、權重總和與 hash；執行端無法判斷它是新訊號、舊訊號、另一支 Champion，還是被人工改過的檔案。

## Interface

```text
TargetPortfolioSnapshot
├─ snapshot/champion/version/hash
├─ generated_at / data_asof / validity
├─ target positions：symbol + target_weight + attribution
├─ research evidence reference
└─ 明確排除：account、cash、shares、market quote、broker object
```

## Intake Gate

執行端收到快照後先檢查：

1. schema/version 可接受；
2. snapshot hash 與內容一致；
3. Champion/implementation hash 沒漂移；
4. `data_asof` 與有效期限未過；
5. 權重有限、非負、總和符合契約；
6. attribution 完整；
7. 沒有 broker/account 欄位滲入。

全通過只得到 `READY_FOR_DRAFT`，意思是「允許計算差額並產生提案草稿」，不是 `READY_FOR_REAL`。

## 深 module 的價值

這個 seam 讓研究 implementation 可以換 FinLab、其他資料源或不同策略族，而執行端只學一個 interface。反過來，broker、股數、盤別與 approval 的變更也不污染研究。
