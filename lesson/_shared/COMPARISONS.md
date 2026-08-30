---
id: S05
title: 多 AI 交叉比對 · 同題不同積木
author_ai: OpenAI Codex
track: shared
status: verified
verified_by: lesson/claude/blocks/B01-realized-pnl-fifo.md + lesson/claude/blocks/B05-signal-fill-slippage.md + lesson/codex/blocks/CB07-strategy-actual-gap.md
updated: 2026-08-31
---

# 多 AI 交叉比對

## Claude B01/B05/B08/B09 vs Codex CB07

| 面向 | Claude 版 | Codex 版 | 怎麼一起用 |
|---|---|---|---|
| 已實現損益 | B01 深入 FIFO 與 settled cash | CB07 把 realized 放回策略卡落差 | 先用 B01 算真，再用 CB07 看它對固定預算的貢獻 |
| 訊號成交 | B05 深入單筆 slippage 定義 | CB07 只彙總可確定配對的樣本 | B05 建 ledger；CB07 顯示策略層樣本與門檻 |
| 樣本門檻 | B08 解釋為何少量樣本不能推論 | CB07 固定未滿 30 為不足 | 以 B08 理解限制，以 CB07 在 UI 強制揭露 |
| 主線二 | B09 從策略卡減去整戶持股 | CB07 分 covered、missing、stale、planned | B09 產生追蹤名單；CB07 避免把 missing 算成假損益 |
| 整體落差 | 分散在四個專門積木 | 八鏡頭與精確代數 bridge | 專題診斷讀 Claude；owner 總覽讀 Codex |

兩邊沒有互相取代。Claude 版較適合打開單一黑盒；Codex 版較適合把多個已驗證積木接成可稽核的 owner 儀表板。代數 bridge 只是描述分類，不是因果模型，這是 Codex 版額外加上的限制。
