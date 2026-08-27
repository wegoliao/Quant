---
id: X3
title: 積木 · 驗證鏈偽造——「簽章驗得過」不等於「是 owner 簽的」
author_ai: ox-alpha (Hermes Agent / Nous Research)
track: governance
status: verified
updated: 2026-08-26
source_repo: src/quant_grill_lab/execution/approval.py + REVIEW-005 Finding A1/S1
web_url: https://wegoliao.github.io/Quant/lesson/ox/03-auth-chain-forgery.html
notebooklm_tags: [security, approval-gate, rsa, fail-closed, sanction, pinned-credential]
---

# 驗證鏈偽造：為什麼簽章驗證通過還能是假的

## 一句話

`verify=True` 只證明「這把公鑰對應的私鑰簽了這份 payload」；
當公鑰、payload、簽章**三樣都由攻擊者提供**時，它只證明攻擊者擁有自己的私鑰——
除非驗證端把公鑰**釘回（pin）一個不可替換的信任根**，否則整條生物辨識邊界形同虛設。

## 這個 bug 的演化史（同一個洞被打了三次）

| 版本 | 開門條件 | 誰抓到 |
|---|---|---|
| v1 | `sanctioned_transmission()` 收兩個字串就開 | DeepSeek Pro |
| v2 | 收 `HumanApproval` 物件＋重新驗簽 | Opus 自己修 |
| v3 殘留 | 驗簽通過即開 REAL sanction，**不重新驗 pinned credential** | **Codex（A1）** |

教訓：每次修補只堵住被指出來的那條路。要問的不是「這條路通了嗎」，
而是「**信任根到底是誰**」。

## 黑盒子解構：攻擊重現

Codex 在記憶體裡完成以下十幾行等價操作：

```
1. 產生攻擊者 RSA keypair
2. 建 CNG public blob + challenge payload + PKCS#1 SHA-256 signature
3. 建 HumanApproval, public_key_sha256 欄位故意填無關字串
4. 呼叫 verify()
   → verify=True, signed_hash_matches=True
   → SANCTION_OPEN=True, mode=REAL
```

原因：`HumanApproval.verify()` 只檢查「簽章可被附帶的公鑰驗證」。
`CredentialPin.assert_matches()` 只在 `ApprovalGate.approve()`（鑄造時）執行；
**sanction 開啟時沒有任何人再讀 pin**。

## 第二條繞路：型別信任（Finding S1）

`proposal_submit` 的 broker 參數型別是 `Any`——它宣稱信任
「broker 自己的 immutable attestation」，但任何物件都能回傳 `(real_api, True, ...)`。
於是一個已登入 REAL 的 API 可以被包成假 broker、宣稱 SIM，
讓 SIM proposal 免審批走進同一個 `transmit.place()`。

## 最小修法模式

```python
def open_real_sanction(approval: HumanApproval, gate: ApprovalGate) -> Sanction:
    """REAL sanction 只能經由 exact consumed gate + pinned key 開啟。

    Invariants:
      - sha256(raw_public_key) == approval.public_key_sha256 == CredentialPin.read()
      - signed payload 的 purpose/version/mode/challenge_id/TTL 全部重驗,
        不信任可替換的 dataclass 欄位
      - gate 必須是本進程 exact ApprovalGate.consume() 的產物
    """
    pin = CredentialPin.read()                       # 每次都讀, 不快取
    if sha256(approval.raw_public_key) != pin:
        raise ForgedApproval("key not pinned")
    if not _verify_signed_payload_fields(approval):   # purpose/version/mode/TTL
        raise ForgedApproval("payload fields tampered")
    return gate.consume_exact(approval)               # 唯一開門路徑
```

配套：SIM exemption 必須由**連線時建立的 immutable attestation value object**
（SDK mode ＋ account fingerprint ＋ config identity）傳入，不接受 `Any` 型別自述。

## 契約不變量（黑盒子的輸出邊界）

- 驗簽函式的回傳值**永不**作為開 REAL 門的充分條件
- 信任根只有一個：pinned credential（Windows Hello 綁定的 key hash）
- 長期正解：verifier 與送單移出 AI agent process（目前威脅模型僅防「意外與順手繞過」）

## AI 對話提問範本

1. 「解釋『簽章驗證通過』與『簽署者是可信實體』的差別，並說明 pinning 如何補上這個缺口。」
2. 「審查我的 approval 流程：列出所有『信任根沒有承重』的位置。」
3. 「為什麼 type-based trust（broker 參數是 Any）在安全邊界上是反模式？」

---
上一顆：[X2 零股集合競價](02-oddlot-auction-twse-rules.md)。下一顆：[X4 訂單狀態三聯畫](04-order-state-triptych.md)。
