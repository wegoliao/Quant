---
id: CB04
title: 積木 · OrderProposal 可閱讀、不可變的下單提案
author_ai: OpenAI Codex
track: block
status: verified
verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/execution/order_proposal.py
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, order-proposal, batch-hash, attribution, owner]
---

# OrderProposal

## Interface

```text
proposal_id / batch_hash / mode / expires_at
summary: order_count / gross_value / fees / reserve / warnings
lines: symbol / strategy attribution / side / shares / lot lane / limit / order type
source bindings: target_hash / holdings_asof / quote_asof / config_hash
```

## 輸入

已通過 intake 的 target、owner-attested holdings、unfilled orders、fresh quote、sizing/cost/capacity rules。

## 輸出

供 owner 讀回與核准的 immutable proposal；不是 broker order。

## 不變量

- 同股票可合併 broker 數量，但策略 attribution 不可消失。
- 每筆與總計可重算並與 batch hash 綁定。
- 缺價格、部位不確定、現金不足或 lot lane 模糊時 fail closed。

## 失敗狀態

`HOLD_POSITION_UNCERTAIN`、`HOLD_STALE_QUOTE`、`HOLD_CASH_BREACH`、`HOLD_LOT_AMBIGUOUS`。
