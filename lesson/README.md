# Quant Lesson · 模組化量化系統課程與黑盒子積木庫

[![Status](https://img.shields.io/badge/status-mixed%20evidence-yellow.svg)]()
[![Multi-AI](https://img.shields.io/badge/Multi--AI-Claude%20%7C%20Gemini%20%7C%20Codex%20%7C%20OX%20%7C%20GLM--5.3-blue.svg)]()
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-orange.svg)](https://wegoliao.github.io/Quant/lesson/)

本倉庫收錄 Quant Grill Lab 中由 **Claude、Gemini、OpenAI Codex、OX** 整理的台股工程量化知識，並預留 **GLM-5.3** 獨立審查入口。證據強度不一；請以每篇有效 `status` 與 `verified_by` 判讀，不以目錄或 AI 名稱當真實性保證。

線上文件入口：[https://wegoliao.github.io/Quant/lesson/](https://wegoliao.github.io/Quant/lesson/)

---

## 目錄結構導引

- [`INDEX.md`](INDEX.md)：全站完整目錄與導引。
- [`_shared/`](_shared/)：跨 AI 通用規範、全域系統地圖與術語字典。
  - [`_shared/CROSS_AI_PROTOCOL.md`](_shared/CROSS_AI_PROTOCOL.md)：跨 AI 交互學習標準。
  - [`_shared/SYSTEM_MAP.md`](_shared/SYSTEM_MAP.md)：全系統五層架構地圖。
  - [`_shared/GLOSSARY.md`](_shared/GLOSSARY.md)：量化名詞與指標定義。
- [`gemini/`](gemini/)：**Gemini** 貢獻之課程（G00~G06）與 10 個黑盒子積木（GB01~GB10）；原始 `verified` 宣告仍需 `verified_by` 才算有效。
- [`claude/`](claude/)：**Claude (Anthropic)** 貢獻之實績觀察與成交簿對帳課程。
- [`codex/`](codex/)：**OpenAI Codex** 的全系統脈絡、證據階層、雙主線與 owner-gated execution 積木。
- [`ox/`](ox/)：**OX / ox-alpha** 對 Codex 對抗性稽核成果的獨立整理。
- [`glm-5.3/`](glm-5.3/)：GLM-5.3 專屬軌；目前只有明確標示為 Codex 撰寫的 handoff。

---

## 為什麼本教材適合 NotebookLM 與 AI 對話？

所有 Markdown 文件均遵循以下原則：
1. **結構化 Frontmatter**：包含清晰的 `author_ai`、`track` 與 `notebooklm_tags`。
2. **單目錄合輯**：每個 AI 都有 `ALL.md`，NotebookLM 不需逐頁爬站。
3. **證據降級**：宣告 `verified` 卻沒有 `verified_by` 的文件，建置時自動標為 `unvalidated`。
4. **黑盒子 interface**：積木盡量寫清輸入、輸出、不變量、失敗狀態與組裝位置；缺項視為待補，不假裝完整。
