"""Phase 3 테스트 — AI Deep Analysis 파이프라인.

Mock 기반 단위 테스트로 코드 로직 검증.
Claude API 실제 호출 없이 Agent 파이프라인의 흐름, 실패 처리, 결과 조립을 테스트.

실행: pytest tests/test_phase3_ai_analysis.py -v
"""

import asyncio
import json
import sys
import os
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.claude_client import call_claude, _parse_json_response
from agents import news_agent, data_agent, macro_agent
from agents import cross_validation, analyst_agent
from agents.orchestrator import run_analysis


# ============================================================
# Mock 데이터
# ============================================================

MOCK_QUICK_LOOK = {
    "ticker": "NVDA",
    "price": 950.0,
    "change": 15.0,
    "change_percent": 1.6,
    "sector": "Technology",
    "industry": "Semiconductors",
    "pe": 35.2,
    "forward_pe": 28.1,
    "eps": 4.05,
    "peg": 1.8,
    "market_cap": 2340000000000,
    "week52_high": 980.0,
    "week52_low": 450.0,
    "de_ratio": 0.41,
    "rsi": {"value": 72, "signal": "bearish"},
    "macd": {"signal": "bullish", "detail": "bullish crossover"},
    "ma50": 890.0,
    "ma200": 750.0,
}

MOCK_NEWS_RESPONSE = {
    "overall_sentiment": "positive",
    "sentiment_score": 0.78,
    "recent_news": [
        {"headline": "NVDA reports record revenue", "sentiment": "positive", "impact": "high"},
    ],
    "earnings": "beat",
    "analyst_consensus": "strong_buy",
    "key_events_upcoming": ["Q1 earnings call"],
    "summary": "Overall positive sentiment driven by strong earnings.",
}

MOCK_DATA_RESPONSE = {
    "price_position": "52주 고점 근접 (97%)",
    "valuation": {"assessment": "fairly_valued", "detail": "PER 35 vs 섹터 평균 30"},
    "technicals_summary": {"trend": "bullish", "signals": ["RSI 72 과매수", "MACD 골든크로스"]},
    "financial_health": {"rating": "strong", "detail": "부채비율 0.41로 양호"},
    "summary": "기술적 과매수 신호가 있으나 재무 건전성은 양호.",
}

MOCK_MACRO_RESPONSE = {
    "fed_rate": "5.25%",
    "rate_outlook": "동결",
    "inflation": {"current": "3.2%", "trend": "하락"},
    "employment": {"unemployment_rate": "3.7%", "assessment": "양호"},
    "sector_trend": "반도체 섹터 AI 수요로 성장세",
    "market_sentiment": "bullish",
    "risk_factors": ["중국 규제 리스크", "금리 인하 지연"],
    "summary": "거시경제 환경은 반도체 섹터에 긍정적.",
}

MOCK_CV_RESPONSE = {
    "conflicts": [
        {"topic": "밸류에이션 vs 모멘텀", "detail": "기술지표 과매수이나 실적 호조", "severity": "medium"},
    ],
    "agreements": ["실적 성장세 동의", "반도체 섹터 전망 긍정"],
    "confidence_adjustment": "none",
    "notes": "모순이 있으나 심각하지 않음.",
}

MOCK_ANALYST_RESPONSE = {
    "verdict": "BUY",
    "confidence": "high",
    "bull_case": "AI 수요 폭발로 실적 서프라이즈 지속 예상",
    "bear_case": "밸류에이션 부담과 금리 리스크 존재",
    "key_factors": ["AI 수요", "실적 성장", "섹터 리더"],
    "risk_level": "medium",
    "time_horizon": "medium_term",
    "summary": "성장 모멘텀이 밸류에이션 부담을 상회한다고 판단.",
    "disclaimer": "본 분석은 AI가 생성한 참고 자료이며, 투자 자문이 아닙니다.",
}


def _mock_claude_success(response_data):
    """call_claude가 성공적으로 JSON을 반환하도록 mock."""
    return {"parsed": True, "data": response_data}


