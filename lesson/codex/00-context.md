---
id: CDX00
title: OpenAI Codex 全景脈絡 · 從綠地實驗室到雙主線量化系統
author_ai: OpenAI Codex
track: context
status: verified
verified_by: D:/Quant_Grill_Lab/README.md + AGENTS.md + .planning/GRILL_DECISIONS.md + current source tree
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [codex, system-map, research, execution, governance, evidence]
---

# OpenAI Codex 在 Quant Grill Lab 做了什麼

## 一句話

Codex 把一個「想找到高 Sharpe 策略」的模糊願望，逐步變成一套會拒絕自欺的量化研發系統：研究與 broker 執行分離、每個數字要有證據、每個跨線輸出要有契約、任何不確定都用具名 `HOLD` 或 `WAITING_*` 停下來。

## 系統演化脈絡

| 階段 | 真正解決的問題 | 產出形態 |
|---|---|---|
| 綠地隔離 | 不再依賴舊 repo 的髒工作樹與隱性選擇 | 獨立 Git、獨立 `.venv`、獨立治理決策 |
| 研究骨架 | 策略不能只有一張漂亮回測圖 | deterministic runner、成本、容量、IS/OOS、receipt |
| 研究治理 | 大量搜尋會把雜訊誤認成 alpha | 預註冊、trial count、DSR/PBO、PWF、plateau、HOLD/KILL |
| 雙主線 | 研究目標與真實部位不能混成一個物件 | Mainline 1 / Mainline 2 + `TargetPortfolioSnapshot` seam |
| Owner 執行 | AI 可以準備，但不能授權真實送單 | `OrderProposal -> HumanApproval -> requote -> callbacks -> reconciliation` |
| 可觀察性 | 舊 receipt、舊 HTML、局部測試不能冒充現況 | code/hash/data_asof/run_at/status 的證據階層 |

## 兩條主線不是兩套重複系統

```text
Mainline 1：資料 -> 假說 -> position -> backtest -> 驗證 -> Champion/目標快照
                                            |
                                            v
                              TargetPortfolioSnapshot
                                            |
                                            v
Mainline 2：intake -> 真實部位差額 -> sizing -> OrderProposal -> owner gate -> 對帳
```

Mainline 1 不知道帳戶、股數、五檔或 broker；Mainline 2 不可以偷偷重選策略。兩邊只透過一個去 broker 化、可雜湊、可檢查 freshness 的快照交接。

## Codex 的主要角色

1. **治理翻譯器**：把 owner 的自然語言目標轉成可驗收決策與具名失敗狀態。
2. **實作工程師**：建立研究 runner、策略生命週期、SIM、notebook、owner console 與執行安全模組。
3. **對抗性稽核者**：不信「測試全綠」或 AI 自報完成，回到 source、fixture、receipt 與重跑結果。
4. **系統整合者**：把資料、研究、組合、執行、觀察與對帳接成單向證據鏈。
5. **止損守門員**：證據不足時輸出 `HOLD`、`NO-GO`、`WAITING_*`、`UNVALIDATED`，不拿真錢填補未知。

## 怎麼讀這個目錄

- 想理解「為什麼不能信一張回測圖」：讀 `01-evidence-hierarchy` 與 `03-validation-gates`。
- 想理解「研究如何接到執行」：讀 `02-research-mainline`、`04-target-snapshot-handoff`。
- 想理解「AI 為什麼不能送單」：讀 `05-execution-safety-chain`。
- 想把黑盒子變成積木：直接讀 `blocks/`，每篇都有 interface、輸入、輸出、不變量與失敗狀態。

## 目前誠實狀態

這套系統有大量可用模組，但不等於有可真錢運行的完整系統。最後一次完整盤點仍是：研究 Champion 證據口徑衝突，主線一 `HOLD_RESEARCH_ONLY_NO_PROMOTION`；主線二部分能力存在，但整合仍 `NO-GO REAL`。任何新報告都必須重新以當前 source、tests、hash 與 receipt 驗證，不能沿用這句話當永久現況。
