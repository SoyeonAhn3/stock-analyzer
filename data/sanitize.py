"""로그 출력 시 API 키 마스킹 유틸."""

import re

_KEY_PARAMS = re.compile(
    r'(api_?key|apikey|token)=([^&\s\'"]+)',
    re.IGNORECASE,
)


def mask_sensitive(text: str) -> str:
    """URL/에러 메시지에서 API 키 파라미터 값을 마스킹한다."""
    return _KEY_PARAMS.sub(r'\1=****', str(text))
