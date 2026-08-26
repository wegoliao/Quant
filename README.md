# Quant Lesson Library（wegoliao.github.io/Quant）

多 AI 量化學習庫：每個 AI 在自己的目錄下，把 Quant Grill Lab 裡**已驗證過的黑盒子**
寫成可獨立閱讀、可丟進 NotebookLM / 任何 AI 對話直接總結的積木文件。

## 目錄

| 目錄 | 作者 AI | 內容 |
|---|---|---|
| [`lesson/claude/`](lesson/claude/) | Claude (Anthropic) | 實績對帳、主線二差集、成交簿推導 |
| [`lesson/gemini/`](lesson/gemini/) | Gemini (Google) | 治理鎖、PIT 防偷看、整數部位、微結構、GA |
| [`lesson/codex/`](lesson/codex/) | ox-alpha 整理 Codex (OpenAI) 的實績 | 對抗性稽核法、TWSE 零股競價規則、驗證鏈偽造、訂單狀態三聯畫、多 AI 審查工作流 |
| [`lesson/_shared/`](lesson/_shared/) | 全體共識 | 跨 AI 協議、全系統地圖、術語表 |

## 快速開始

1. 先讀 [`_shared/SYSTEM_MAP.md`](lesson/_shared/SYSTEM_MAP.md) —— 全系統架構
2. 挑一個你要解的問題，到對應 AI 目錄找積木
3. 積木之間沒有隱藏依賴，可以單獨抽走

## NotebookLM / AI 對話用法

把本 repo（或單一目錄）餵給 NotebookLM 後可直接問：

- 「請總結 codex 目錄中關於訂單狀態機的三大設計錯誤」
- 「比對 Claude C00 的主線二差集與 Codex X4 的狀態三聯畫在對帳上的分工」
- 「我想組裝一個下單前檢核器：需要哪些積木、按什麼順序？」

每篇文件的 frontmatter 都有 `notebooklm_tags` 方便檢索。

## 規則

見 [`_shared/CROSS_AI_PROTOCOL.md`](lesson/_shared/CROSS_AI_PROTOCOL.md)：
每個 AI 只寫自己的目錄；引用用相對連結；發現別人的漏洞不覆寫，
在自己的目錄開「對照分析節」。

---
部署：GitHub Pages，網址 `https://wegoliao.github.io/Quant/lesson/`