def _mock_claude_failure(error_msg="API 에러"):
    """call_claude가 실패하도록 mock."""
    return {"parsed": False, "raw_output": "", "error": error_msg}


# ============================================================
# 1. claude_client 테스트
# ============================================================

class TestClaudeClient:
    """claude_client.py 단위 테스트."""

    def test_parse_json_direct(self):
        """순수 JSON 응답 파싱."""
        raw = '{"sentiment": "positive", "score": 0.8}'
        result = _parse_json_response(raw)
        assert result["parsed"] is True
        assert result["data"]["sentiment"] == "positive"

    def test_parse_json_code_block(self):
        """```json 블록 파싱."""
        raw = 'Here is the result:\n```json\n{"verdict": "BUY"}\n```\nEnd.'
        result = _parse_json_response(raw)
        assert result["parsed"] is True
        assert result["data"]["verdict"] == "BUY"

    def test_parse_json_embedded(self):
        """텍스트 안에 포함된 JSON 추출."""
        raw = 'Analysis complete. {"verdict": "HOLD", "confidence": "medium"} That is all.'
        result = _parse_json_response(raw)
        assert result["parsed"] is True
        assert result["data"]["verdict"] == "HOLD"

    def test_parse_json_failure(self):
        """JSON이 없는 텍스트."""
        raw = "This is just plain text with no JSON."
        result = _parse_json_response(raw)
        assert result["parsed"] is False
        assert result["raw_output"] == raw

    @patch("agents.claude_client.ANTHROPIC_API_KEY", "")
    def test_call_claude_no_api_key(self):
        """API 키 미설정 시 에러 반환."""
        result = call_claude("system", "user")
        assert result["parsed"] is False
        assert "ANTHROPIC_API_KEY" in result["error"]

    @patch("agents.claude_client.usage_tracker")
    def test_call_claude_exhausted(self, mock_tracker):
        """일일 한도 초과 시 에러 반환."""
        mock_tracker.is_exhausted = True
        result = call_claude("system", "user")
        assert result["parsed"] is False
        assert "한도" in result["error"]


# ============================================================
# 2. News Agent 테스트
# ============================================================

