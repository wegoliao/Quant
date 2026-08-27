---
id: CDX07
title: 問題寫法 · 用 AI 拆黑盒子、驗證積木與組裝系統
author_ai: OpenAI Codex
track: prompts
status: verified
verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/06_LATEST_DUAL_MAINLINES_AND_FINLAB_CURRICULUM.md sections 7-9
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [prompts, notebooklm, learning, black-box, oral-exam]
---

# 問題寫法：不要問「解釋這個系統」

## 建立全貌

> 請把系統拆成資料、研究、驗證、組合、handoff、執行、對帳七層。每層列出 owner、輸入、輸出、interface、不變量、權限、HOLD 狀態，以及下游如何使用。

## 拆一個黑盒子

> 針對 `TargetPortfolioSnapshot`，列出它隱藏的 implementation、對 caller 暴露的最小 interface、禁止欄位、hash/freshness 規則、所有 fail-closed 狀態與一個最小正反例。

## 驗證一個積木

> 不採信文件的 `verified` 標籤。找出直接 source、測試、fixture、最近 receipt 與 hash；執行最小可重跑驗證。若缺任何一項，輸出 `UNVALIDATED` 並列出缺口。

## 組裝積木

> 我要從研究候選組成 paper-SIM 流程。請只使用已確認積木，畫出資料流與每個 seam，列出 ordering constraints；任何需要 REAL、credentials 或 owner action 的步驟停止並回傳具名等待狀態。

## 反自欺口試

> 扮演對抗性審查者。逐項挑戰 PIT、same-bar、成本、滑價、流動性、capacity、trial count、IS/OOS、PWF、regime、benchmark、correlation 與 forward evidence。每個 finding 必須附可重跑反例或明確缺少的證據。

## 比較不同 AI

> 比較 `lesson/claude`、`lesson/gemini`、`lesson/codex`、`lesson/ox` 對同一主題的 interface、不變量與證據。不要投票；以可重跑證據決定，無法決定時保留具名分歧。
