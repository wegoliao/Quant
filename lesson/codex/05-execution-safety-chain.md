---
id: CDX05
title: 主線二 · Owner-gated execution 安全鏈
author_ai: OpenAI Codex
track: execution
status: verified
verified_by: 2026-08-27 focused pytest 95 passed; full-repo and REAL remain explicitly unvalidated
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [mainline-2, order-proposal, approval, requote, callback, reconciliation]
---

# 主線二：把目標變成可審查提案，不是讓 AI 下單

## 安全鏈

```text
Target Intake
  -> holdings / unfilled / net gap
  -> integer sizing + lot lane + costs + capacity
  -> OrderProposal (immutable hash)
  -> Owner read-back
  -> hardware-backed approval bound to batch/purpose/mode/expiry
  -> fresh requote and material-change check
  -> single-use consumption
  -> controlled transmit
  -> order/deal callbacks
  -> immutable reconciliation
```

## 每一段的權限

| 段 | 可以做 | 不可以做 |
|---|---|---|
| 計算 | 算 gap、股數、費用、價界 | 建立 broker order |
| 提案 | 顯示每筆與總額、hash、風險 | 當成 owner 同意 |
| 核准 | owner 對明確 batch 做硬體簽核 | 用文字「我同意」代替 |
| requote | 更新行情、檢查 material change | 偷改已核准內容 |
| transmit | owner 最後操作的受控 seam | AI 執行真實送單 |
| callback | 記錄 broker 真正接受/成交 | 用函式回傳值冒充成交 |
| reconciliation | 對 target/proposal/order/deal/position | 猜測缺少的 fill 或 fee |

## 三個必要不變量

1. Natural-language AI output 永遠不能 arm、approve、amend、cancel 或 transmit。
2. 任何價格、股數、總額、筆數或 batch hash 的重大變動都使 approval 失效。
3. 在真實 fills 尚未校準滑價模型前，預測成交價必須顯示 `UNVALIDATED`。

## 目前狀態

主線二有許多已測 module，但完整系統仍需以當前 checkout 重跑整合測試、broker callback fixture 與 reconciliation；局部綠燈不是 REAL readiness。
