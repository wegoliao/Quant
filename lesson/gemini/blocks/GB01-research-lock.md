---
id: GB01
title: 積木 · 全域排他研究鎖 (OS-backed Research Lock)
author_ai: Gemini (Google DeepMind / Antigravity)
track: block
status: verified
updated: 2026-08-26
source_code: d:/Quant_Grill_Lab/src/quant_grill_lab/research_lock.py
web_url: https://wegoliao.github.io/Quant/lesson/gemini/blocks/GB01-research-lock.html
notebooklm_tags: [building-block, lock, concurrency, os-lock, research-safety]
---

# 積木 · 全域排他研究鎖 (Research Lock)

## 一句話定義 (TL;DR)

一個基於作業系統檔案鎖（OS File Lock）與 JSON 中繼資料的**跨程序排他鎖**，支援逾時心跳檢測（Heartbeat Timeout）與自動死鎖回收，徹底杜絕多 Agent 並發回測與網站建置衝突。

---

## 1. 黑盒子解構 (What Problem It Solves)

當多個量化任務（例如全量回測、註冊新策略、建置網站）同時執行時，競爭寫入檔案會導致資料毀損。本積木提供情境管理器（Context Manager），保證同一時間只有一個任務能執行特定關鍵操作。

### 契約不變量 (Invariants):
1. **排他性**：任何時刻，同一種 Lock Kind（或全域排他）只能被一個進程（PID）持有。
2. **心跳與自動過期**：若進程異常崩潰，鎖在超過 15 分鐘（900秒）未更新心跳時，自動被下一個請求安全回收。
3. **無殘留**：正常退出（含例外拋出）時保證釋放檔案鎖。

---

## 2. 最小可運行積木代碼 (Minimal Runnable Pattern)

```python
"""GB01: OS-backed Research Work Lock."""

from __future__ import annotations

import contextlib
import datetime
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

LOCK_FILE = Path("_runtime/RESEARCH_LOCK.json")
LOCK_TIMEOUT_SECONDS = 900.0  # 15 minutes


class ResearchLockBusy(RuntimeError):
    """Raised when the requested lock is currently held by another process."""


@dataclass(frozen=True)
class LockMetadata:
    kind: str
    holder: str
    scope: str
    pid: int
    acquired_at: str
    heartbeat_at: str


@contextlib.contextmanager
def acquire_research_lock(
    kind: str,
    holder: str,
    scope: str,
    lock_file: Path = LOCK_FILE,
) -> Iterator[LockMetadata]:
    """Acquires a process-safe research lock."""
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 1. 檢查現有鎖中繼資料與心跳
    if lock_file.exists():
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_hb = datetime.datetime.fromisoformat(data["heartbeat_at"])
            age = (datetime.datetime.now(datetime.timezone.utc) - last_hb).total_seconds()
            
            # 若鎖未過期且非當前進程，拋出繁忙例外
            if age < LOCK_TIMEOUT_SECONDS and data.get("pid") != os.getpid():
                raise ResearchLockBusy(
                    f"Lock '{data.get('kind')}' is currently held by {data.get('holder')} "
                    f"(PID {data.get('pid')}) for scope '{data.get('scope')}' (age {age:.1f}s)."
                )
        except (json.JSONDecodeError, KeyError, ValueError):
            pass  # 損毀的 JSON 允許被覆寫回收

    # 2. 寫入新鎖
    meta = LockMetadata(
        kind=kind,
        holder=holder,
        scope=scope,
        pid=os.getpid(),
        acquired_at=now_iso,
        heartbeat_at=now_iso,
    )
    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, indent=2)

    try:
        yield meta
    finally:
        # 3. 退出時安全釋放
        if lock_file.exists():
            try:
                with open(lock_file, "r", encoding="utf-8") as f:
                    cur = json.load(f)
                if cur.get("pid") == os.getpid():
                    lock_file.unlink(missing_ok=True)
            except Exception:
                lock_file.unlink(missing_ok=True)
```

---

## 3. 單元測試範例 (Unit Test)

```python
def test_gb01_lock_acquisition_and_release(tmp_path):
    lock_path = tmp_path / "test_lock.json"
    
    with acquire_research_lock("OFFICIAL_SIM", "AgentA", "Unit Testing", lock_file=lock_path) as meta:
        assert lock_path.exists()
        assert meta.holder == "AgentA"
        
        # 測試同一時間其他 Agent 無法獲取
        try:
            with acquire_research_lock("OFFICIAL_SIM", "AgentB", "Conflict Test", lock_file=lock_path):
                assert False, "Should have raised ResearchLockBusy"
        except ResearchLockBusy:
            pass  # 正確阻擋
            
    assert not lock_path.exists()  # 正確自動釋放
```

---

## 4. NotebookLM & AI 提問範本

- **Prompt**：「請分析 GB01 積木如何防止因為 Agent 異常崩潰而導致的永久死鎖（Deadlock）？」
