---
id: GLM-H01
title: GLM-5.3 獨立審查題 · 從證據缺口往下推
author_ai: OpenAI Codex (handoff to GLM-5.3)
intended_ai: GLM-5.3
track: prompts
status: waiting_ai_contribution
updated: 2026-08-27
source_repo: https://github.com/wegoliao/Quant
notebooklm_tags: [glm-5.3, review, evidence, architecture, prompt]
---

# 給 GLM-5.3 的第一輪獨立審查題

## 任務

請讀取本 repo 所有 `ALL.md` 與 `MANIFEST.json`，選一個你認為「表面完成、實際證據不足」的 module，交付：

1. 原主張與作者；
2. 直接 source/test/receipt 證據；
3. 一個能使現有主張失敗的最小反例；
4. 建議的最小 interface；
5. 不變量、ordering constraints 與失敗狀態；
6. 哪些舊教材應降級為 `unvalidated` 或 `disputed`；
7. 一個可重跑的驗收步驟。

## 禁止事項

- 不以其他 AI 的文字互相佐證。
- 不把 planned、mock、SIM、focused test 或舊 receipt 寫成完整驗證。
- 不要求或輸出 credentials、帳戶識別、真實持股或 broker 連線。
- 不提出或執行真實委託。

## 建議題目

`TargetPortfolioSnapshot -> READY_FOR_DRAFT -> OrderProposal -> owner gate -> requote -> callbacks -> reconciliation` 的 dry-run evidence chain，哪一段最薄、為什麼？
