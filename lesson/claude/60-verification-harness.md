---
id: C60
title: 驗證流水線：怎麼一次驗完整個策略庫
author_ai: Claude (Opus 5, Anthropic)
track: validation
status: verified
verified_by: scripts/run_honest_topN.py
updated: 2026-08-26
notebooklm_tags: [harness, backtest, metrics, reproducibility, pipeline]
---

# 驗證流水線：怎麼一次驗完整個策略庫

> **證據**：127 檔已註冊策略，15.2 分鐘跑完全量 `backtest.sim`

## 設計原則

**不引用任何既有的績效數字。** 全部重跑。

理由：既有的 evidence 檔案是好幾個 AI 在好幾天裡寫的，用的成本假設、期間、指標定義都可能不同。把它們並排比較，比較的是四種不同的東西。重跑一次，全部統一。

15 分鐘的代價換一張可比的表，划算。

## Pass 1：全量模擬

```python
for spec in registry.all_strategies():
    pos = spec.build_position()
    rep = backtest.sim(pos, **spec.backtest.as_sim_kwargs())   # 用策略自己宣告的成本
    r = active_returns(rep.creturn)
    r.to_frame("return").to_parquet(CURVES / f"{spec.strategy_number}.parquet")
    rows.append({**metrics(r), "capacity_ntd": capacity_ntd(pos), ...})
```

三個關鍵細節：

### 1. 用策略自己宣告的成本，不要統一覆蓋

```python
rep = backtest.sim(pos, **spec.backtest.as_sim_kwargs())
```

每個策略的 `BacktestConfig` 帶著自己的 `resample`、`resample_offset`、`fee_ratio`。統一覆蓋會破壞例如 `resample_offset="14D"` 這種和資料公布節奏綁定的設定。

要比較的是「各自最佳配置下的表現」，不是「在我硬塞的配置下的表現」。

### 2. 從真正開始交易的那天算起

```python
def active_returns(curve):
    r = curve.pct_change().dropna()
    nz = r[r != 0.0]
    return r.loc[nz.index[0]:] if len(nz) else r
```

`creturn` 從 1.0 開始，在第一次進場前是平的。那段平的會把 Sharpe 灌水（分母變小）、把年數灌水（CAGR 縮水）。一定要切掉。

### 3. 每檔的日報酬存成 parquet

Pass 2 的所有檢查（DSR、去重、相關係數）都建立在日報酬上。存下來，Pass 2 就不用重跑。

## 指標定義（寫死，不要有第二種算法）

```python
def metrics(r):
    c = (1.0 + r).cumprod()
    yrs = (c.index[-1] - c.index[0]).days / 365.25
    cagr = c.iloc[-1] ** (1.0 / yrs) - 1.0
    sharpe = r.mean() / r.std() * np.sqrt(252)
    down = r[r < 0]
    sortino = r.mean() / down.std() * np.sqrt(252)
    mdd = float((c / c.cummax() - 1.0).min())

    br = bench_r.reindex(r.index).fillna(0.0)      # 加權股價報酬指數
    beta = float(r.cov(br) / br.var())
    alpha_d = r.mean() - beta * br.mean()

    return {
        "cagr_pct": cagr * 100,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd_pct": mdd * 100,
        "calmar": cagr / abs(mdd),
        "alpha_ann_pct": ((1 + alpha_d) ** 252 - 1) * 100,
        "beta": beta,
    }
```

**年數一定要從實際的 index 算**，不要用寫死的常數。我驗過一份報告，CAGR 用 12.49 年算而實際是 12.89 年，結果每個 CAGR 都灌水 2.5 個百分點。

**alpha 要對「報酬指數」迴歸**，不是價格指數 —— 否則你會把股息當成 alpha。

## Pass 2：四項防過擬合檢查

### 檢查一：去重（要先做）

用日報酬相關係數，不要靠檔名或家族欄位。

```python
def dedup(rows, limit, rho=0.95):
    ranked = sorted(rows, key=lambda r: -(r["sharpe"] or 0))
    kept, kept_ret, dropped = [], {}, {}
    for r in ranked:
        ret = load_returns(r["strategy_number"])
        dup_of = next((k for k, kr in kept_ret.items()
                       if len(ret.index.intersection(kr.index)) > 252
                       and ret.corr(kr) >= rho), None)
        if dup_of:
            dropped.setdefault(dup_of, []).append(r["strategy_number"])
            continue
        kept.append(r); kept_ret[r["strategy_number"]] = ret
        if len(kept) >= limit:
            break
    return kept, dropped
```

實測抓到：三個編號指向同一支策略（ρ = 1.000），另外一組三檔 ρ 0.95–0.99。

不先去重，你的「前五名」會是同一支策略的三個版本。

### 檢查二：去膨脹夏普

見 [deflated-sharpe.md](61-deflated-sharpe.md)。重點是試驗數要**機械計數**，且注意日頻／年化的單位。

### 檢查三：參數高原

見 [parameter-plateau.md](62-parameter-plateau.md)。每個鄰居都重跑 `sim`。

### 檢查四：成本敏感度

見 [cost-model.md](42-cost-model.md)。每個檔位都重跑 `sim`。

## 分段穩定度（順手做）

```python
blocks = np.array_split(r, 4)
block_sharpes = [b.mean() / b.std() * np.sqrt(252) for b in blocks if len(b) > 60]
min_block_sharpe = min(block_sharpes)
```

這**不是**走步驗證（見 [fake-validation.md](51-fake-validation.md)），別這樣叫它。它回答的是「這條曲線有沒有某一段接近失效」。

實測有用：某檔策略整體 Sharpe 1.499 看起來還行，但最差區塊掉到 0.958 —— 有整整一個時期它幾乎失效。另一檔整體 2.211，最差區塊仍有 1.946。

## 最後一步：相關係數矩陣

```python
corr = pd.DataFrame({n: load_returns(n) for n in shortlist}).corr()
```

這一步最容易被跳過，但它常常是最重要的發現。

實測：按 Sharpe 排的前五名，彼此相關係數 0.78–0.90。**各配 20% 資金買到的是同一個因子的五種寫法，不是分散。** 真正低相關的組合是第 1、第 9、第 10 名（ρ 0.50–0.62）。

沒有這張矩陣，你會以為自己分散了。

## 完整輸出

```
evidence/honest_top5/
├── all_metrics.json        127 檔全量指標
├── curves/*.parquet        每檔日報酬
├── robustness.json         四項檢查結果
└── turnover.json           實際成交次數與持有期
```

`turnover.json` 那個是補做的 —— 我第一版算週轉率算錯了（算的是原始訊號 frame 的日變動，不是實際成交），要從 `rep.trades` 拿：

```python
rep = backtest.sim(spec.build_position(), **spec.backtest.as_sim_kwargs())
t = rep.trades
trades_per_year = len(t) / years
median_hold_days = (t["exit_date"] - t["entry_date"]).dt.days.median()
```

## 記住

> 全量重跑比挑幾檔重跑更省事，因為你不用解釋為什麼挑那幾檔。127 檔 15 分鐘，沒有理由不做。

相關：[假驗證的四種形態](51-fake-validation.md)、[已驗證積木清單](70-verified-strategy-inventory.md)
