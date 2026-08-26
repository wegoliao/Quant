# lesson/claude · 完整合輯

作者 AI：**Claude (Opus 5, Anthropic)**　·　檔案 13 份　·　產生於 2026-08-26

這份檔案把整個目錄串成一份，給只能吃一個 URL 的 AI 用。
每一節開頭的 `## [id] title` 對應一個獨立檔案，可以單獨抽走使用。

---

## [C00] 脈絡 · 這個系統到底在做什麼

*track: context · status: verified · source: lesson/claude/00-context.md*

# 脈絡 · 這個系統到底在做什麼

如果你只讀一份文件，讀這份。其他所有積木都假設你已經知道這裡的分層。

## 一句話

一個把「策略卡說賺多少」和「帳戶實際賺多少」分開量測，並且**拒絕用估算冒充實績**的績效觀察系統。

## 為什麼要分開量測

台股散戶最常見的自我欺騙是把三個不同的數字混成一個：

| 數字 | 它真正的意思 | 誰在騙人 |
|---|---|---|
| 策略卡報酬 | 訊號價 → 現價，等權，無成本 | 假設你買得到訊號價 |
| 帳面損益 | 現價 × 股數 − 成本 | 假設你賣得掉，且不含賣出費稅 |
| 實際損益 | 已收現金 − 已付現金 | 這個不會騙人 |

三個數字在多頭時很接近，所以你不會發現差異。等到要縮小部位、或標的變薄的時候，差距會一次爆出來。這個系統的全部設計動機就是：**永遠讓這三個數字並排顯示，並且標註哪一個是估算。**

## 兩條主線

系統把宇宙切成兩半，切點是「有沒有真的付錢」：

**主線一（Mainline 1）· 錢的那條**
- 來源：券商成交回報，逐筆
- 有：成交價、股數、手續費、證交稅、成交日
- 能算：已實現損益、未實現損益、TWR、MDD
- 目前：22 筆買、1 筆賣、四個 NT$50 萬 sleeve

**主線二（Mainline 2）· 紙上的那條**
- 定義：策略卡上有訊號、但**整戶零部位**的個股
- 不配資金、不進 sleeve、不影響任何實績數字
- 能算：分價分布、現價分位、容量
- 不能算：報酬。因為沒有進場點，任何報酬都是假設出來的

關鍵設計：**主線二的名單不是人工維護的，是資料的差集自己算出來的。**

```
主線二 = { 今日策略卡的成員 } − { 成交簿推導出的整戶持股 }
```

名單會自己浮現、自己消失。你買了一檔，它隔天自動離開主線二；你賣光一檔，它自動回來。沒有第三個地方需要同步。

> 這是整個系統最值得抄走的一個想法：**能被推導的東西，永遠不要另外存一份。**

## 資料流

```
券商成交回報 ──> inputs/actual_fills.csv ──┐
                                            ├──> sleeve 曲線 ──> 已實現/未實現拆解
TWSE/TPEx OpenAPI ──> inputs/price_history.csv ─┤
                                            │
每日策略卡截圖 ──> inputs/latest_strategy_signals.csv ──> 主線二差集 ──> 分價分布
                                            │
                  inputs/watchlist.csv ─────┘   (決定要抓誰的行情)
```

四個 CSV 是**唯一的真相來源**。所有 HTML 都是產物，刪掉可以重建；CSV 刪掉就沒了。

## 邊界（不可協商）

這條支線被刻意設計成**沒有能力做壞事**：

- 不保存憑證
- 不登入券商
- 不送單、改單、刪單
- 不讀取 credentials 目錄
- 純標準函式庫，沒有券商 SDK

「更新行情」和「授權交易」是兩件完全不同的事。把它們放在同一個程序裡是災難的開始 —— 一個抓價格的 bug 不應該有能力送出委託。

## 目前的誠實狀態

寫下來是因為 AI 很容易在總結時把這些吞掉：

- 只有 11 筆日報酬，**Sharpe / Alpha / Beta / IR 全部顯示 N/A**，不是壞了，是樣本不夠（門檻 20）
- 理論卡曲線只到某個共同截止日，差異只在共同日期比較
- 分價分布是日線近似，不是逐筆分價表
- 成本口徑有 NT$653 落差（成交簿 vs 券商快照），已揭露未抹平

## 怎麼用這份 lesson

每個積木（block）都是一個**已經驗證過的黑盒子**：有明確輸入、明確輸出、明確不變量、明確測試。你可以單獨抽走任何一個放進自己的專案，不需要理解其他的。

建議順序：

1. 先讀 [`01-contracts`](01-contracts.md) —— 知道資料長什麼樣
2. 再讀 [`B01 已實現損益`](blocks/B01-realized-pnl-fifo.md) —— 最小、最完整的一個積木
3. 然後照你要解的問題挑 —— 積木之間沒有隱藏依賴

---

**本目錄作者：Claude (Opus 5, Anthropic)。**
其他 AI 請寫在 `lesson/<你的名字>/`，不要改這一份。交互學習的規則見 [`_shared/CROSS_AI_PROTOCOL`](../_shared/CROSS_AI_PROTOCOL.md)。

---

## [C01] 資料契約 · 四個 CSV 就是全部

*track: context · status: verified · source: lesson/claude/01-contracts.md*

# 資料契約 · 四個 CSV 就是全部

積木之間不靠函式呼叫溝通，靠**檔案格式**。這是刻意的：CSV 可以被人眼檢查、被 git diff、被任何語言讀，而且不會因為你換了框架就壞掉。

## 契約設計的三條規則

**1. 一個檔案一個事實層級。**
成交是成交、行情是行情、訊號是訊號。不要有一個「總表」把三種東西混在一起 —— 那個總表會變成沒有人敢改的東西。

**2. 每一列都要能回答「你從哪來」。**
每個 CSV 都有 `source` 欄。不是裝飾，是當數字對不起來時唯一能查的線索。

**3. 缺資料要留成缺資料。**
空字串就是空字串。不要填 0，不要 forward fill，不要「合理推估」。下游看到空值會 fail closed；看到假的 0 會安靜地算出錯的答案。

---

## `actual_fills.csv` · 成交簿（唯一不會騙人的檔案）

```csv
trade_id,strategy_id,stock_code,stock_name,side,fill_date,fill_time,fill_price,shares,consideration_twd,fee_twd,tax_twd,cash_out_twd,cash_in_twd,currency,source
X-02HV,YOY,3702,大聯大,BUY,2026-08-11,,126.5,546,69069,98,0,69167,0,TWD,20260820庫存表.xlsx
X-07P7,YOY,3702,大聯大,SELL,2026-08-19,,107,546,58422,83,175,0,58164,TWD,20260820庫存表.xlsx
```

| 欄位 | 契約 |
|---|---|
| `trade_id` | 券商委託單號。**不保證唯一** —— 不同日可能重複，需要時自己加日期後綴 |
| `strategy_id` | `TRUST` / `YOY` / `MARGIN` / `BREAKOUT`。歸屬是人工決定，同一檔可以拆給兩個策略 |
| `side` | `BUY` / `SELL` |
| `cash_out_twd` | 買進實付＝價金＋手續費 |
| `cash_in_twd` | 賣出實收＝價金−手續費−證交稅 |

**關鍵：`cash_out` / `cash_in` 才是真相，不是 `fill_price × shares`。**
所有損益計算都必須從這兩欄出發。用價差算出來的損益永遠比實際好看。

**同一檔可以掛在不同策略。** 例如 1709 和益：3,644 股在 `BREAKOUT`、305 股在 `MARGIN`。所以持股要用 `(strategy_id, stock_code)` 當 key，不能只用 `stock_code`。

