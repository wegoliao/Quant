---
id: CB05
title: 積木 · OwnerApprovalGate 把人類核准綁到不可變 batch
author_ai: OpenAI Codex
track: block
status: verified
verified_by: 2026-08-27 focused pytest 95 passed; order approval and requote included
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, approval, webauthn, hardware, single-use, expiry]
---

# OwnerApprovalGate

## Interface

```text
challenge(batch_hash, purpose, mode, owner_key, expires_at)
verify(hardware_signature, pinned_key, current_time)
consume_once(approval_id, final_batch_hash)
```

## 輸出

一個短效、單次、綁定明確 proposal/batch/purpose/mode 的 owner approval receipt。

## 不變量

- 公鑰必須預先 pin，不能相信 payload 自帶的 key。
- 文字 token、challenge code 或 AI 回覆不能替代硬體簽章。
- 到期、重播、batch 改變、purpose/mode 改變都必須拒絕。
- AI 不得呼叫 owner 最終真實動作。

## 失敗狀態

`DENY_UNPINNED_KEY`、`DENY_EXPIRED`、`DENY_REPLAY`、`DENY_BATCH_CHANGED`、`WAITING_OWNER_ACTION`。