class TestNewsAgent:
    """news_agent.py 단위 테스트."""

    @patch("agents.news_agent.call_claude")
    @patch("agents.news_agent.api_client")
    def test_run_success(self, mock_api, mock_claude):
        """정상 실행: 뉴스 + 애널리스트 데이터 수집 후 Claude 호출."""
        mock_api.get_news.return_value = {
            "articles": [{"headline": "NVDA soars", "source": "Reuters", "summary": "Strong earnings"}],
        }
        mock_api.get_analyst.return_value = {
            "strong_buy": 10, "buy": 5, "hold": 3, "sell": 1, "strong_sell": 0,
        }
        mock_claude.return_value = _mock_claude_success(MOCK_NEWS_RESPONSE)

        result = asyncio.run(news_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["agent"] == "news"
        assert result["status"] == "success"
        assert result["overall_sentiment"] == "positive"
        mock_claude.assert_called_once()

    @patch("agents.news_agent.call_claude")
    @patch("agents.news_agent.api_client")
    def test_run_no_news(self, mock_api, mock_claude):
        """뉴스 없어도 실행 가능."""
        mock_api.get_news.return_value = None
        mock_api.get_analyst.return_value = None
        mock_claude.return_value = _mock_claude_success(MOCK_NEWS_RESPONSE)

        result = asyncio.run(news_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["status"] == "success"

    @patch("agents.news_agent.call_claude")
    @patch("agents.news_agent.api_client")
    def test_run_claude_failure(self, mock_api, mock_claude):
        """Claude 호출 실패 시 예외 발생."""
        mock_api.get_news.return_value = None
        mock_api.get_analyst.return_value = None
        mock_claude.return_value = _mock_claude_failure()

        with pytest.raises(RuntimeError, match="News Agent 실패"):
            asyncio.run(news_agent.run("NVDA", MOCK_QUICK_LOOK))

    @patch("agents.news_agent.call_claude")
    @patch("agents.news_agent.api_client")
    def test_run_partial_result(self, mock_api, mock_claude):
        """JSON 파싱 실패 시 raw_output으로 partial 반환."""
        mock_api.get_news.return_value = None
        mock_api.get_analyst.return_value = None
        mock_claude.return_value = {
            "parsed": False,
            "raw_output": "Sentiment is positive overall",
            "error": "JSON 파싱 실패",
        }

        result = asyncio.run(news_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["status"] == "partial"
        assert "raw_output" in result


# ============================================================
# 3. Data Agent 테스트
# ============================================================

class TestDataAgent:
    """data_agent.py 단위 테스트."""

    @patch("agents.data_agent.call_claude")
    def test_run_success(self, mock_claude):
        """정상 실행: quick_look_data 재사용 확인."""
        mock_claude.return_value = _mock_claude_success(MOCK_DATA_RESPONSE)

        result = asyncio.run(data_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["agent"] == "data"
        assert result["status"] == "success"
        assert "valuation" in result
        mock_claude.assert_called_once()

    @patch("agents.data_agent.call_claude")
    def test_run_includes_fundamentals_in_prompt(self, mock_claude):
        """프롬프트에 재무 지표가 포함되는지 확인."""
        mock_claude.return_value = _mock_claude_success(MOCK_DATA_RESPONSE)
        asyncio.run(data_agent.run("NVDA", MOCK_QUICK_LOOK))

        call_args = mock_claude.call_args[0]
        user_message = call_args[1]
        assert "PER" in user_message
        assert "35.2" in user_message

    @patch("agents.data_agent.call_claude")
    def test_run_failure(self, mock_claude):
        """Claude 실패 시 예외."""
        mock_claude.return_value = _mock_claude_failure()
        with pytest.raises(RuntimeError, match="Data Agent 실패"):
            asyncio.run(data_agent.run("NVDA", MOCK_QUICK_LOOK))


# ============================================================
# 4. Macro Agent 테스트
# ============================================================

class TestMacroAgent:
    """macro_agent.py 단위 테스트."""

    @patch("agents.macro_agent.call_claude")
    @patch("agents.macro_agent.api_client")
    def test_run_success(self, mock_api, mock_claude):
        """정상 실행: FRED 데이터 수집 후 Claude 호출."""
        mock_api.get_macro.return_value = {
            "fed_rate": 5.25, "cpi": 3.2, "unemployment": 3.7,
        }
        mock_claude.return_value = _mock_claude_success(MOCK_MACRO_RESPONSE)

        result = asyncio.run(macro_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["agent"] == "macro"
        assert result["status"] == "success"
        assert "fed_rate" in result

    @patch("agents.macro_agent.call_claude")
    @patch("agents.macro_agent.api_client")
    def test_run_no_macro_data(self, mock_api, mock_claude):
        """FRED 실패해도 실행 가능."""
        mock_api.get_macro.return_value = None
        mock_claude.return_value = _mock_claude_success(MOCK_MACRO_RESPONSE)

        result = asyncio.run(macro_agent.run("NVDA", MOCK_QUICK_LOOK))
        assert result["status"] == "success"


# ============================================================
# 5. Cross-validation 테스트
# ============================================================

class TestCrossValidation:
    """cross_validation.py 단위 테스트."""

    @patch("agents.cross_validation.call_claude")
    def test_run_success(self, mock_claude):
        """정상 교차검증."""
        mock_claude.return_value = _mock_claude_success(MOCK_CV_RESPONSE)

        agent_results = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
            "macro": {"agent": "macro", "status": "success", **MOCK_MACRO_RESPONSE},
        }
        result = cross_validation.run(agent_results)
        assert result["status"] == "success"
        assert len(result["conflicts"]) > 0

    @patch("agents.cross_validation.call_claude")
    def test_run_partial_agents(self, mock_claude):
        """Agent 2개만 성공해도 교차검증 가능."""
        mock_claude.return_value = _mock_claude_success(MOCK_CV_RESPONSE)

        agent_results = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
        }
        result = cross_validation.run(agent_results)
        assert result["status"] == "success"

    def test_run_empty_results(self):
        """Agent 결과 없으면 기본 결과 반환 (예외 아님)."""
        result = cross_validation.run({})
        assert result["status"] == "skipped"
        assert result["confidence_adjustment"] == "none"

    @patch("agents.cross_validation.call_claude")
    def test_run_claude_failure(self, mock_claude):
        """Claude 실패해도 기본 결과 반환 (파이프라인 중단 안 함)."""
        mock_claude.return_value = _mock_claude_failure()

        agent_results = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
        }
        result = cross_validation.run(agent_results)
        # 실패해도 에러가 아닌 기본 결과
        assert result["confidence_adjustment"] == "none"


# ============================================================
# 6. Analyst Agent 테스트
# ============================================================

class TestAnalystAgent:
    """analyst_agent.py 단위 테스트."""

    @patch("agents.analyst_agent.call_claude")
    def test_run_success(self, mock_claude):
        """정상 최종 판단."""
        mock_claude.return_value = _mock_claude_success(MOCK_ANALYST_RESPONSE)

        agent_results = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
            "macro": {"agent": "macro", "status": "success", **MOCK_MACRO_RESPONSE},
        }
        cv = {"agent": "cross_validation", "status": "success", **MOCK_CV_RESPONSE}

        result = analyst_agent.run(agent_results, cv, success_count=3)
        assert result["verdict"] == "BUY"
        assert result["confidence"] == "high"  # 3/3 성공 → 유지
        assert "disclaimer" in result

    @patch("agents.analyst_agent.call_claude")
    def test_confidence_downgrade_2_of_3(self, mock_claude):
        """2/3 성공 시 신뢰도 1단계 하향."""
        response = {**MOCK_ANALYST_RESPONSE, "confidence": "high"}
        mock_claude.return_value = _mock_claude_success(response)

        result = analyst_agent.run({}, {}, success_count=2)
        assert result["confidence"] == "medium"  # high → medium

    @patch("agents.analyst_agent.call_claude")
    def test_confidence_downgrade_1_of_3(self, mock_claude):
        """1/3 성공 시 신뢰도 low 고정."""
        response = {**MOCK_ANALYST_RESPONSE, "confidence": "high"}
        mock_claude.return_value = _mock_claude_success(response)

        result = analyst_agent.run({}, {}, success_count=1)
        assert result["confidence"] == "low"  # 강제 low

    @patch("agents.analyst_agent.call_claude")
    def test_run_claude_failure(self, mock_claude):
        """Claude 실패 시 HOLD + low 반환 (예외 아님)."""
        mock_claude.return_value = _mock_claude_failure()

        result = analyst_agent.run({}, {}, success_count=1)
        assert result["verdict"] == "HOLD"
        assert result["confidence"] == "low"


# ============================================================
# 7. Orchestrator 테스트
# ============================================================

class TestOrchestrator:
    """orchestrator.py 단위 테스트."""

    def test_full_pipeline_with_overrides(self):
        """agent_overrides로 전체 파이프라인 mock 테스트."""
        overrides = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
            "macro": {"agent": "macro", "status": "success", **MOCK_MACRO_RESPONSE},
        }

        with patch("agents.cross_validation.call_claude") as mock_cv, \
             patch("agents.analyst_agent.call_claude") as mock_analyst:
            mock_cv.return_value = _mock_claude_success(MOCK_CV_RESPONSE)
            mock_analyst.return_value = _mock_claude_success(MOCK_ANALYST_RESPONSE)

            result = asyncio.run(run_analysis(MOCK_QUICK_LOOK, agent_overrides=overrides))

        assert result["ticker"] == "NVDA"
        assert result["agent_status"] == {"news": "success", "data": "success", "macro": "success"}
        assert result["analyst"]["verdict"] == "BUY"
        assert result["cross_validation"]["status"] == "success"
        assert result["errors"] == []

    def test_all_agents_fail(self):
        """모든 Agent 실패 시 분석 중단."""
        with patch("agents.news_agent.run", side_effect=RuntimeError("fail")), \
             patch("agents.data_agent.run", side_effect=RuntimeError("fail")), \
             patch("agents.macro_agent.run", side_effect=RuntimeError("fail")):

            result = asyncio.run(run_analysis(MOCK_QUICK_LOOK))

        assert result["analyst"] is None
        assert result["cross_validation"] is None
        assert len(result["errors"]) == 3

    def test_partial_agent_failure(self):
        """1개 Agent 실패, 2개 성공 시 분석 계속."""
        overrides = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
        }

        with patch("agents.macro_agent.run", side_effect=RuntimeError("FRED fail")), \
             patch("agents.cross_validation.call_claude") as mock_cv, \
             patch("agents.analyst_agent.call_claude") as mock_analyst:
            mock_cv.return_value = _mock_claude_success(MOCK_CV_RESPONSE)
            mock_analyst.return_value = _mock_claude_success(MOCK_ANALYST_RESPONSE)

            result = asyncio.run(run_analysis(MOCK_QUICK_LOOK, agent_overrides=overrides))

        assert result["agent_status"]["news"] == "success"
        assert result["agent_status"]["data"] == "success"
        assert result["agent_status"]["macro"] == "failed"
        assert result["analyst"] is not None  # 분석 계속됨
        assert len(result["errors"]) == 1

    def test_graceful_degradation_confidence(self):
        """2/3 성공 시 신뢰도 하향 확인."""
        overrides = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
        }

        with patch("agents.data_agent.run", side_effect=RuntimeError("fail")), \
             patch("agents.macro_agent.run", side_effect=RuntimeError("fail")), \
             patch("agents.cross_validation.call_claude") as mock_cv, \
             patch("agents.analyst_agent.call_claude") as mock_analyst:
            mock_cv.return_value = _mock_claude_success(MOCK_CV_RESPONSE)
            response = {**MOCK_ANALYST_RESPONSE, "confidence": "high"}
            mock_analyst.return_value = _mock_claude_success(response)

            result = asyncio.run(run_analysis(MOCK_QUICK_LOOK, agent_overrides=overrides))

        # 1/3 성공 → confidence low 고정
        assert result["analyst"]["confidence"] == "low"

    @patch("agents.orchestrator.AGENT_TIMEOUT", 0.01)
    @patch("agents.orchestrator.AGENT_RETRY_DELAY", 0.01)
    def test_agent_timeout(self):
        """Agent 타임아웃 시 재시도 후 실패."""

        async def slow_agent(ticker, data):
            await asyncio.sleep(10)
            return {}

        overrides = {
            "news": {"agent": "news", "status": "success", **MOCK_NEWS_RESPONSE},
            "data": {"agent": "data", "status": "success", **MOCK_DATA_RESPONSE},
        }

        with patch("agents.macro_agent.run", side_effect=slow_agent), \
             patch("agents.cross_validation.call_claude") as mock_cv, \
             patch("agents.analyst_agent.call_claude") as mock_analyst:
            mock_cv.return_value = _mock_claude_success(MOCK_CV_RESPONSE)
            mock_analyst.return_value = _mock_claude_success(MOCK_ANALYST_RESPONSE)

            result = asyncio.run(run_analysis(MOCK_QUICK_LOOK, agent_overrides=overrides))

        assert result["agent_status"]["macro"] == "failed"
        assert result["analyst"] is not None  # 나머지로 계속 분석


# ============================================================
# 8. Usage Tracker 연동 테스트
# ============================================================

class TestUsageTrackerIntegration:
    """usage_tracker와 claude_client 연동 테스트."""

    @patch("agents.claude_client.Anthropic")
    @patch("agents.claude_client.ANTHROPIC_API_KEY", "test-key")
    def test_increment_on_call(self, mock_anthropic_cls):
        """Claude 호출 시 usage_tracker가 증가하는지 확인."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"result": "ok"}')]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        mock_client.messages.create.return_value = mock_response

        from utils.usage_tracker import usage_tracker
        before = usage_tracker.count
        call_claude("test system", "test user")
        after = usage_tracker.count
        assert after == before + 1