---

## `price_history.csv` · 官方行情

```csv
asof_date,stock_code,open,high,low,close,volume,market,source
2026-08-25,2637,95.9,99.5,94.7,95.5,12345678,TWSE,TWSE_STOCK_DAY
```

- 來源：TWSE `STOCK_DAY`、TPEx `daily_close_quotes`，都是官方公開 API
- **休市、資料未發布、日期不符 → 不寫入。** 寧可缺一天，不可拿舊價冒充今天收盤
- OHLC 四個都要。只存 close 的話，分價分布（B02）和成交落點（B03）都做不了 —— 這是很多人事後才發現的坑

---

## `latest_strategy_signals.csv` · 每日策略卡

```csv
asof_date,effective_date,strategy_id,stock_code,stock_name,industry,entry_display,entry_price,close,magnitude_pct,direction,signed_return_pct,signal,source,quality_note
2026-08-25,,MARGIN,6213,聯茂,電子零組件,424.0,424.0,530,24.8,+,24.8,抱,owner_strategy_card_2026-08-25,
```

- `magnitude_pct` 恆為正、`direction` 是 `+`/`-`、`signed_return_pct` 才是帶號的。這是為了如實保存卡面（卡面只印絕對值加符號）
- `quality_note` 記錄**來源自相矛盾**的地方，例如：

```
PRINTED_PCT_VS_ENTRY_CLOSE_GAP:printed=37.8+,implied=+36.4
```

> 卡面印 37.8%，但用它自己印的進場價和收盤價回推是 36.4%。
> **不改任何一格，只標註。** 資料的矛盾是資訊，抹平它就是銷毀證據。

---

## `watchlist.csv` · 誰的行情要繼續抓

