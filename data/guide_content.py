"""Beginner's Guide 콘텐츠 모듈 — 정적 딕셔너리 기반.

사용법:
    from data.guide_content import get_categories, get_topics, get_topic_detail
    cats = get_categories()           # ["chart_basics", ...]
    topics = get_topics("chart_basics")  # [{title, level, ...}, ...]
    detail = get_topic_detail("chart_basics", 0)
"""

from typing import Any, Optional

GUIDE_CONTENT: dict[str, dict[str, Any]] = {
    "chart_basics": {
        "category": "차트 보는 법",
        "topics": [
            {
                "title": "캔들스틱 차트",
                "level": "beginner",
                "what": "일정 기간의 시가·고가·저가·종가를 하나의 봉으로 표현한 차트. 빨간(양봉)은 상승, 파란(음봉)은 하락.",
                "how": "몸통이 길면 강한 방향성, 꼬리(그림자)가 길면 반전 시도가 있었음을 의미.",
                "when": "모든 차트 분석의 기본. 단기 트레이딩부터 장기 투자까지 필수.",
                "example": "NVDA 일봉에서 긴 아래꼬리 양봉 → 저점 매수세 유입 신호.",
            },
            {
                "title": "이동평균선 (MA)",
                "level": "beginner",
                "what": "일정 기간의 종가 평균을 이은 선. MA50(50일), MA200(200일)이 대표적.",
                "how": "주가가 MA 위에 있으면 상승 추세, 아래면 하락 추세. 골든크로스(MA50이 MA200 상향 돌파)는 강세 신호.",
                "when": "추세 방향 확인 시. 매매 타이밍보다는 큰 흐름 파악에 활용.",
                "example": "AAPL MA50이 MA200을 상향 돌파 → 골든크로스 발생, 중장기 상승 신호.",
            },
            {
                "title": "거래량 분석",
                "level": "beginner",
                "what": "일정 기간 동안 거래된 주식 수. 가격 변동의 '확신도'를 측정.",
                "how": "가격 상승 + 거래량 증가 = 강한 상승. 가격 상승 + 거래량 감소 = 약한 상승(반전 주의).",
                "when": "돌파 확인, 추세 강도 평가, 바닥/천장 판단 시.",
                "example": "TSLA 저항선 돌파 시 거래량 3배 급증 → 진짜 돌파로 판단.",
            },
        ],
    },
    "key_metrics": {
        "category": "핵심 지표",
        "topics": [
            {
                "title": "PER (주가수익비율)",
                "level": "beginner",
                "what": "주가 ÷ 주당순이익(EPS). '이 회사 이익의 몇 배를 지불하는가'를 나타냄.",
                "how": "PER 낮으면 저평가, 높으면 고평가 가능성. 단, 성장주는 PER이 높아도 정당화될 수 있음.",
                "when": "같은 섹터 종목 비교, 밸류에이션 판단 시. Forward PER(미래 예상)도 함께 확인.",
                "example": "AAPL PER 28 vs 소비자전자 평균 25 → 약간 프리미엄, 하지만 브랜드 가치 반영.",
            },
            {
                "title": "EPS (주당순이익)",
                "level": "beginner",
                "what": "순이익 ÷ 발행 주식 수. 1주당 얼마를 벌었는지 보여줌.",
                "how": "EPS 성장률이 핵심. 전년 대비 20%+ 성장이면 강한 실적.",
                "when": "실적 발표 시즌(어닝 시즌)에 예상 EPS vs 실제 EPS 비교.",
                "example": "NVDA EPS $4.05 (전년 $1.80) → YoY 125% 성장, AI 수요 반영.",
            },
            {
                "title": "시가총액",
                "level": "beginner",
                "what": "주가 × 발행 주식 수. 시장이 평가하는 기업의 총 가치.",
                "how": "Large Cap($10B+)은 안정적, Mid Cap($2B~$10B)은 성장 잠재력, Small Cap은 고위험 고수익.",
                "when": "투자 유니버스 설정, 포트폴리오 분산 시.",
                "example": "AAPL 시총 $3.5T → 세계 최대 기업, 안정성 최상위.",
            },
            {
                "title": "배당 수익률",
                "level": "intermediate",
                "what": "연간 배당금 ÷ 주가 × 100. 주가 대비 매년 받는 현금 비율.",
                "how": "2~4%면 양호, 5%+ 이면 고배당이지만 지속 가능성 확인 필요.",
                "when": "인컴 투자, 은퇴 포트폴리오 구성 시.",
                "example": "JNJ 배당률 3.1%, 62년 연속 배당 증가 → '배당 귀족'.",
            },
        ],
    },
    "technicals": {
        "category": "기술적 지표",
        "topics": [
            {
                "title": "RSI (상대강도지수)",
                "level": "intermediate",
                "what": "최근 가격 변동의 상승/하락 비율. 0~100 범위. 70+ 과매수, 30- 과매도.",
                "how": "RSI 70 이상이면 단기 조정 가능성, 30 이하면 반등 가능성. 다이버전스도 확인.",
                "when": "매매 타이밍 판단, 과열/침체 확인 시.",
                "example": "MSFT RSI 75 → 과매수 구간, 단기 조정 후 진입 고려.",
            },
            {
                "title": "MACD",
                "level": "intermediate",
                "what": "단기 EMA와 장기 EMA의 차이. 추세의 방향과 강도를 동시에 보여줌.",
                "how": "MACD선이 시그널선 상향 돌파 = 매수 신호, 하향 돌파 = 매도 신호.",
                "when": "추세 전환 포착, 매매 신호 확인 시.",
                "example": "AMD MACD 골든크로스 + 히스토그램 양전환 → 상승 추세 시작.",
            },
            {
                "title": "볼린저 밴드",
                "level": "intermediate",
                "what": "이동평균선 ± 표준편차 2배. 가격이 밴드 안에서 움직이는 범위를 보여줌.",
                "how": "상단 밴드 터치 = 과매수 가능, 하단 밴드 터치 = 과매도 가능. 밴드 폭 축소 = 변동성 폭발 임박.",
                "when": "변동성 판단, 돌파 매매 타이밍 시.",
                "example": "TSLA 볼린저 밴드 수축 후 상단 돌파 + 거래량 급증 → 강한 상승 신호.",
            },
        ],
    },
    "market_concepts": {
        "category": "시장 개념",
        "topics": [
            {
                "title": "불/베어 마켓",
                "level": "beginner",
                "what": "불 마켓: 주가가 20%+ 상승한 지속적 상승장. 베어 마켓: 20%+ 하락한 하락장.",
                "how": "불 마켓에서는 '매수 후 보유'가 유리, 베어 마켓에서는 방어적 자산(채권, 배당주) 비중 확대.",
                "when": "포트폴리오 전략 수립, 시장 사이클 판단 시.",
                "example": "2023~2024년 AI 테마 주도 불 마켓 → NVDA +240%, 나스닥 +40%.",
            },
            {
                "title": "금리와 주식시장",
                "level": "intermediate",
                "what": "중앙은행(Fed)의 기준금리. 높으면 대출 비용 증가 → 기업 이익 감소 → 주가 하락 압력.",
                "how": "금리 인하 시 성장주(테크) 유리, 금리 인상 시 가치주(은행, 에너지) 유리.",
                "when": "FOMC 회의 전후, 매크로 환경 분석 시.",
                "example": "2022년 Fed 급격한 금리 인상 → 나스닥 -33%, 성장주 타격.",
            },
            {
                "title": "VIX (공포지수)",
                "level": "intermediate",
                "what": "S&P 500 옵션의 내재 변동성. 시장의 공포/탐욕 수준 측정.",
                "how": "VIX 20 이하 = 안정, 30+ = 불안, 40+ = 극도의 공포. '공포에 사라'의 지표.",
                "when": "시장 심리 판단, 변동성 매매, 헤지 전략 시.",
                "example": "VIX 35 → 시장 패닉, 역사적으로 6개월 후 반등 확률 80%+.",
            },
        ],
    },
    "investment_styles": {
        "category": "투자 스타일",
        "topics": [
            {
                "title": "성장 투자 (Growth)",
                "level": "beginner",
                "what": "매출/이익이 빠르게 성장하는 기업에 투자. 높은 PER도 감수.",
                "how": "매출 성장률 20%+, Forward PER 25+ 종목 선호. 배당보다 주가 상승에 집중.",
                "when": "강세장, 금리 인하 구간에서 유리.",
                "example": "NVDA, AMD, CRM — AI 성장 테마 수혜주.",
            },
            {
                "title": "가치 투자 (Value)",
                "level": "beginner",
                "what": "내재 가치 대비 저평가된 기업에 투자. 낮은 PER, 높은 배당 선호.",
                "how": "Forward PER < 18, 배당률 2%+, 안정적 실적 기업 선호.",
                "when": "약세장, 금리 인상 구간에서 방어적 성격 발휘.",
                "example": "JNJ, PG, KO — 배당 귀족, 경기 방어주.",
            },
            {
                "title": "균형 투자 (Balanced)",
                "level": "beginner",
                "what": "성장주와 가치주를 적절히 혼합. 리스크 분산이 핵심.",
                "how": "포트폴리오에서 성장주 40~60%, 가치주 30~40%, 채권/현금 10~20%.",
                "when": "시장 방향이 불확실할 때, 장기 투자 시.",
                "example": "AAPL(성장) + JNJ(가치) + BND(채권) 조합.",
            },
        ],
    },
}


def get_categories() -> list[str]:
    """카테고리 키 목록 반환."""
    return list(GUIDE_CONTENT.keys())


def get_category_info(category: str) -> Optional[dict[str, Any]]:
    """카테고리 전체 정보 반환."""
    return GUIDE_CONTENT.get(category)


def get_topics(category: str) -> list[dict[str, Any]]:
    """특정 카테고리의 주제 리스트 반환. 없으면 빈 리스트."""
    cat = GUIDE_CONTENT.get(category)
    if cat is None:
        return []
    return cat.get("topics", [])


def get_topic_detail(category: str, index: int) -> Optional[dict[str, Any]]:
    """특정 주제의 상세 정보 반환.

    Args:
        category: 카테고리 키
        index: 주제 인덱스 (0부터)

    Returns:
        {title, level, what, how, when, example} 또는 None
    """
    topics = get_topics(category)
    if 0 <= index < len(topics):
        return topics[index]
    return None
