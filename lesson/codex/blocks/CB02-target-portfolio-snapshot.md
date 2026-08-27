---
id: CB02
title: 積木 · TargetPortfolioSnapshot 研究到執行的唯讀快照
author_ai: OpenAI Codex
track: block
status: verified
verified_by: 2026-08-27 focused pytest 95 passed; target snapshot and intake included
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, target, snapshot, handoff, immutable]
---

# TargetPortfolioSnapshot

## Interface

```text
identity: snapshot_id/version/hash
research binding: champion_id/version/implementation_hash/evidence_hash
time: generated_at/data_asof/valid_until
targets: symbol/target_weight/strategy attribution
```

## 禁止輸入

account id、broker object、cash、real holdings、market quote、share quantity、credential 或 order type。

## 輸出

可由 execution intake 驗證的 immutable target；不包含「怎麼下單」。

## 不變量

- 內容與 hash 一致。
- 權重有限、非負、總和符合契約。
- attribution 完整。
- snapshot 的 Champion 與 implementation 綁定。

## 失敗狀態

`HOLD_STALE_SNAPSHOT`、`HOLD_HASH_MISMATCH`、`HOLD_CHAMPION_MISMATCH`、`HOLD_ATTRIBUTION_MISSING`。

## 組裝位置

上游接 Champion receipt；下游只接 Target Intake Gate。通過後仍只有 `READY_FOR_DRAFT`。
