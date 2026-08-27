---
id: CB03
title: 積木 · DecisionState 用具名狀態保存未知
author_ai: OpenAI Codex
track: block
status: verified
verified_by: D:/Quant_Grill_Lab/src/quant_grill_lab/strategy_selection/model.py + execution/target_intake_gate.py
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [block, status, hold, waiting, no-go, fail-closed]
---

# DecisionState

## Interface

```yaml
state: PROMOTE | HOLD_* | KILL_* | WAITING_* | READY_FOR_DRAFT | NO_GO_REAL
reasons: [machine-readable reason codes]
evidence_refs: [receipt/hash/path]
next_acceptable_evidence: [關閉狀態需要什麼]
authority: research | execution | owner
```

## 為什麼是積木

`None`、空字串或「看起來可用」會讓下游自行猜測；具名狀態把未知保存到 interface 上，讓下游 fail closed。

## 不變量

- `HOLD` 不是失敗，也不是 PASS；它表示缺少可判決證據。
- `READY_FOR_DRAFT` 不能自動升級 `READY_FOR_REAL`。
- `PROMOTE` 只屬研究生命週期，不能授權 broker 行為。
- 只有 owner action 能跨 owner authority seam。

## 常見錯誤

把 `PAPER_MATCHED` 當 fill、把 `SKIP_BUSY` 當更新成功、把局部 tests 綠當 REAL-ready。
