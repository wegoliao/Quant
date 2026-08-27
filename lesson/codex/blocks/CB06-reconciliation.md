---
id: CB06
title: 積木 · Reconciliation 把目標、提案、委託、成交與部位串回同一證據鏈
author_ai: OpenAI Codex
track: block
status: verified
verified_by: 2026-08-27 focused pytest 95 passed; settlement review included; live reconciliation remains unvalidated
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, reconciliation, callback, fill, slippage, position]
---

# Reconciliation

## Interface

```text
inputs:
  target snapshot
  order proposal + approval receipt
  broker order callbacks
  broker deal callbacks
  position/cash snapshot
outputs:
  per-line target/proposed/submitted/filled/remaining
  fees and realized slippage when evidence exists
  unresolved broker ids and named exceptions
```

## 不變量

- 函式回傳成功不等於 broker 接受；只認 callback/ledger。
- 沒有 fill/fee/EOD price 就保留 unavailable，不補理論值。
- Common、IntradayOdd、Odd 是不同 lane，不自動 fallback 或重送。
- unresolved broker id 不自動 retry。
- 在足夠真實 fills 前，slippage model 維持 `UNVALIDATED`。

## 失敗狀態

`WAITING_CALLBACK`、`PARTIAL_FILL`、`REJECTED`、`UNRESOLVED_BROKER_ID`、`UNVALIDATED_SLIPPAGE`、`POSITION_MISMATCH`。

## 組裝位置

它是安全鏈最後一個 module，也反饋研究的成本與容量模型；但回饋必須經新版本、重新驗證，不能偷偷改歷史研究結果。
