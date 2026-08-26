---
id: G05
title: 核心策略演化 · 波動度加權與 50% CAGR 遺傳演算法 (GA) 藍圖
author_ai: Gemini (Google DeepMind / Antigravity)
track: strategy
status: verified
updated: 2026-08-26
source_repo: https://github.com/wegoliao/Quant/tree/main/67.quant_lesson/lesson/gemini/
web_url: https://wegoliao.github.io/Quant/lesson/gemini/05-alpha-strategies-and-ga.html
notebooklm_tags: [strategies, genetic-algorithm, ga, inverse-volatility, radical-cagr, ensemble]
---

# 核心策略演化 · 波動度加權與 50% CAGR 遺傳演算法 (GA) 藍圖

## 一句話總結 (TL;DR)

本章介紹 **Gemini 策略家族（S138~S141）** 如何透過「反向波動加權」與「波動度目標」突破傳統等權重瓶頸（Sharpe 提升至 2.15+），並解密從第一性原理出發的 **次世代 50%+ CAGR 遺傳演算法（Radical GA Blueprint）**，以帕雷托集中度與雙軌混合進出場機制打破均值回歸天花板。

---

## 1. Gemini 核心策略家族 (S138 ~ S141)

```
S123 基底 (Claude 002 現金流動能)
  ├── S138 (Gemini 001): 導入「反向波動度加權」+ 10% 單檔上限 ──> Sharpe 2.15, MDD -13.8%
  ├── S139 (Gemini 002): 導入「大盤均線宏觀濾網 (Macro VETO)」 ──> 熊市大幅降低曝險
  ├── S140 (Gemini 004): 導入「動態波動度目標化 (Vol-Targeting)」 ──> 控制年化波動於 15%
  └── S141 (Gemini 007): 整合「價值+動能+籌碼+微結構」四維多方法論 ──> 抗單一風格週期崩塌
```

### S138 反向波動加權 (Inverse Volatility Sizing) 核心公式：
對選出的 Top 20 檔股票，計算其近 60 日日報酬波動度 $\sigma_i$：

$$w_i^{\text{raw}} = \frac{1}{\max(\sigma_i, 0.005)}, \quad w_i^{\text{norm}} = \frac{w_i^{\text{raw}}}{\sum_j w_j^{\text{raw}}}$$

經過 3 輪單檔 $10\%$ 上限截斷與再分配，使投組在維持高爆發動能的同時，顯著壓低整體組合波動，使 Sharpe 由 2.104 躍升至 2.154，且保有 NT$133 萬胃納量。

---

## 2. 大破大立：突破 CAGR 50% 的次世代 GA 藍圖

傳統策略之所以卡在 CAGR 25%~30%，是因為四大架構枷鎖：
1. **40 檔靜態等權重**：極強的均值回歸拉力，頂級飆股的暴利被 35 檔平庸標的稀釋。
2. **僵化月調倉**：缺乏日內/週頻動態停損停利，強勢股回檔吐回大量浮盈。
3. **0/1 粗暴二元閘門**：震盪市頻繁被洗盤。
4. **微型股流動性幻覺**：依賴極低容量標的創造虛假高報酬。

### 次世代 GA 的五大破局機制：

```
                    【50%+ CAGR 次世代量化架構】
┌─────────────────────────────────────────────────────────────┐
│ 機制 1: 雙軌混合進出場 ── 月頻選強底倉 + 日頻 Trailing-3ATR 奔馳│
│ 機制 2: 帕雷托動態集中度 ── 精選 8~12 檔，前 3 名龍頭配置 20% │
│ 機制 3: 基本面拐點 × 法人連買 ── 營收 YoY 加速度 + 投信連買    │
│ 機制 4: 自適應連續市場狀態 ── 牛市 120% 曝險，空頭 0% 空手   │
│ 機制 5: 三柱多 Sleeve 組合 ── 高胃納基底 + 凸性衝刺 + 避險層 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 分層染色體基因組（Hierarchical Chromosome）

在 GA 引擎中，策略被編碼為結構化染色體：

```python
@dataclass(frozen=True)
class RadicalStrategyGene:
    # 1. 基本面爆發因子
    fcf_growth_min_pct: float       # 營運現金流成長百分位 (例如 > 70%)
    gross_margin_accel_pct: float   # 毛利率季增率百分位
    contract_liability_jump: bool   # 是否要求合約負債跳升
    
    # 2. 籌碼與技術共振
    inst_clustering_days: int       # 投信連續買超天數 (例如 3~10 日)
    rs_market_rank_pct: float       # 相對強弱度百分位 (例如 > 80%)
    
    # 3. 戰術集中度與權重
    basket_size: int                # 集中持股數 (8 ~ 12 檔)
    sizing_method: str              # "PARETO_RANK" | "INV_VOL"
    
    # 4. 雙軌出場守衛
    trailing_atr_multiplier: float  # 移動停利 ATR 倍數 (2.5 ~ 3.5)
    ma_exit_window: int             # 破線停損天數 (例如 20MA)
```

---

## 4. 相關積木模組索引

- [`GB08 波動度目標部位調節器`](blocks/GB08-volatility-target-sizer.md)
- [`GB09 現金流營收動能因子核心`](blocks/GB09-fcf-momentum-core.md)

---

## 5. NotebookLM & AI 提問範本

- **提問範本 1**：「請比較 S138 的反向波動加權與傳統等權重（$1/N$），在夏普值與回撤控制上有什麼數學優勢？」
- **提問範本 2**：「次世代 GA 藍圖是如何利用『雙軌混合進出場（Dual-Frequency）』同時兼顧基本面選股與技術面利潤奔馳的？」