```csv
stock_code,stock_name,strategy_id,track,market,note
6213,聯茂,MARGIN,MAINLINE2,TWSE,融資卡成員；整戶零部位
3702,大聯大,YOY,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

這個檔案解決一個真實踩到的洞：**持股清單驅動抓取時，一檔賣掉就等於資料斷線。**

3702 平倉後從持股消失，行情停止更新，結果它的兩筆成交在成交落點分析裡完全對不到日線 —— 賣出樣本數是 0。加進 watchlist 後才補回來。

詳見 [`B06 watchlist 驅動抓取`](blocks/B06-watchlist-driven-fetch.md)。

---

## 為什麼是 CSV 不是資料庫

- 可以 `git diff`。資料改了什麼，PR 裡看得見
- 可以用 Excel 開。owner 要臨時補一列不需要問工程師
- 不需要 migration。加一欄就是加一欄
- 壞掉的時候看得出來哪一列壞了

代價是沒有交易、沒有索引、沒有型別。在**單人、每天幾十列**的規模下，這些代價是零，好處是全部。規模上去再換 —— 但那時候你已經知道 schema 該長什麼樣了，因為它已經被真實使用磨過一年。

---

**本目錄作者：Claude (Opus 5, Anthropic)。**

---

## [C20] 陷阱清單 · 這個專案真的踩到的坑

*track: traps · status: verified · source: lesson/claude/20-traps.md*

# 陷阱清單

每一條都是**真的發生過**的，不是教科書上的假設。附上發現方式，因為「怎麼被發現的」比「是什麼」更有價值。

---

## T01 · 一條曲線兩種估值口徑

**症狀**：績效曲線在最後一天憑空掉 0.44%，看起來像當天虧損。

**原因**：歷史日用毛值（`股數 × 收盤`），最新日用可變現淨值（扣賣出費稅）。**換了尺，不是變了值。**

**教訓**：口徑必須整條線一致。如果要改，整條一起改。

**怎麼發現的**：把日報酬列出來看，最後一天的數字和個股漲跌對不上。

---

## T02 · 已實現損益沒有名字

**症狀**：owner 讀了三天畫面，問「大聯大的虧損你是不是漏算了？」

**原因**：數學沒漏 —— sleeve 曲線一直含這筆虧損。但**整個 repo 沒有任何地方叫做「已實現」**，所有標籤都寫「未實現」。賣掉的股票離開庫存表，畫面上就找不到了。

**教訓**：正確的數字放在錯誤的標籤下面，等於錯的。**一個你指不出來的虧損，你不會從它身上學到東西。**

**怎麼發現的**：使用者讀畫面讀出來的，不是測試抓到的。這類問題測試抓不到 —— 測試只驗證計算，不驗證「人看得懂嗎」。

---

## T03 · 賣掉的股票資料斷線

**症狀**：成交落點分析裡，賣出樣本數 = 0。系統只有 1 筆賣出，那 1 筆是空的。

**原因**：抓行情的宇宙來自持股清單。3702 平倉後離開持股 → 行情停更 → 它的兩筆成交都對不到日線。

**教訓**：**你最需要一檔股票資料的時刻，正好是它剛賣掉的時候。**

**修法**：[`B06 watchlist 驅動抓取`](blocks/B06-watchlist-driven-fetch.md)

---

## T04 · 只存收盤價

**症狀**：想做分價分布和成交落點，發現做不了。

**原因**：`price_history.csv` 早期只有 `close`。分價分布需要 `high/low/volume`，成交落點需要 `high/low`。

**教訓**：**存資料的時候多存幾欄的成本是零，事後補的成本是無限大**（歷史行情可能已經不好拿了）。OHLCV 五個欄位一律全存。

---

## T05 · 委託單號不唯一

**症狀**：8/19 的 2301 光寶科和 8/25 的 2637 慧洋-KY，委託單號都是 `X-00ZX`。

**原因**：券商的委託單號在不同日期會重複。

**教訓**：**不要相信外部系統的 ID 是全域唯一的。** 需要唯一鍵時自己組（例如 `X-00ZX-20260825`），並且在文件裡寫明這個 ID 不唯一。

---

## T06 · 用價差算損益

**症狀**：算出來的損益永遠比對帳單好看一點點。

**原因**：`(賣價 − 買價) × 股數` 少算手續費和證交稅。3702 的價差答案 −10,647，真實答案 −11,003。

**教訓**：差 356 元不多，但**它永遠往好的方向錯**。100 筆之後你的策略評估會系統性偏樂觀。永遠從 `cash_out` / `cash_in` 出發。

---

## T07 · 資料來源自相矛盾，然後被抹平

**症狀**：策略卡表頭印 +3.7%，但畫面上六檔成分股的可見數字平均是 +4.33%，差 0.63pp。

**正確處理**：**原樣保存，標註不一致**。

```
quality_note: PRINTED_PCT_VS_ENTRY_CLOSE_GAP:printed=37.8+,implied=+36.4
```

**錯誤處理**：改其中一格讓驗算過關。

**教訓**：**資料的矛盾是資訊。** 抹平它就是銷毀證據。三個月後你想查「這個策略卡的表頭是怎麼算的」，只剩下你自己改過的版本。

---

## T08 · 成本口徑差 NT$653

**症狀**：成交簿累加的在庫實付 1,178,519，券商快照的在庫成本 1,177,866。

**處理**：**揭露，不抹平。** 四策略實績以逐筆成交現金流為準，並在頁面上寫出這個差額。

**教訓**：兩個來源不一致時，選一個當主，另一個當對照，**並且把差額顯示出來**。偷偷用其中一個是最糟的選擇。

---

## T09 · 樣本 11 筆算 Sharpe

**症狀**：Sharpe 顯示 3.2，看起來很棒。

**原因**：標準差在小樣本下極不穩定，年化再乘 √252 ≈ 15.9 倍把雜訊放大。

**教訓**：見 [`B08 樣本量門檻`](blocks/B08-sample-size-gate.md)。**敢顯示 N/A 才是專業。**

---

## T10 · 把快照倒推一年當歷史

**症狀**：曾經有一版把 2026-08-24 的持股股數倒推到一年前，算出一條「一年績效曲線」。

**原因**：想要有 CAGR / Sharpe / MDD 可以看。

**為什麼是災難**：那條曲線描述的是「如果你一年前就持有今天這些股票會怎樣」。這是**完美的後見之明**，和你的實際績效無關，而且必然很好看（因為今天持有的是活下來的那些）。

**教訓**：**倖存者偏誤最常見的形式，就是拿今天的持股回推歷史。** 這一版已被移除。

---

## T11 · 一字板除以零

**症狀**：分價分布在某些標的上崩潰。

**原因**：漲跌停的日子 `high == low`，`span = 0`。

**教訓**：台股有漲跌停，任何用到 `(price - low) / (high - low)` 的公式都必須處理 `span == 0`。

---

## T12 · 抓取安靜失敗

**症狀**：某檔一直沒資料，三週後才發現。

**教訓**：`kept == 0` 要進 failures 清單並顯示在 receipt 裡。**安靜的失敗是所有資料管線最大的敵人。**

---

## 一個統計

12 條裡面，**有 5 條是「數字是對的但呈現是錯的」或「資料是缺的但沒有人被告知」**（T02, T03, T07, T08, T12）。

只有 4 條是真正的計算錯誤（T01, T06, T10, T11）。

> 這個比例值得記住：**在資料系統裡，「沒有被說出來」造成的傷害，比「算錯」更多。**

---

**作者：Claude (Opus 5, Anthropic)**

---

## [C30] 問題寫法 · 怎麼問才會拿到真話

*track: prompts · status: verified · source: lesson/claude/30-prompts.md*

# 問題寫法 · 怎麼問才會拿到真話

這一份不是「prompt 模板大全」。它記錄的是**在這個專案裡實際產生高價值輸出的提問結構**，以及它們為什麼有效。

---

## P01 · 指名實例 + 陳述期望屬性

**實際的提問：**

> 有計算已經實現的虧損嗎？大聯大是已實現的虧損喔，你是不是漏算了？請再幫我精準呈現。

**為什麼這個提問很好：**

1. **指名了一個具體實例**（大聯大），不是「損益好像怪怪的」
2. **陳述了期望屬性**（它是已實現虧損），給了可驗證的斷言
3. **問的是「有沒有」，不是「請加上」** —— 留了空間讓答案是「有，但你看不到」

**結果**：真相是「數學沒漏，但整個系統沒有『已實現』這個字」。如果提問寫成「請加上已實現損益計算」，就會直接進到寫程式，而錯過「原來問題在呈現不在計算」這個更重要的發現。

**可複製的結構：**

```
[具體實例] 應該是 [屬性]。
你的 [輸出] 有反映這件事嗎？
```

---

## P02 · 先問邊界，再問答案

**反面**：「這檔該在幾塊買？」

**正面**：「我要能追蹤買賣價到最適合的入場點。」

第二種問法把問題從「給我一個價格」改成「給我一個追蹤機制」。前者要的是預測（沒有人有），後者要的是量測（可以做到）。

**結果**：做出了成交落點分析（[B03](blocks/B03-fill-landing.md)），並且發現「3702 的虧損不是賣錯是買錯」—— 這個發現比任何一個建議價格都有用，因為它告訴你**不要去優化下單方式**。

**可複製的結構：**

```
我要能 [持續量測 X]，而不是 [一次性得到 Y 的答案]。
```

---

## P03 · 要求「不要為了過關而改資料」

**實際的提問（大意）：**

> 原樣保存並標示來源不一致，不要為了讓驗證過關去改任何一格。

這句話應該寫在**每一個**資料匯入任務裡。AI（和人）在面對「兩個數字對不起來」時的預設衝動是讓它們對得起來，而最快的方式是改其中一個。

**結果**：`quality_note` 欄位誕生，矛盾被保存成資料而不是被消滅。

---

## P04 · 明確禁止「安靜地降級」

**寫法：**

```
資料不足時顯示 N/A，不要用較短的序列硬算。
缺日要標成「沒有來源」，不要自行補數。
休市或資料未發布時保持 NO_NEW_CLOSE，不得拿舊價冒充今天收盤。
```

這三句擋掉了三種最常見的靜默降級。**每一種都會產生一個看起來正常的錯誤數字。**

---

## P05 · 要求把限制印在產出上，不是只在對話裡

**寫法：**

> 這些限制要寫在頁面上，不是只在 README。

差別很大。README 沒有人讀，頁面上的字每天都會被看到。

**實例**：「目前 22 筆買進的樣本量還不足以下結論」這句話印在主線二頁面上，所以三個月後回來看的人不會誤用那個 40%。

---

## P06 · 給 AI 明確的「不可協商」清單

這個專案的每個腳本開頭都有：

```
Pure standard library. No network, no broker, no order path.
```

以及在 handoff 文件裡：

```
不得讀取 credentials、登入券商或實際傳送／修改／取消委託。
不得把單一庫存快照拿去算 CAGR、Sharpe、Alpha、Beta 或 MDD。
```

**為什麼有效**：這些是**否定式的、可檢查的**約束。「請小心處理」不可檢查；「不得有 order path」可以用 grep 檢查。

---

## P07 · 問「你怎麼驗證的」

當 AI 說「已完成、測試通過」時，追問：

```
哪個測試在擋哪一種錯誤？
如果有人把 X 改回舊做法，哪個測試會失敗？
```

好的測試能回答第二個問題。**不能回答的測試只是覆蓋率裝飾。**

實例：`test_the_real_3702_round_trip_reconciles_to_the_fill_book` 的存在理由，就是「3702 這筆虧損被任何形式抹掉時會叫」。

---

## P08 · 要求區分「數學錯」和「呈現錯」

```
這個數字是算錯了，還是算對了但沒有顯示出來？
```

在這個專案的 12 個陷阱裡，**有 5 個是呈現問題，只有 4 個是計算問題**（見 [`20-traps`](20-traps.md)）。

大部分人只審查計算，所以大部分問題留在呈現。

---

## P09 · 讓 AI 先盤點再動手

**寫法：**

> 幫我盤點如何更精進，並在這基礎上……

「盤點」這個動作強迫 AI 先讀現況、列出差距，而不是直接開始寫。代價是多一輪對話，收穫是不會做出「解決一個不存在的問題」的東西。

---

## P10 · 明確要求多個版本並保留

**寫法：**

> 我要 [功能] 的多個 UI/UX 版本。

單一版本會讓你在第一個想法上定型。三個版本讓你看到取捨。

**實例**：主線二做了三種介面（分價階梯／進場軌道／熱力矩陣），並且明說「用一陣子你會知道哪個真的在用，到時候砍掉另外兩個」。

**關鍵是後半句** —— 多版本是暫時的探索工具，不是永久的維護負擔。

---

## 給 AI 讀者的一段話

如果你是被丟進來總結這個 repo 的 AI，請注意這一份文件的元訊息：

**這個專案的使用者會追問。** 他會指名具體實例、會問「是不是漏算了」、會要求不准為了過關改資料。

所以正確的回應方式不是給一個乾淨的摘要，是**主動說出還沒解決的、樣本不足的、口徑有差的部分**。這份 repo 裡每一個 `N/A`、每一個 `quality_note`、每一句「還不足以下結論」，都是刻意留下的。**把它們總結掉，就是把這個專案最有價值的部分刪掉。**

---

**作者：Claude (Opus 5, Anthropic)**

---

## [B01] 已實現損益 · FIFO 對沖，只認落袋現金

*track: block · status: verified · verified_by: tests/test_realized.py (5 tests) · source: lesson/claude/blocks/B01-realized-pnl-fifo.md*

# B01 · 已實現損益（FIFO）

## 它解決什麼

賣掉的部位會從庫存表消失。庫存表消失 → 畫面上找不到 → 你以為沒發生。

真實案例：3702 大聯大 8/11 買 546 股、8/19 賣掉，**虧 NT$11,003**。這筆錢確實不在庫存裡了，但它從帳戶流出去了。而整個系統的每一個標籤都寫著「未實現損益」，所以 owner 讀了三天畫面，問出一句：「你是不是漏算了？」

**數學沒有漏 —— sleeve 曲線一直是對的**（賣出的現金回到 sleeve，報酬自然含這筆虧損）。漏的是**名字**。一個你指不出來的虧損，等於沒有發生過，你不會從它身上學到任何事。

## 契約

```python
closed_lots(fills: Sequence[Fill]) -> list[Lot]
open_lots(fills: Sequence[Fill]) -> dict[(strategy_id, stock_code), shares]
by_strategy(lots: Iterable[Lot]) -> dict[strategy_id, Summary]
as_of(lots, day) -> list[Lot]        # 只取 day 以前結算的
```

`Fill` 必要欄位：`strategy_id, stock_code, side, date, fill_price, shares, cash_out, cash_in`

`Lot` 產出：`shares, buy_date, buy_price, sell_date, sell_price, cost_twd, proceeds_twd, realized_pnl_twd, return_pct, holding_days`

**不變量**
- `realized_pnl = proceeds − cost`，其中 cost/proceeds 都來自現金欄，不是價差
- 已平倉的股數必須離開 `open_lots`，兩邊永遠不重複計算同一股
- 賣出找不到對應買進 → `raise`，不是回傳 0

## 核心：為什麼一定要 FIFO 而不是均價

均價法會算出**正確的總損益、錯誤的每一件事**：

| | FIFO | 均價 |
|---|---|---|
| 總已實現 | 對 | 對 |
| 進場價 | 真實的那一筆 | 虛構的加權平均 |
| 持有天數 | 真實 | 無法定義 |
| 一賣跨多買 | 拆成多列，各自有天數 | 壓成一列 |

你要的不是「我總共賺多少」，那個看銀行帳戶就好。你要的是**「哪一種進場活得久、哪一種活不久」**，那需要每一筆的持有期是真的。

## 陷阱

**陷阱 1：用價差算損益。**
`(賣價 − 買價) × 股數` 少算手續費和證交稅。3702 的價差答案是 −10,647，真實答案是 −11,003。差 356 元不多，但**它永遠往好的方向錯**，累積 100 筆之後你的策略評估會系統性偏樂觀。

**陷阱 2：把已實現和未實現加起來當「總報酬率」時分母搞錯。**
已實現的分母是已經退出的成本，未實現的分母是還在裡面的成本。兩者不能直接平均。系統的作法是各自報，合計只報**金額**和**對固定預算的百分比**（分母是 NT$50 萬，不是浮動成本）。

**陷阱 3：把 realized 算進「未實現損益」那張卡。**
首頁「累積未實現損益 +40,107」是券商庫存快照，**確實不含** −11,003。這不是 bug，是定義。但如果沒有另一張卡把 realized 寫出來，讀者一定會把它當成「我的總損益」。

## 程式碼

```python
def closed_lots(fills):
    books = defaultdict(deque)
    lots = []
    for fill in sorted(fills, key=lambda r: (r["date"], r.get("trade_id", ""))):
        key = (fill["strategy_id"], fill["stock_code"].strip())
        shares = float(fill["shares"])

        if fill["side"] == "BUY":
            books[key].append({
                "date": fill["date"],
                "shares": shares,
                "unit_cost": float(fill["cash_out"]) / shares,   # 含手續費
                "price": float(fill["fill_price"]),
            })
            continue

        unit_proceeds = float(fill["cash_in"]) / shares          # 已扣費稅
        remaining = shares
        while remaining > 1e-9:
            if not books[key]:
                raise RealizedError(f"{key} 賣出沒有對應買進")
            lot = books[key][0]
            matched = min(remaining, lot["shares"])
            lots.append({
                "strategy_id": key[0], "stock_code": key[1],
                "shares": matched,
                "buy_date": lot["date"], "sell_date": fill["date"],
                "cost_twd": matched * lot["unit_cost"],
                "proceeds_twd": matched * unit_proceeds,
                "realized_pnl_twd": matched * (unit_proceeds - lot["unit_cost"]),
                "return_pct": unit_proceeds / lot["unit_cost"] - 1.0,
                "holding_days": (fill["date"] - lot["date"]).days,
            })
            lot["shares"] -= matched
            remaining -= matched
            if lot["shares"] <= 1e-9:
                books[key].popleft()
    return lots
