---
id: CDX06
title: 日常營運 · 用 receipt 與具名等待狀態取代「應該有跑」
author_ai: OpenAI Codex
track: operations
status: verified
verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/daily + notebook_runtime.py + scripts/verify_finlab_runtime.py
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [daily, receipt, waiting, finlab-runtime, notebook, scheduler]
---

# 日常營運不是按 Run All 就算完成

## 一次正式 run 應該留下什麼

```text
command + interpreter/kernel
run_at + source-specific data_asof
config/code/data hashes
input inventory
named checks
output artifacts
terminal status
```

## 具名狀態的用途

- `WAITING_DATA`：輸入沒有更新到契約要求的時點。
- `WAITING_OWNER_BROKER_EVIDENCE`：需要 owner 提供的只讀 broker artifact。
- `SKIP_BUSY`：環境正被 kernel 使用；這不是更新成功。
- `SKIP_LOCK_HELD`：另一個正式研究流程持有 OS lock。
- `FAILED_WRITE_RECEIPT`：工作可能跑過，但證據沒有原子落地，仍算失敗。
- `NO_UPDATE`：只有本次所有健康檢查為零且新 receipt 寫入才算成功。

## Notebook 安全契約

可交付 notebook 應可重跑、固定 kernel、沒有秘密、沒有 saved outputs；任何 REAL 控制預設 `false`。AI 不填 credentials、不啟用 REAL switch、不執行 owner 最後動作 cell。

## 為什麼這也是量化 alpha 的一部分

如果每日資料、版本、訊號、成交與報告無法重現，你無法判斷績效來自策略、資料漂移、執行落差或人工作業。營運 receipt 是研究可證偽性的延伸。
