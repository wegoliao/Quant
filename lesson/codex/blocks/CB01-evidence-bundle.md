---
id: CB01
title: 積木 · EvidenceBundle 可重跑證據包
author_ai: OpenAI Codex
track: block
status: verified
verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/experiment_lifecycle.py
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, evidence, receipt, hash, reproducibility]
---

# EvidenceBundle

## Interface

```python
EvidenceBundle(
    run_at, data_asof, command, interpreter,
    code_hash, config_hash, data_hash,
    checks, artifacts, terminal_status,
)
```

## 輸入

實際執行環境、資料截止日、設定、所有 gate 結果與輸出檔案索引。

## 輸出

一個可序列化、可雜湊、能回答「誰、何時、用什麼資料與程式得到什麼狀態」的 receipt。

## 不變量

- `run_at` 與 `data_asof` 分開。
- terminal status 非成功時不能只保留最後漂亮 artifact。
- artifact 必須能回到 hash/input；HTML 不能是唯一數字來源。
- 原子寫入失敗即 `FAILED_WRITE_RECEIPT`。

## 失敗狀態

`WAITING_DATA`、`SKIP_LOCK_HELD`、`FAILED_CHECK`、`FAILED_WRITE_RECEIPT`、`UNVALIDATED_CONFLICT`。

## 組裝位置

研究 runner、daily pipeline、notebook、dashboard、target handoff 與 reconciliation 都應回傳或引用這個積木。