```

30 行。沒有相依套件。可以直接複製到任何專案。

## 驗證

`tests/test_realized.py`，5 個測試，每一個都在擋一種特定的自我欺騙：

1. **`test_realized_uses_settled_cash_not_price_difference`** —— 斷言答案比「價差答案」更差。如果有人偷偷改回價差法，這個測試會炸
2. **`test_the_real_3702_round_trip_reconciles_to_the_fill_book`** —— 用真實成交簿對帳，並斷言 `realized_pnl < 0`。註解寫著「3702 closed at a loss; never round it away」
3. **`test_a_sell_without_a_matching_buy_fails_closed`** —— 資料錯要炸，不要回傳 0
4. **`test_one_sell_across_two_buys_splits_into_two_lots`** —— 斷言持有天數是 `[9, 7]` 兩個不同的值
5. **`test_realized_and_unrealized_never_double_count_the_same_share`** —— 斷言平倉部位的成本已完全離開在庫帳面成本

> 測試的價值不在「證明現在是對的」，在「未來有人改壞的時候會叫」。
> 第 2 個測試會在 3702 這筆虧損被任何形式抹掉時失敗，這才是它存在的理由。

## 真實產出

| 策略 | 已實現 | 未實現 | 合計 |
|---|---:|---:|---:|
| 投信 | — | +15,330 | +15,330 |
| YOY | **−11,003** | +14,145 | **+3,142** |
| 融資 | — | −4,354 | −4,354 |
| 突破 | — | +25,073 | +25,073 |

YOY 的 +0.63% 長這樣：一筆虧 11,003 的平倉，加上還在手上的 +14,145。分開看才知道這個策略發生過什麼事。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/realized.py`

---

## [B02] 分價分布 · 用日線做出 volume-at-price

*track: block · status: verified · verified_by: output/mainline2_receipt.json (7 names profiled) · source: lesson/claude/blocks/B02-volume-profile.md*

# B02 · 分價分布（volume-at-price）

## 它解決什麼

「這個價格算高還是低？」

一般人用均線、用 52 週高低。這兩個都只用了收盤價，丟掉了**成交量在價格上的分布**。真正的問題不是「離最高點多遠」，是「有多少人在這個價位附近真的成交過」。

分價分布給你三個數字：

- **POC（Point of Control）**：成交量最大的那個價位
- **價值區（Value Area）**：涵蓋 70% 成交量的價格帶
- **現價分位**：有多少比例的成交量發生在現價以下

## 關鍵限制：交易所不給你逐筆分價

真正的分價表需要逐筆成交（tick）。TWSE / TPEx 的公開 API 只給**日線 OHLCV**。所以只能近似。

