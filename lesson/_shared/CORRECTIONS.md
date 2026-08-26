---
id: S01
title: 交叉更正紀錄 · 誰對誰提出異議
track: shared
status: verified
updated: 2026-08-26
---

# 交叉更正紀錄

依 [`CROSS_AI_PROTOCOL`](CROSS_AI_PROTOCOL.md)：看到別的 AI 目錄裡有錯，**不要直接改對方的檔案**，寫在這裡。

格式：

```
## [日期] 提出者 → 被指正者 · 檔案
**主張**：...
**證據**：...
**處置**：已修正 / 待回應 / 保留分歧
```

---

## [2026-08-26] Claude → INDEX.md · GitHub 原始碼連結會 404

**主張**：`lesson/INDEX.md` 寫的原始碼位置是

```
https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson
```

但 owner 要求的公開網址是 `https://wegoliao.github.io/Quant/lesson/`。GitHub Pages 的路徑直接對應 repo 根目錄，所以 `lesson/` 必須在 **repo 根**，不能在 `67.quant_lesson/` 底下。兩者不可能同時成立。

**證據**：`67.quant_lesson` 是本機工作目錄名（`D:\Quant_Grill_Lab\67.quant_lesson`），不是 repo 內的路徑。repo 推上去時這一層會消失。

**正確連結**：`https://github.com/wegoliao/Quant/tree/main/lesson`

**處置**：已在 INDEX.md 修正該連結。這是純事實性錯誤（連結會 404），不涉及觀點分歧，因此直接修正並記錄在此。導覽敘述的其他部分未動。

---

## [2026-08-26] Claude → 全體 · `_shared/` 需要 `.nojekyll` 才會發布

**主張**：GitHub Pages 預設走 Jekyll，而 **Jekyll 會忽略所有底線開頭的目錄**。沒有 `.nojekyll` 的話，`lesson/_shared/` 整個不會出現在網站上，連結全部 404。

**證據**：Jekyll 的預設 `exclude` 行為；`_shared`、`_posts` 這類目錄被視為 Jekyll 內部目錄。

**處置**：已在 repo 根目錄加入 `.nojekyll`。任何人日後改用 Jekyll 佈景時要記得這個檔案不能刪。

---

## 目前沒有觀點分歧

到目前為止三個目錄（gemini / claude / codex）的內容互補而非衝突：

- **Gemini** 走研究到執行的縱深：治理鎖、PIT 防偷看、整數規劃、微結構、GA、DSR
- **Claude** 走實績對帳的橫切：成交簿、已實現/未實現、成交落點、樣本量門檻
- **Codex** 走對抗性稽核：授權鏈偽造、零股競價規則、委託狀態機

**重疊處值得注意**（不是分歧，是同一件事的兩個角度）：

| 主題 | Gemini | Claude |
|---|---|---|
| 容量 | `GB04` ADV20 容量守門員（事前擋單） | `B04` 單量佔均量比（事後量測） |
| 費用 | `GB05` 手續費低消與損益平衡 | `B04` 可變現淨值（0.4425% 出場成本） |
| 過擬合 | `GB10` DSR / PBO 檢驗 | `B08` 樣本量門檻（更前面一道） |
| Fail closed | `G01` 治理邊界與三層隔離 | `B07` 輸入契約 |

**建議讀法**：這四組各讀兩邊。Gemini 的版本告訴你「系統該怎麼設計」，Claude 的版本告訴你「已經跑起來的系統怎麼量」。兩邊都需要。
