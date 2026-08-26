# Quant · 跨 AI 量化系統課程與積木庫

**線上入口：<https://wegoliao.github.io/Quant/lesson/>**

台股四策略績效系統的拆解教學。每個 AI 一個目錄，各自寫下**驗證過的積木、踩過的陷阱、有效的提問法**，可以互相讀、互相補、互相挑錯。

純技術教學文件。不含投資建議、不含買賣訊號、不含委託路徑。

## 丟給 AI / NotebookLM

| 你要的 | 用這個 |
|---|---|
| 機器可讀索引（llms.txt 慣例） | <https://wegoliao.github.io/Quant/llms.txt> |
| 結構化清單（JSON） | <https://wegoliao.github.io/Quant/lesson/MANIFEST.json> |
| Claude 全部一份 | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/claude/ALL.md` |
| Gemini 全部一份 | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/gemini/ALL.md` |
| Codex 全部一份 | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/codex/ALL.md` |
| 跨 AI 共用規範 | `https://raw.githubusercontent.com/wegoliao/Quant/main/lesson/_shared/ALL.md` |

在 NotebookLM 建一個筆記本，把上面四份 `ALL.md` 加成來源，就有完整知識庫。

## 目錄

- [`lesson/INDEX.md`](lesson/INDEX.md) — 全站導覽
- [`lesson/_shared/`](lesson/_shared/) — 跨 AI 協定、系統地圖、術語表、交叉更正
- [`lesson/gemini/`](lesson/gemini/) — Gemini：研究到執行的縱深
- [`lesson/claude/`](lesson/claude/) — Claude：實績對帳的橫切
- [`lesson/codex/`](lesson/codex/) — Codex：對抗性稽核

## 重建

```bash
python scripts/build_lessons.py
```

Markdown 是唯一來源。所有 `.html`、`ALL.md`、`llms.txt`、`MANIFEST.json` 都是產物，可以刪掉重建。

## 來源系統

- 程式碼：<https://github.com/wegoliao/performance-accumulation-dashboard>
- 公開儀表板：<https://wegoliao.github.io/performance-accumulation-dashboard/>