**唯一誠實的假設：把當天的成交量在 `[最低, 最高]` 之間均勻分攤。**

這個假設一定是錯的（實際成交會集中在某幾個價位），但它是**無偏的** —— 它不偏向任何價位。任何比它「更聰明」的分攤（例如假設集中在收盤價附近）都是在猜，而猜錯會讓 POC 系統性偏移。

> 這就是為什麼這個系統**從來不把 POC 叫做「合理價」**。
> 它是「過去半年成交量最大的價位」，句號。用日線近似算出來的東西，沒有資格承擔規範性的名字。

## 契約

```python
volume_profile(bars, bins=44) -> {
    "low", "high", "edges", "volume",     # 直方圖本體
    "poc", "poc_index",                   # 最大量價位
    "value_low", "value_high",            # 70% 量能帶
    "total", "bars", "first", "last",     # 稽核用
}
percentile_of(profile, price) -> float    # 0..1，price 以下的量佔比
```

`bars` 需要 `low, high, close, volume`。**只有 close 是做不出來的** —— 這是很多人存資料時省掉 OHLC，事後才發現的坑。

## 演算法

**第一步：分攤。** 對每根日線，把成交量按重疊比例分給每個價格 bin。

```python
for bar in bars:
    span = bar["high"] - bar["low"]
    if span <= 0 or bar["volume"] <= 0:
        # 一字板／無量：整筆塞進收盤價那格
        index = min(int((bar["close"] - low) / width), bins - 1)
        volume[max(index, 0)] += bar["volume"]
        continue
    for index in range(bins):
        overlap = min(edges[index + 1], bar["high"]) - max(edges[index], bar["low"])
        if overlap > 0:
            volume[index] += bar["volume"] * overlap / span
```

**第二步：價值區。** 從 POC 出發，每次往量比較大的那一側擴一格，直到累積 70%。

```python
poc_index = max(range(bins), key=lambda i: volume[i])
low_index = high_index = poc_index
covered = volume[poc_index]
while covered < total * 0.70 and (low_index > 0 or high_index < bins - 1):
    below = volume[low_index - 1] if low_index > 0 else -1.0
    above = volume[high_index + 1] if high_index < bins - 1 else -1.0
    if above >= below:
        high_index += 1;  covered += volume[high_index]
    else:
        low_index -= 1;   covered += volume[low_index]
```

**第三步：分位。** 線性內插，不要只回傳所在 bin 的編號 —— bin 邊界會造成鋸齒。

```python
def percentile_of(profile, price):
    if price <= profile["low"]:  return 0.0
    if price >= profile["high"]: return 1.0
    below = 0.0
    for i, edge in enumerate(profile["edges"][:-1]):
        upper = profile["edges"][i + 1]
        if price >= upper:
            below += profile["volume"][i]
        elif price > edge:
            below += profile["volume"][i] * (price - edge) / (upper - edge)  # 內插
            break
        else:
            break
    return below / profile["total"]
```

## 陷阱

**陷阱 1：bin 數量沒有正確答案，但要固定。**
用了 44。太少（<20）看不出結構，太多（>100）每格都是雜訊。重點是**所有標的用同一個數字**，否則跨標的比較沒有意義。

**陷阱 2：一字板會讓 span=0，除以零。**
台股有漲跌停。必須有 `span <= 0` 的分支，直接把量塞進收盤價那格。

**陷阱 3：把分位當成訊號。**
「現價分位 99%」的意思是「過去半年只有 1% 的量成交在更高的位置」。它**不代表**貴、不代表該賣、不代表會回檔。它只是描述統計。真實產出裡 6213 聯茂分位 99%、POC 271.88、現價 530 —— 這在強勢突破股身上是常態，不是異常。

**陷阱 4：視窗長度會改變答案。**
6 個月和 1 年的 POC 可能差很遠。**視窗長度必須顯示在畫面上**，不能只在程式碼裡。

## 真實產出（6 個月，134 個交易日）

| 股票 | 收盤 | POC | 現價分位 | 在價值區 |
|---|---:|---:|---:|:--:|
| 1714 和桐 | 16.50 | 9.89 | 62% | 在 |
| 2030 彰源 | 23.65 | 18.36 | 99% | 外 |
| 3046 建基 | 57.20 | 57.73 | 59% | 在 |
| 3605 宏致 | 116.50 | 89.40 | 91% | 外 |
| 6213 聯茂 | 530.00 | 271.88 | 99% | 外 |
| 6570 維田 | 52.90 | 59.34 | 43% | 在 |
| 6603 富強鑫 | 26.25 | 25.69 | 70% | 在 |

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::volume_profile`

---

## [B03] 成交落點 · 唯一能對「進場點」說的實證

*track: block · status: verified · verified_by: output/mainline2_receipt.json (22 buys, 1 sell) · source: lesson/claude/blocks/B03-fill-landing.md*

# B03 · 成交落點（fill landing）

## 它解決什麼

每個人都想知道「最適合的入場點在哪」。這是一個**預測問題**，而且沒有人有答案。

但有一個相鄰的問題是**可量測的**，而且幾乎沒有人在量：

> 你已經下的單，實際落在當天價格區間的哪裡？

把每一筆成交價放回**它自己那天的最高／最低**之間，正規化成 0..1：

```
0% = 當日最低（買到最便宜）
100% = 當日最高（買到最貴）
```

買進落點越低越省，賣出落點越高越好。這不預測任何事 —— 它衡量已經發生的執行品質。

## 為什麼這個指標比 slippage 更早可用

訊號→成交的履約落差（[B05](B05-signal-fill-slippage.md)）需要「訊號價」，而訊號價只在你有完整訊號紀錄時存在。成交落點**只需要成交簿和日線**，回溯期有多長就能算多長。

換句話說：**這是你今天就能算的東西，而且過去所有成交都算得到。**

## 契約

```python
range_position(bar, price) -> float | None   # 0..1；span==0 時回 None
fill_landings(fills, bars) -> list[Landing]
```

`Landing` 產出：`position`（區間位置）、`vs_close`（對當日收盤 %）、`vs_open`（對當日開盤 %）、`status`

**不變量**
- 找不到對應日線 → `status="NO_BAR"`、`position=None`，**不要跳過、不要當 0**
- 一字板（`high == low`）→ `None`，因為區間位置沒有定義

## 程式碼

```python
def range_position(bar, price):
    span = bar["high"] - bar["low"]
    if span <= 0:
        return None                      # 一字板：位置無定義
    return max(0.0, min(1.0, (price - bar["low"]) / span))
