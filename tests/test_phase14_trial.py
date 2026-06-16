"""Phase 14 테스트 — 무료체험 크레딧 지갑 + Google 로그인 게이트.

지갑 코어(reserve/commit/release)와 인증 의존성(get_current_user)을
실제 Google 네트워크 호출 없이 단위 검증한다.

신원 키(device_id 컬럼)에는 Google sub가 들어가지만, 지갑 로직은
키 값의 출처를 모르므로 테스트에서는 평범한 문자열을 sub 대신 사용한다.

실행: pytest tests/test_phase14_trial.py -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import database
from services import trial_service as ts


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """격리된 임시 SQLite DB로 교체한 뒤 스키마 초기화."""
    db_file = tmp_path / "test_app.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()
    yield db_file


SUB = "google-sub-1234567890"   # 검증된 Google sub 자리 (테스트용 문자열)


# ============================================================
# 지갑 생성 / 상태
# ============================================================

def test_initial_wallet_has_3_credits(temp_db):
    status = ts.get_or_create_user(SUB)
    assert status["balance"] == ts.INITIAL_CREDITS == 3
    assert status["held"] == 0
    assert status["available"] == 3


def test_get_status_is_readonly_and_idempotent(temp_db):
    ts.get_or_create_user(SUB)
    a = ts.get_status(SUB)
    b = ts.get_status(SUB)
    assert a == b == {"balance": 3, "held": 0, "available": 3}


# ============================================================
# reserve → commit (성공 경로)
# ============================================================

def test_reserve_holds_one_credit(temp_db):
    r = ts.reserve_credit(SUB, "req-1")
    assert r["ok"] is True
    assert r["held"] == 1
    assert r["available"] == 2
    assert r["balance"] == 3   # 아직 차감 전


def test_commit_deducts_balance(temp_db):
    ts.reserve_credit(SUB, "req-1")
    c = ts.commit_credit(SUB, "req-1")
    assert c["ok"] is True
    assert c["balance"] == 2
    assert c["held"] == 0
    assert c["available"] == 2


# ============================================================
# reserve → release (실패 환불 경로)
# ============================================================

def test_release_refunds_without_charging(temp_db):
    ts.reserve_credit(SUB, "req-1")
    rel = ts.release_credit(SUB, "req-1")
    assert rel["ok"] is True
    assert rel["balance"] == 3   # 환불 — 차감 안 됨
    assert rel["held"] == 0
    assert rel["available"] == 3


# ============================================================
# 한도 소진 → 429 (no_credit)
# ============================================================

def test_exhausting_credits_blocks_further_reserve(temp_db):
    # 3회 예약+확정으로 잔액 소진
    for i in range(3):
        assert ts.reserve_credit(SUB, f"req-{i}")["ok"] is True
        assert ts.commit_credit(SUB, f"req-{i}")["ok"] is True

    # 4번째는 거절
    blocked = ts.reserve_credit(SUB, "req-4")
    assert blocked["ok"] is False
    assert blocked["reason"] == "no_credit"
    assert blocked["available"] == 0
    assert blocked["balance"] == 0


# ============================================================
# 멱등성 — 같은 ref_id 재시도는 중복 차감 안 됨
# ============================================================

def test_reserve_is_idempotent_per_ref_id(temp_db):
    first = ts.reserve_credit(SUB, "same-ref")
    second = ts.reserve_credit(SUB, "same-ref")
    assert first["ok"] is True
    assert second["ok"] is True
    assert second.get("already") is True
    # 두 번 호출했어도 hold는 1개만
    assert second["held"] == 1
    assert second["available"] == 2


def test_commit_is_idempotent_per_ref_id(temp_db):
    ts.reserve_credit(SUB, "same-ref")
    ts.commit_credit(SUB, "same-ref")
    again = ts.commit_credit(SUB, "same-ref")
    assert again["ok"] is True
    assert again.get("already") is True
    assert again["balance"] == 2   # 한 번만 차감


def test_wallets_are_isolated_per_sub(temp_db):
    ts.reserve_credit(SUB, "req-1")
    ts.commit_credit(SUB, "req-1")
    other = ts.get_status("another-google-sub")
    assert other["balance"] == 3   # 다른 계정은 영향 없음


# ============================================================
# 인증 의존성 — 네트워크 없이 401 경로 검증
# ============================================================

def test_get_current_user_rejects_missing_header():
    from fastapi import HTTPException
    from backend.auth import get_current_user

    with pytest.raises(HTTPException) as exc:
        get_current_user(None)
    assert exc.value.status_code == 401


def test_get_current_user_rejects_non_bearer():
    from fastapi import HTTPException
    from backend.auth import get_current_user

    with pytest.raises(HTTPException) as exc:
        get_current_user("Token abc123")
    assert exc.value.status_code == 401


def test_get_current_user_rejects_empty_bearer():
    from fastapi import HTTPException
    from backend.auth import get_current_user

    with pytest.raises(HTTPException) as exc:
        get_current_user("Bearer    ")
    assert exc.value.status_code == 401
