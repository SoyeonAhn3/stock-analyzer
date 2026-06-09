"""이메일 발송 모듈 (플러그인) — Phase 14 무료체험 인증코드 전송.

EMAIL_BACKEND 환경변수로 동작이 갈린다:
    - "console" (기본값): 코드를 stdout/로그에 출력만. 실제 발송 없음 (개발/사내망용)
    - "smtp": SMTP 서버로 실제 메일 발송 (배포용)

SMTP 모드 환경변수:
    SMTP_HOST, SMTP_PORT(기본 587), SMTP_USER, SMTP_PASS, SMTP_FROM(선택, 기본=SMTP_USER)

사용법:
    from services.email_sender import send_verification_email
    ok = send_verification_email("user@example.com", "123456")
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_DEFAULT_BACKEND = "console"
_DEFAULT_SMTP_PORT = 587
_APP_NAME = "QuantAI"


def send_verification_email(email: str, code: str) -> bool:
    """인증코드를 이메일로 발송한다.

    Args:
        email: 수신자 이메일 주소
        code: 6자리 인증코드

    Returns:
        발송 성공 시 True, 실패 시 False.
        console 백엔드는 항상 True (출력만 하므로).
    """
    backend = os.environ.get("EMAIL_BACKEND", _DEFAULT_BACKEND).strip().lower()

    if backend == "smtp":
        return _send_via_smtp(email, code)
    return _send_via_console(email, code)


def _send_via_console(email: str, code: str) -> bool:
    """개발/사내망 모드 — 실제 발송 없이 코드를 출력."""
    message = (
        f"\n{'=' * 48}\n"
        f"  [{_APP_NAME}] 이메일 인증코드 (console 모드)\n"
        f"  수신: {email}\n"
        f"  코드: {code}  (10분 후 만료)\n"
        f"{'=' * 48}\n"
    )
    print(message)
    logger.info("Verification code for %s: %s (console backend)", email, code)
    return True


def _send_via_smtp(email: str, code: str) -> bool:
    """배포 모드 — SMTP 서버로 실제 메일 발송."""
    host = os.environ.get("SMTP_HOST", "").strip()
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASS", "").strip()
    port = int(os.environ.get("SMTP_PORT", _DEFAULT_SMTP_PORT))
    sender = os.environ.get("SMTP_FROM", "").strip() or user

    if not host or not user or not password:
        logger.error("SMTP backend selected but SMTP_HOST/USER/PASS not fully configured")
        return False

    body = (
        f"{_APP_NAME} 이메일 인증코드입니다.\n\n"
        f"인증코드: {code}\n\n"
        f"이 코드는 10분 후 만료됩니다.\n"
        f"본인이 요청하지 않았다면 이 메일을 무시하세요."
    )
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"[{_APP_NAME}] 인증코드: {code}"
    msg["From"] = sender
    msg["To"] = email

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(sender, [email], msg.as_string())
        logger.info("Verification email sent to %s via SMTP", email)
        return True
    except Exception as e:
        logger.error("SMTP send failed for %s: %s", email, e)
        return False