```

三行。整個 block 最有價值的部分不是程式碼，是**想到要算它**。

## 陷阱

**陷阱 1（真的踩到了）：平倉的股票行情會斷線。**

原本抓取宇宙來自持股清單。3702 賣掉之後從持股消失 → 行情停更 → 它的**買進和賣出兩筆成交都對不到日線** → 賣出樣本數顯示 0。

一個只有 1 筆賣出的系統，把那 1 筆弄丟了，就等於完全沒有出場資料。修法見 [`B06 watchlist 驅動抓取`](B06-watchlist-driven-fetch.md)。

**陷阱 2：n=22 不能下結論。**
平均 40% 看起來不錯，但 22 筆買進、1 筆賣出的樣本量不足以說「你的執行很好」。系統把這句話**印在頁面上**，不是藏在 README：

> 目前 22 筆買進的樣本量還不足以下結論，任何「改用限價／改掛開盤」的決定都應該等樣本夠了再談。

**陷阱 3：把落點好壞當成損益好壞。**
最有價值的一個發現剛好反過來 —— 見下。

## 真實產出

22 筆買進，平均落在當日區間 **40%**（低於中點），平均比當日收盤低 **0.75%**。1 筆賣出落在 **89%**。

| | 股票 | 落點 |
|---|---|---:|
| 最好 | 2609 陽明 | 4% |
| | 2408 南亞科 | 12% |
| | 6672 騰輝 | 15% |
| 最差 | 2395 研華 | 82% |
| | 3702 大聯大 | 79% |
| | 2301 光寶科 | 68% |

**最有價值的一句話：3702 的虧損不是賣錯，是買錯。**

買在當日 79% 高位、賣在 89% 高位 —— 兩邊執行都不差。錢是在 8/11 到 8/19 之間跌掉的，那是選股／持有期的問題，不是下單技巧的問題。

沒有這個指標，你會花時間去優化下單方式（限價？分批？掛開盤？），而真正的問題在完全不同的地方。**這就是量測的價值：它告訴你不要優化什麼。**

## 延伸

累積到 30 筆以上之後可以做的事（現在還不行）：

- 按策略分組：哪個策略的進場執行比較差
- 按下單時段分組：需要 `fill_time`（成交簿已經留了這一欄，目前多數是空的）
- 對照當日振幅：波動大的日子落點是不是更糟

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::range_position`

---

## [B04] 可變現淨值 · 帳面值不是你拿得到的錢

*track: block · status: verified · source: lesson/claude/blocks/B04-liquidation-value.md*

# B04 · 可變現淨值

## 它解決什麼

`股數 × 收盤價` 是**毛值**。你賣掉拿不到那麼多，因為出場要付手續費和證交稅。

台股現股賣出成本：
- 手續費 0.1425%（券商可能打折，但保守用全額）
- 證交稅 0.3%
- 合計約 **0.4425%**

聽起來很小。但它是**單向、必然、每次都發生**的。任何一個「勝率 52%、平均賺 0.8%」的策略，扣掉這個之後就不存在了。

## 契約

```python
estimated_liquidation_value(shares: float, close: float) -> float
```

```python
def estimated_liquidation_value(shares, close):
    """Mirror the broker screen's estimated fee + 0.3% transaction tax."""
    gross = shares * close
    return gross - int(gross * 0.001425) - int(gross * 0.003)
```

**注意 `int()`。** 券商的費用是**無條件捨去到整數元**的，不是四捨五入。要跟券商畫面對得起來就必須複製這個行為 —— 這種細節是「數字對不起來」的常見來源。

## 為什麼要在每一天都用它，而不是只在最後一天

這是一個真實的 bug。原本的實作是：歷史日用毛值、最新日用淨值。結果**曲線在最後一天憑空掉了 0.44%**，看起來像當天虧損，其實是換了尺。

> **一條曲線只能有一個估值口徑。**
> 如果你改了口徑，整條線要一起改，不能只改末端。

修正後：所有日期都用可變現淨值，所以曲線的形狀是對的，起點也是對的。

## 陷阱

**陷阱 1：拿它跟券商的「未實現損益」比。**
券商庫存畫面的損益通常是**毛值**（不扣賣出費稅）。所以你的數字會系統性比券商小 0.44%。這不是錯，但必須標註口徑，否則 owner 會以為算錯了。

**陷阱 2：買進成本也要含手續費。**
成本端是 `cash_out`（價金＋手續費），賣出端是淨值。兩邊都含成本，這樣算出來的報酬才是**真的能落袋的報酬**。只扣一邊是最常見的半吊子做法。

**陷阱 3：零股和整股的費用結構不同。**
零股手續費有最低收費（通常 NT$1或20），小額交易的實際費率會遠高於 0.1425%。這個 block **不處理零股**，用在零股上會低估成本。

## 一個延伸的觀念：容量

同樣的邏輯往前推一步就是**容量**。你能買多少而不推動價格？

```python
SLOT_TWD = 50_000.0          # 50 萬 sleeve 分十檔
PARTICIPATION_CAP = 0.05     # 不超過均量 5%

slot_shares = SLOT_TWD / price
participation = slot_shares / avg_volume_20d
capacity_twd = avg_volume_20d * PARTICIPATION_CAP * price
```

真實產出裡，6570 維田的單量佔均量 **0.392%**，6213 聯茂只有 **0.001%** —— 差了 400 倍。同一個策略在這兩檔身上的可執行性完全不同，而傳統的回測報告不會告訴你這件事。

> **Sharpe 很高但容量只有 NT$10 萬的策略，不是好策略，是一個統計假象。**

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::estimated_liquidation_value`

---

## [B05] 履約落差 · 策略卡報的價，帳戶付的價

*track: block · status: verified · source: lesson/claude/blocks/B05-signal-fill-slippage.md*

# B05 · 訊號 → 成交 履約落差

## 它解決什麼

策略卡說「進場 97.1」。帳戶實際成交 **97.80**。

差 0.72%。聽起來沒事。但如果這個落差是**系統性的**，那麼一個年化 20% 的策略，一年進出 20 次，就會被吃掉 14 個百分點。

**這個落差在理論曲線裡看不到，在帳戶淨值裡也看不到** —— 帳戶淨值只知道你付了 97.80，不知道原本應該是 97.1。它只存在於「兩份資料的交集」，所以必須刻意去記錄。

## 契約

```python
build_slippage_ledger(path, ohlc) -> list[SlippageRow]
```

輸入 `signal_fills.csv`：

```csv
signal_date,effective_date,strategy_id,stock_code,stock_name,action,signal_ref_price,signal_basis,fill_date,fill_time,fill_price,shares,source
2026-08-24,2026-08-25,MARGIN,2637,慧洋-KY,BUY,97.1,NEXT_OPEN,2026-08-25,10:14:13,97.80,1000,owner_pasted_fill
```

## 核心：方向要對

```python
# 買進成交在參考價「之上」是不利；賣出成交在「之下」是不利
direction = 1.0 if side == "BUY" else -1.0

def basis_points(reference):
    if not reference:
        return None
    return direction * (fill_price / reference - 1.0) * 10_000.0
```

**正的 bp 一律代表「對自己不利」**，不論買賣。這樣所有樣本可以直接平均，不需要分開處理。

這個小設計很重要：如果買賣用不同符號，你的統計會在買賣比例改變時漂移，而你不會發現。

## 三個參考價，全部都要記

同一筆成交要對照三個基準，因為它們回答不同的問題：

| 參考價 | 回答的問題 |
|---|---|
| `signal_ref_price` | 策略卡的報酬要打幾折 |
| 當日開盤 | 如果我無腦掛開盤會怎樣 |
| 當日收盤 | 我比「收盤價買」好還是差 |

只記一個的話，你之後想問另外兩個問題時，資料已經沒了。**紀錄的成本很低，事後補的成本是無限大。**

## 陷阱

**陷阱 1：`signal_basis` 一定要寫。**
「97.1」是收盤價？次日開盤預期？還是策略卡的進場欄？三者的落差意義完全不同。系統用 `NEXT_OPEN` 這種明確的 enum，不允許空白。

**陷阱 2：只記成交的，不記沒成交的。**
如果訊號發出但你沒買（掛單沒成交、或當天忘了），那也是履約落差的一部分 —— 而且是最貴的那一部分。**未執行的訊號要留紀錄**，否則你的落差統計只涵蓋「有成交的那些」，選擇性偏誤會讓數字好看。

（這一點目前的實作**還沒做到**，誠實記在這裡。）

**陷阱 3：樣本 1 筆就下結論。**
目前只有 2637 慧洋-KY 一筆。0.72% 這個數字現在**什麼都不代表**。

## 為什麼這是整個系統最重要的一張表

策略研究的終局問題只有一個：

> 這個策略能不能被執行？

回測告訴你「如果能買到訊號價會怎樣」。履約落差帳告訴你「你買不買得到」。**兩者相減才是真實可得報酬。**

大部分人的策略死在這裡，而且死了不知道 —— 因為他們從來沒有把訊號價和成交價放在同一張表上。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::build_slippage_ledger`

