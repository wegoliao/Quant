---
id: CDX03
title: 研究驗證堆疊 · 一支策略要過哪些關才不是漂亮雜訊
author_ai: OpenAI Codex
track: validation
status: verified
verified_by: D:/Quant_Grill_Lab/deliverables/notebooklm_quant_playbook/02_RULES_WHAT_WENT_WRONG.md + 03_HOW_TO_DEVELOP.md
updated: 2026-08-27
source_repo: D:/Quant_Grill_Lab
notebooklm_tags: [walk-forward, dsr, pbo, plateau, capacity, costs, oos]
---

# 研究驗證堆疊

## Gate 不是分數加總

硬 gate 是 AND，不是平均：任何一關失敗都不能用另一個漂亮指標抵銷。

| Gate | 要回答的問題 | 常見造假方式 |
|---|---|---|
| 資料時點 | 當天真的知道這個值嗎 | 用現在分類套全歷史、先 ffill 再 rank |
| 成交語意 | 訊號後何時、什麼價能成交 | same-bar、close 訊號又用 close 成交 |
| 摩擦 | 報酬扣掉費稅與滑價後還剩多少 | 費用比例有寫但沒進 equity |
| OOS/PWF | 換期間與 regime 還活著嗎 | 只做一次 50/50 切分 |
| 多重嘗試 | 是最好的一次運氣嗎 | 不記 trial count、DSR 參數傳錯 |
| 參數高原 | 鄰近參數也有效嗎 | 只有一個尖峰 |
| 流動性容量 | 真實資金能不能部署 | 只報平均成交量，不報持倉權重與退出天數 |
| 組合邊際 | 新策略真的帶來新風險來源嗎 | 六支高度相關策略當成六條腿 |

## 建議裁決資料結構

```yaml
strategy_id: Sxxx
gates:
  pit: PASS | HOLD | KILL
  costs: PASS | HOLD | KILL
  pwf: PASS | HOLD | KILL
  multiple_testing: PASS | HOLD | KILL
  plateau: PASS | HOLD | KILL
  capacity: PASS | HOLD | KILL
verdict: PROMOTE | HOLD | KILL
reasons: [具名、可重跑]
```

## 關鍵問題寫法

不要問「這支策略好不好？」；要問：

> 在固定資料截止日、已登記 trial count、完整成本與相同 runner 下，這支策略的 full/IS/OOS/PWF、MDD、Calmar、capacity、plateau 與既有策略相關是多少？任何 gate 缺證據時回傳哪個 HOLD？
