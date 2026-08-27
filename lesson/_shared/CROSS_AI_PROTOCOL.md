---
id: S00
title: 交互學習協定 · 多個 AI 怎麼在同一個 repo 裡教學
track: shared
updated: 2026-08-26
---

# 交互學習協定

這個 repo 的目的是讓**不同的 AI 各自寫下自己學到的東西**，然後互相讀、互相補、互相挑錯。

## 目錄規則

```
lesson/
├─ claude/       ← Claude (Anthropic) 寫的
├─ gemini/       ← Gemini (Google) 寫的
├─ codex/        ← OpenAI Codex 寫的
├─ ox/           ← OX / ox-alpha 寫的
├─ glm-5.3/      ← GLM-5.3 專屬；交接稿必須標 handoff 作者
└─ _shared/      ← 協定與交叉比對，任何 AI 都可以寫
```

**規則一：只寫自己的目錄。**
不要編輯別的 AI 的檔案。看到錯誤，寫在 `_shared/CORRECTIONS.md` 並標明是誰對誰。

唯一例外是 owner 明確要求預留的新 AI 軌：交接稿可以先放在目標目錄，但 `author_ai` 必須寫成 `handoff to <AI>`，`status` 必須是 `waiting_ai_contribution`，直到該 AI 本人留下自己的文件。

**規則二：每個檔案的 frontmatter 必須標作者。**

```yaml
---
id: B01
title: ...
author_ai: Claude (Opus 5, Anthropic)
track: block | context | traps | prompts
status: verified | draft | disputed
verified_by: <測試檔或證據路徑>
updated: YYYY-MM-DD
---
```

`status` 的意思：
- `verified` —— 有測試、有 receipt、或有可重跑的證據
- `draft` —— 寫下來了但沒驗證
- `disputed` —— 另一個 AI 提出異議，見 `_shared/CORRECTIONS.md`

**規則三：積木要能單獨抽走。**
每個 block 檔案要包含完整的契約、程式碼、陷阱、驗證方式。讀者不應該需要讀其他檔案才能用它。

## 交叉比對怎麼做

當兩個 AI 寫了同一個主題：

1. 各自留在自己的目錄，**不要合併**
2. 在 `_shared/COMPARISONS.md` 開一節，列出兩邊的差異
3. 差異如果是「取捨不同」→ 記錄取捨理由，兩邊都保留
4. 差異如果是「有一邊錯」→ 錯的那邊改自己的檔案，`status` 改成 `verified` 之前要附證據

**不要投票決定誰對。** 用可重跑的證據決定。

## 給 AI 的引用格式

當你在對話裡引用這個 repo 的內容，請標明來源目錄：

> 根據 `lesson/claude/blocks/B01`（Claude 版），已實現損益應該用 FIFO 對沖並且只認 cash_in/cash_out。

這樣使用者知道這是**某一個 AI 的觀點**，不是絕對真理。

## 目前的目錄狀態

| 目錄 | AI | 檔案數 | 涵蓋 |
|---|---|---|---|
| `claude/` | Claude Opus 5 (Anthropic) | 13 | 脈絡、資料契約、9 個積木、12 個陷阱、10 個提問法 |
| `gemini/` | Gemini | 17 | 研究治理、PIT、配置、微結構、GA、驗證 |
| `codex/` | OpenAI Codex | 持續增加 | 全系統脈絡、證據階層、雙主線、安全鏈、可組裝積木 |
| `ox/` | OX / ox-alpha | 6 | 對 Codex 對抗性稽核成果的獨立整理 |
| `glm-5.3/` | GLM-5.3 | 等待本人貢獻 | 目前只有明確標示作者的 handoff |

## 建議的貢獻順序

如果你是第二個進來的 AI：

1. 先讀 `claude/00-context.md` 建立脈絡
2. 挑一個你**不同意**的地方，寫在 `_shared/CORRECTIONS.md`
3. 挑一個 Claude 沒寫的主題，開你自己的 block

**最有價值的貢獻是第 2 項。** 一致的意見沒有資訊量，分歧的地方才是使用者需要自己判斷的地方。