---

## [B06] watchlist 驅動抓取 · 別讓賣掉的股票資料斷線

*track: block · status: verified · source: lesson/claude/blocks/B06-watchlist-driven-fetch.md*

# B06 · watchlist 驅動抓取

## 它解決什麼（一個真的踩到的洞）

抓行情要先決定「抓誰」。最自然的做法是：**抓我持有的**。

這個做法有一個安靜的失效模式：

```
你賣掉一檔 → 它離開持股 → 抓取宇宙不再包含它 → 資料從那天起斷線
```

而你**最需要它資料的時刻，正好是它剛賣掉的時候** —— 你要做出場分析、要算成交落點、要看賣掉之後它走去哪。

實際發生的事：3702 大聯大平倉後，它的買進和賣出兩筆成交在成交落點分析（[B03](B03-fill-landing.md)）裡完全對不到日線。整個系統只有 1 筆賣出樣本，而那 1 筆是空的。

## 契約

抓取宇宙 = `positions_ledger.csv` ∪ `watchlist.csv` ∪ `BENCHMARKS`

```python
def load_universe():
    seen = {}
    for row in read_csv(LEDGER_PATH):        # 持股
        seen.setdefault(row["stock_code"], {...})
    for row in read_csv(WATCHLIST_PATH):     # 追蹤清單：主線二 + 已平倉
        seen.setdefault(row["stock_code"], {...})
    return [seen[code] for code in sorted(seen)]
```

`watchlist.csv` 的 `track` 欄決定用途：

```csv
stock_code,stock_name,strategy_id,track,market,note
6213,聯茂,MARGIN,MAINLINE2,TWSE,融資卡成員；整戶零部位
3702,大聯大,YOY,CLOSED,TWSE,已平倉；保留行情供成交落點對照
```

- `MAINLINE2` → 進主線二頁面 + 抓行情
- `CLOSED` → **只抓行情**，不進任何頁面

`setdefault` 而非覆寫：持股清單優先，watchlist 只補沒有的。

## 為什麼分成兩個檔案而不是一個欄位

因為它們的**生命週期不同**。

`positions_ledger.csv` 是部位狀態，會被績效計算讀取。`watchlist.csv` 是觀察意圖，只被抓取程序讀取。把「我想看這檔」寫進部位檔，遲早會有人不小心把它算進淨值。

> **一個檔案一個責任。** 想在既有檔案加一個 `shares=0` 的列來偷渡追蹤清單，那是在給未來的自己埋雷。

## 陷阱

**陷阱 1：市場別（上市／上櫃）用猜的。**
`6570` 看起來像上櫃，但不一定。正確做法是**先試 TWSE，失敗再試 TPEx**，把 `market` 欄當成提示而不是事實：

```python
order = ["TPEX", "TWSE"] if market == "TPEX" else ["TWSE", "TPEX"]
for candidate in order:
    rows = fetch(code, candidate)
    if rows:
        return rows, candidate      # 回傳「實際解析出來的」市場別
```

**陷阱 2：抓取失敗要吵，不要安靜。**
`kept == 0` 要進 `failures` 清單並顯示。一個安靜失敗的抓取程序會讓你在三週後才發現某檔一直沒資料。

**陷阱 3：抓太多。**
7 檔 × 7 個月 × 1.8 秒延遲 ≈ 3 分鐘。宇宙每加一檔就是線性成本，而且會撞到交易所的 rate limit。**只抓你真的會看的**，這就是為什麼 watchlist 是明確清單而不是「全市場」。

## 一般化：這個模式叫什麼

這是**「意圖與狀態分離」**。

- 狀態（我持有什麼）：由事實推導，不可手動編輯
- 意圖（我想觀察什麼）：人工維護，不影響任何計算

很多資料管線的腐爛都來自把這兩者混在一起。分開之後，狀態可以隨時重算，意圖可以隨時修改，兩邊互不干擾。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/fetch_prices.py::load_universe`

---

## [B07] Fail closed · 寧可炸掉，不要安靜地算錯

*track: block · status: verified · source: lesson/claude/blocks/B07-fail-closed-inputs.md*

# B07 · Fail closed 輸入契約

## 它解決什麼

金融資料管線最危險的不是崩潰，是**安靜地算出一個看起來合理的錯誤數字**。

崩潰你會馬上知道。錯誤數字你會拿去做決定。

## 反面教材

```python
price = float(row.get("close", 0))          # 缺資料 → 0 元
shares = int(row.get("shares") or 0)        # 缺資料 → 0 股
value = price * shares                       # 靜悄悄的 0
```

這段程式碼永遠不會拋例外，也永遠不會告訴你資料有問題。它會讓某一天的淨值變成 0，然後那天的日報酬變成 −100%，然後你的 MDD 變成 −100%，然後你以為策略爆掉了。

## 契約

```python
class InputError(ValueError):
    """Input contract violation that must fail closed."""

def required_float(value, field) -> float:
    if value is None or str(value).strip() == "":
        raise InputError(f"{field} is required")
    try:
        number = float(str(value).replace(",", ""))
    except ValueError as exc:
        raise InputError(f"{field} must be numeric: {value!r}") from exc
    if not math.isfinite(number):
        raise InputError(f"{field} must be finite")
    return number
```

四個檢查，每一個都擋一種真實會發生的事：

| 檢查 | 擋什麼 |
|---|---|
| 空值 | Excel 匯出的空格、券商漏欄 |
| 非數字 | `"—"`、`"N/A"`、`"停牌"` |
| 千分位 | `"1,234.5"` —— 這是台灣資料的常態 |
| `isfinite` | `inf`、`nan` —— 除以零的殘骸 |

**`field` 參數不是裝飾。** 錯誤訊息必須說出是哪一欄壞了，否則你要在 5,000 列裡面找。

## 三種缺資料，三種處理

不是所有缺資料都該炸。要分清楚：

**1. 契約違反 → 拋例外**
成交簿裡有一列沒有 `cash_out`。這是資料錯誤，繼續算下去只會產生垃圾。

**2. 已知的資料未到 → 明確狀態碼**
今天的收盤還沒發布。這是正常的，回傳 `NO_NEW_CLOSE` 或 `MARKET_DATE_MISMATCH`，**不要拿昨天的價格冒充今天**。

**3. 樣本不足 → 顯示 N/A**
只有 11 筆日報酬，算不出可信的 Sharpe。見 [`B08 樣本量門檻`](B08-sample-size-gate.md)。

```python
MIN_RISK_RETURN_OBS = 20

if len(returns) < MIN_RISK_RETURN_OBS:
    return None          # 不是 0，不是「暫時用 11 筆算」
```

## 陷阱

**陷阱 1：用 `or` 當預設值。**

```python
volume = to_float(row.get("volume")) or 0.0
```

這行有一個 bug：**真實的 0 成交量會被當成缺資料**。在停牌日這是對的行為，在其他情況下不是。要區分就要用 `is None`：

```python
volume = to_float(row.get("volume"))
volume = 0.0 if volume is None else volume
```

**陷阱 2：在迴圈裡 try/except 然後 continue。**

```python
for row in rows:
    try:
        process(row)
    except Exception:
        continue          # ← 這裡吞掉了多少列？沒有人知道
