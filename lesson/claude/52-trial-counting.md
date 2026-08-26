---
id: C52
title: 試驗計數：少算 4.7 倍，門檻就低了 0.26 個 Sharpe
author_ai: Claude (Opus 5, Anthropic)
track: traps
status: verified
verified_by: evidence/honest_top5/robustness.json
updated: 2026-08-26
notebooklm_tags: [dsr, trial-count, selection-bias, deduplication]
---

# 試驗計數：少算 4.7 倍，門檻就低了 0.26 個 Sharpe

> **證據**：機械掃描 23 個實驗紀錄檔，得到 624 次試驗；repo 自己的紀錄用的是 134

## 問題

去膨脹夏普（Deflated Sharpe Ratio, Bailey & López de Prado 2014）在回答一件事：

> 就算所有策略都毫無價值，你試了 N 次之後，最好的那一個仍然會呈現多高的 Sharpe？

這個「門檻」隨 N 上升，也隨試驗結果的**離散度**上升。所以 DSR 有一個致命的操作弱點：**N 是你自己填的**。填小一點，門檻就低，你的策略就「通過」了。

## 實測

這個 repo 的實驗紀錄留在 `evidence/kiln/exp*.json`。機械掃描全部 23 個檔案：

```python
def kiln_trials():
    sh = []
    for f in sorted(glob.glob("evidence/kiln/exp*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, list):
            continue
        for row in d:
            v = row.get("sharpe_local")
            if isinstance(v, (int, float)) and np.isfinite(v):
                sh.append(float(v))
    return len(sh), np.array(sh)
```

結果：**624 次有記錄 Sharpe 的試驗**。

但 repo 自己的 `evidence/kiln/dsr.json` 寫的是 `"n_trials": 134`，另一份文件寫 253。

門檻的差距：

| 宣告的試驗數 | 選擇偏差門檻（年化 Sharpe） |
|---|---|
| 134 | 1.401 |
| 253 | 1.512 |
| **624（機械計數）** | **1.660** |

差 0.26 個 Sharpe。對一個 Sharpe 2.1 的策略來說，這決定了 DSR 是 0.92 還是 0.96 —— 也就是「通過」還是「不通過」。

用 624 重算，12 檔候選只有 1 檔通過：

| 策略 | Sharpe | DSR (n=624) | 判定 |
|---|---|---|---|
| S122 | 2.211 | **0.9595** | 通過 |
| S138 | 2.148 | 0.9435 | 差 0.007 |
| S123 | 2.097 | 0.9237 | 未過 |
| S124 | 2.027 | 0.8885 | 未過 |
| S022 | 1.756 | 0.6282 | 未過 |

## 而且 624 還是下界

`evidence/kiln/exp*.json` 只是**有留下 JSON 紀錄**的試驗。沒留紀錄的探索、手動試的參數、以及外部繼承的搜尋成本都不在裡面：

- 某檔策略是從 FinLab 公開文章移植的 —— 發表者自己試了多少次才發表這一個？未知，但不是零。**一個被發表的策略，按定義就是「看起來夠好所以被發表」的那一個。**
- 某檔繼承的策略自帶 288 次家族內試驗。

所以真實門檻只會比 1.660 更高，DSR 只會更低。這一點必須寫進報告，不能只寫「通過」。

## 兩個容易踩的技術陷阱

### 陷阱一：日頻 vs 年化的單位混用

大部分 DSR 實作內部用**每期（日頻）** Sharpe：

```python
observed = float(series.mean()) / standard_deviation      # 日頻，約 0.14
```

但你手上的試驗紀錄通常是**年化** Sharpe（1.3 ~ 2.5）。如果你把年化的 `trial_sharpes` 直接餵進去，門檻會用年化尺度算出來（1.660），再拿去和日頻的觀測值（0.139）比較 —— **每一檔的 DSR 都會是 0.0000**。

我第一次跑就中了這個。修法是先去年化：

```python
ann = np.sqrt(252)
kiln_sh = kiln_sh_ann / ann          # 門檻與觀測值同尺度
d = deflated_sharpe_ratio(ret, n_trials=n_kiln, trial_sharpes=kiln_sh.tolist())
print(d.annualised_benchmark)        # 顯示時再年化回來
```

**症狀**：所有 DSR 都是 0.0000，或所有都是 1.0000。兩者都代表尺度錯了，不是策略特別爛或特別好。

### 陷阱二：只餵存活者

```
trial_sharpes:
    Per-period Sharpes of every trial. Their VARIANCE sets the selection
    bar; supplying only the survivors understates it and inflates the result.
```

只餵通過門檻的那 20 個，離散度會被低估，門檻跟著低估。要餵**全部**試驗，包括爛的。

## 「整個 catalog 當成一次搜尋」的讀法

還有一種更嚴格的框法：如果你是從 127 檔已註冊策略裡挑出「最好的那一個」，那 N 就是 127，離散度是跨家族的離散度（大得多）。

| 讀法 | N | 門檻（年化） | 通過數 |
|---|---|---|---|
| 已宣告的搜尋活動 | 624 | 1.660 | 1 / 12 |
| 整個 catalog | 127 | **2.713** | **0 / 12** |

第二種讀法下，**沒有任何一檔通過**（最高的 S122 只有 0.0563）。

這兩種讀法都對，只是在回答不同的問題。誠實的報告要把兩個都列出來，不能只挑好看的那個。

## 還有一個會汙染分母的東西：重複註冊

用日報酬相關係數做去重時發現：

- **S123 = S139 = S141**，ρ = 1.000，績效數字完全相同 —— 同一支策略佔了三個永久編號
- S047 ≈ S048 ≈ S050，ρ 0.95–0.99

如果你用「策略數」當分母做任何統計（包括試驗計數），重複註冊會讓數字失真。去重要用報酬序列的相關係數，不能靠檔名或家族欄位。

```python
def dedup(rows, limit, rho=0.95):
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}
    for r in ranked:
        ret = load_returns(r["strategy_number"])
        dup_of = next((k for k, kr in kept_ret.items()
                       if ret.corr(kr) >= rho), None)
        if dup_of:
            dropped.setdefault(dup_of, []).append(r["strategy_number"])
            continue
        kept.append(r); kept_ret[r["strategy_number"]] = ret
        if len(kept) >= limit:
            break
    return kept, dropped
```

## 記住

> DSR 唯一能修正的是「你申報了多少次試驗」。它修正不了你沒申報的、也修正不了你有沒有偷看未來。它是必要條件，不是充分條件。

相關：[怎麼算去膨脹夏普](61-deflated-sharpe.md)、[假驗證的四種形態](51-fake-validation.md)
