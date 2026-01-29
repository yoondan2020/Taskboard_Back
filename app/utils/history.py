from datetime import date, datetime
from typing import Any, Optional

def to_history_value(value: Any) -> Optional[str]:
    """
    히스토리에 저장할 값 정규화 유틸

    규칙:
    - None, "", 공백 -> None
    - date/datetime -> ISO 문자열
    - 그 외 -> str(value)
    """
    if value is None:
        return None

    # 날짜 타입
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    # 문자열/숫자 등
    s = str(value).strip()
    return s if s else None