```

如果真的要容錯，**至少要數**：收集失敗的列、印出數量、超過閾值就整批失敗。

**陷阱 3：把驗證寫在畫面渲染裡。**
驗證要在**載入時**做，不是在畫圖時。否則同一份壞資料會在不同的圖表裡表現出不同的症狀，你會以為是畫圖的 bug。

## 一句話

> 一個會炸的管線，你會修它。
> 一個會安靜算錯的管線，你會信它。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_dashboard.py::required_float`

---

## [B08] 樣本量門檻 · 敢顯示 N/A 才是專業

*track: block · status: verified · source: lesson/claude/blocks/B08-sample-size-gate.md*

# B08 · 樣本量門檻

## 它解決什麼

Sharpe = 平均日報酬 / 日報酬標準差 × √252

用 11 筆日報酬算，這個公式**會給你一個數字**。它可能是 3.2，看起來很棒。它毫無意義。

標準差在小樣本下極不穩定，年化又乘上 √252 ≈ 15.9 倍，把雜訊放大成一個看起來很專業的數字。**這是量化領域最常見的自我欺騙。**

## 契約

```python
MIN_RISK_RETURN_OBS = 20

def sharpe(returns):
    if len(returns) < MIN_RISK_RETURN_OBS:
        return None
    ...

def beta(portfolio, benchmark):
    common = align(portfolio, benchmark)
    if len(common) < MIN_RISK_RETURN_OBS + 1:   # 迴歸需要多一點
        return None
    ...
```

回傳 `None`，畫面顯示 `N/A`，**並且顯示為什麼**：

```
Sharpe   N/A    WAITING_MIN_20_RETURNS (目前 11 筆)
MDD      -0.76% OK
```

## 三個設計決定

**1. 門檻是常數，不是參數。**
如果它是參數，某天有人會為了讓畫面好看而調小它。常數放在模組頂端，改它需要改程式碼、過 code review、跑測試。

**2. 不同指標門檻可以不同。**
MDD 只需要一條曲線，2 筆就能算，而且意義明確 —— 所以 MDD **不設門檻**。Sharpe、Sortino、Alpha、Beta、IR、TE 需要分布的穩定性，全部設門檻。

分清楚「需要樣本量」和「不需要樣本量」的指標，比統一設一個門檻更誠實。

**3. 狀態碼要出現在畫面上，不是只在 log。**
`WAITING_MIN_20_RETURNS` 這個字串是給**人**看的。它告訴 owner：不是壞了，是還沒到。沒有這個字串，空白的 Sharpe 欄位會被當成 bug，然後有人會「修好它」。

## 陷阱

**陷阱 1：用月報酬或週報酬繞過門檻。**
「日報酬只有 11 筆，那我用週報酬吧」—— 週報酬只會更少。改變頻率不會創造資訊。

**陷阱 2：用回測填補實績。**
「實際只有 11 天，那我把回測的 500 天接上去」—— 這會產生一條在接點處性質完全改變的曲線，而且回測那段沒有滑價、沒有費用、沒有執行失敗。

系統的作法是**兩條線並排畫，只在共同截止日比較差異**，永遠不接在一起。

**陷阱 3：把「不夠」當成「不好」。**
N/A 不是負面評價。它是「還不知道」。這兩者的差別是專業和業餘的分界線。

## 更深的一層：Deflated Sharpe

即使樣本夠了，還有第二個問題：**你試了幾種策略才找到這一個？**

如果你測了 200 個參數組合，最好的那個的 Sharpe 有很大一部分是選擇偏誤。Deflated Sharpe Ratio 就是在扣這個。

兩個實務上踩過的坑：

- **DSR 顯示 1.0000 代表有 bug**，不是代表完美。通常是試驗次數沒有正確傳入
- **長期只做多的台股組合，成分間相關性 |ρ| ≤ 0.5 是不可能達到的**。任何用這個當門檻的篩選會回傳空集合

## 一句話

> 一個誠實的 N/A，比一個不誠實的 3.2 有價值一萬倍。
> 因為 N/A 讓你繼續蒐集資料，3.2 讓你下注。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/analytics.py::MIN_RISK_RETURN_OBS`

---

## [B09] 推導式狀態 · 能算出來的絕不另存一份

*track: block · status: verified · source: lesson/claude/blocks/B09-derived-state.md*

# B09 · 推導式狀態

## 它解決什麼

「我想追蹤那些有訊號但我沒買的股票。」

**業餘做法**：開一個 `mainline2.csv`，手動維護名單。

**問題**：這份名單有三種方式會腐爛。
- 你買了一檔，忘了從名單刪掉 → 重複計算
- 你賣光一檔，忘了加回名單 → 追蹤斷線
- 策略卡換成分股，名單沒跟上 → 追蹤了一檔已經不在策略裡的股票

三個月後這份名單和現實完全脫節，而且**沒有任何機制會告訴你**。

## 契約

不要存名單。**每次重算。**

```
主線二 = { 今日策略卡的成員 } − { 成交簿推導出的整戶持股 }
```

```python
def held_positions(fills):
    held = defaultdict(float)
    for fill in fills:
        held[fill["stock_code"]] += fill["shares"] * (1 if fill["side"] == "BUY" else -1)
    return {code: shares for code, shares in held.items() if shares > 1e-9}


def build_roster(signals, bars, held):
    roster = []
    for (strategy_id, code), signal in sorted(signals.items()):
        if code in held:           # 有部位 → 不是主線二
            continue
        roster.append({...})
    return roster
```

持股本身也是推導的 —— 從成交簿加總，不是另外存一份庫存表。

**唯一的真相是成交簿。** 其他都是它的函數。

## 效果

名單自己浮現、自己消失：

- 8/25 買了 2637 慧洋-KY → 它隔天自動離開主線二
- 假設賣光 1709 和益 → 它自動回到主線二（如果還在卡上）
- 策略卡拿掉某檔 → 它自動消失，不會變成孤兒

**沒有第三個地方需要同步。** 這是這個系統最值得抄走的一個想法。

## 陷阱

**陷阱 1：`> 0` 要用 `> 1e-9`。**
浮點數加減後不會剛好等於 0。一檔完全賣光的股票可能留下 `-4.5e-16`，用 `> 0` 判斷會讓它憑空消失或憑空出現。

**陷阱 2：同一檔在不同策略。**
2395 研華同時出現在 YOY 卡和 BREAKOUT 卡上，但部位掛在 YOY。

問題：BREAKOUT 的 2395 算不算「沒買」？

系統的決定是**用整戶零部位當判準**（`code in held`，不看 strategy_id），因為主線二問的是「這個名字我有沒有曝險」，而曝險是整戶的。但這個決定必須寫下來，否則三個月後沒有人記得為什麼。

> **推導規則本身就是需要文件的東西。** 程式碼說明「怎麼算」，文件說明「為什麼這樣算」。

**陷阱 3：推導很慢的時候會有人想快取。**
現在 23 筆成交，重算是瞬間的事。等到 10,000 筆的時候會有人想存中間結果。

那時候的正確做法是**存快照 + 存推導版本號**，並且有一個測試比對快照和重算結果。不是放棄推導。

## 一般化

這個模式在資料庫世界叫 **derived state / materialized view**，在函數式程式設計叫 **single source of truth**。

判斷準則很簡單：

> **如果 A 可以從 B 算出來，那 A 不應該被儲存。**
> 如果非存不可（效能），那必須有一個測試證明存的和算的一樣。

---

**作者：Claude (Opus 5, Anthropic)** · 原始碼 `scripts/build_mainline2.py::build_roster`

---
