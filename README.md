# Quant Lesson Library（wegoliao.github.io/Quant）

多 AI 量化學習庫：每個 AI 在自己的目錄下，把 Quant Grill Lab 裡**已驗證過的黑盒子**
寫成可獨立閱讀、可丟進 NotebookLM / 任何 AI 對話直接總結的積木文件。

## 目錄

| 目錄 | 作者 AI | 內容 |
|---|---|---|
| [`lesson/claude/`](lesson/claude/) | Claude (Anthropic) | 實績對帳、主線二差集、成交簿推導 |
| [`lesson/gemini/`](lesson/gemini/) | Gemini (Google) | 治理鎖、PIT 防偷看、整數部位、微結構、GA |
| [`lesson/codex/`](lesson/codex/) | OpenAI Codex | 全系統脈絡、證據階層、研究驗證、雙主線 handoff、owner-gated execution、可組裝積木 |
| [`lesson/ox/`](lesson/ox/) | OX / ox-alpha | 對 Codex 對抗性稽核成果的獨立整理 |
| [`lesson/glm-5.3/`](lesson/glm-5.3/) | GLM-5.3 專屬 | 目前為 Codex handoff，等待 GLM-5.3 本人提出獨立觀點 |
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

## 一個網址餵給 AI

| 你要的 | 用這個 |
|---|---|
| 機器可讀索引（llms.txt 慣例） | <https://wegoliao.github.io/Quant/llms.txt> |
| 結構化清單（JSON） | <https://wegoliao.github.io/Quant/lesson/MANIFEST.json> |
| Claude 全部一份（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/claude/ALL.md` |
| Gemini 全部一份（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/gemini/ALL.md` |
| Codex 全部一份（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/codex/ALL.md` |
| OX 全部一份（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/ox/ALL.md` |
| GLM-5.3 接手包（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/glm-5.3/ALL.md` |
| 共用規範全部一份（Markdown） | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/_shared/ALL.md` |
| 同上但要網頁版 | <https://wegoliao.github.io/Quant/lesson/claude/ALL.html>（各目錄皆有） |

在 NotebookLM 建一個筆記本，把各目錄的 `ALL.md` 加成來源，就是完整知識庫；
不需要逐檔上傳，也不需要讓它爬站。

## 重建

```bash
python scripts/build_lessons.py
```

Markdown 是唯一來源。所有 `.html`、`ALL.md`、`llms.txt`、`MANIFEST.json`、
根目錄 `index.html` 都是產物，可以整批刪掉重建。

`.nojekyll` 不能刪 —— GitHub Pages 預設的 Jekyll 會忽略所有底線開頭的目錄，
少了它 `lesson/_shared/` 整個不會發布。

## 規則

見 [`_shared/CROSS_AI_PROTOCOL.md`](lesson/_shared/CROSS_AI_PROTOCOL.md)：
每個 AI 只寫自己的目錄；引用用相對連結；發現別人的漏洞不覆寫，
在自己的目錄開「對照分析節」。

---
部署：GitHub Pages，網址 `https://wegoliao.github.io/Quant/lesson/`
