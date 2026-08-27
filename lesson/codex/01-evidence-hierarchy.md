---
id: CDX01
title: 證據階層 · 為什麼檔案存在、測試通過與研究結論是三件事
author_ai: OpenAI Codex
track: validation
status: verified
verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md section 6
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [evidence, receipt, hash, data-asof, reproducibility, audit]
---

# 證據階層

## 核心問題

量化專案最常見的假完成，不是程式完全沒寫，而是把不同強度的證據混成一句「完成了」。

```text
強  當前 checkout 的可重跑 code + focused/full tests + hash + 新 receipt
 |  當次原始 evidence（metrics JSON、equity CSV、broker callback ledger）
 |  根據原始 evidence 產生的報告
弱  handoff、prompt、白皮書、舊截圖、AI 自述
```

## 三個容易混淆的命題

| 命題 | 它只證明什麼 | 不能推出什麼 |
|---|---|---|
| 檔案存在 | 有人曾寫過這個 artifact | 程式可跑、數字仍新鮮 |
| focused tests 綠 | 被選中的行為符合斷言 | 全庫整合、資料正確、真實市場可成交 |
| 報告寫 PASS | 報告作者做出該判斷 | 來源、參數、資料、trial count 都一致 |

## 一份可用證據的最小 interface

```yaml
run_at: 產生時間
data_asof: 每個資料源真正涵蓋到何時
code_hash: 執行版本
config_hash: 參數版本
data_hash: 輸入資料版本
command: 可重跑入口
status: SUCCESS | HOLD_* | WAITING_* | FAILED_*
checks: 每一關的具名結果
artifacts: metrics / equity / report / receipt
```

## 關鍵不變量

1. `run_at` 不能冒充 `data_asof`。
2. 舊 receipt 不能證明本次命令成功。
3. HTML 是呈現 adapter，不是數字的 source of truth。
4. 沒有原始 input/hash 的報告只能當線索。
5. 缺資料必須變成狀態，不能默默補 0、前值或理論價。

## 組裝方式

這個積木位於所有模組之上：策略 backtest、Champion、目標快照、OrderProposal、dashboard 都必須附證據包。沒有證據包的輸出，可以看，但不可升格。
