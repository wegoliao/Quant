# lesson/glm-5.3 · 完整合輯

作者 AI：**OpenAI Codex (handoff to GLM-5.3)**　·　檔案 2 份　·　產生於 2026-08-27

這份檔案把整個目錄串成一份，給只能吃一個 URL 的 AI 用。
每一節開頭的 `## [id] title` 對應一個獨立檔案，可以單獨抽走使用。

---

## [GLM-H00] GLM-5.3 接手入口 · 待模型本人閱讀後提出獨立觀點

*track: context · status: waiting_ai_contribution · source: lesson/glm-5.3/00-handoff-context.md*

# GLM-5.3 接手入口

這個目錄已由 owner 指定給 **GLM-5.3**，但目前內容只是 OpenAI Codex 準備的交接，不冒充 GLM-5.3 已經閱讀、驗證或同意。

## 建議先讀

1. `lesson/_shared/SYSTEM_MAP.md`：系統分層與資料流。
2. `lesson/_shared/CROSS_AI_PROTOCOL.md`：作者歸屬與證據規則。
3. `lesson/codex/ALL.md`：Codex 對整體研究、handoff、執行與未解問題的整理。
4. `lesson/claude/ALL.md`：績效與成交對帳視角。
5. `lesson/gemini/ALL.md`：研究治理與量化工程視角。
6. `lesson/ox/ALL.md`：OX 對 Codex 對抗性稽核成果的整理。

## GLM-5.3 第一份正式貢獻的 interface

```yaml
author_ai: GLM-5.3
status: draft | verified | disputed
claim: 它不同意或補充什麼
evidence: 可重跑 source/test/receipt
affected_modules: 哪些積木會受影響
proposed_change: 新 interface 或新 gate
tradeoff: 改善什麼、犧牲什麼
```

## 最有價值的起點

不要重寫摘要。優先找出一個現有教材的錯誤假設、缺失的 edge case，或一個能縮小 interface 又保留能力的 deepening 建議。

---

## [GLM-H01] GLM-5.3 獨立審查題 · 從證據缺口往下推

*track: prompts · status: waiting_ai_contribution · source: lesson/glm-5.3/01-independent-review-brief.md*

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

---
