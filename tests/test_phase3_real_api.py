"""Phase 3 실제 API 테스트 - AI Deep Analysis 파이프라인.

실제 Claude API + 금융 API를 호출하여 전체 파이프라인을 검증한다.
Claude API 호출 비용 발생 (1회 실행 약 $0.05~0.10).

실행: pytest tests/test_phase3_real_api.py -v -s
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from agents.claude_client import call_claude, _parse_json_response
from agents import news_agent, data_agent, macro_agent
from agents import cross_validation, analyst_agent
from agents.orchestrator import run_analysis
from data.quote import get_quote
from data.fundamentals import get_fundamentals
from data.technicals import get_technicals
from data.cache import cache
from utils.usage_tracker import usage_tracker

TICKER = "AAPL"


# ============================================================
# 0. Quick Look 데이터 수집 (Phase 2 재사용)
# ============================================================

@pytest.fixture(scope="module")
def quick_look_data():
    """실제 API로 Quick Look 데이터를 한 번만 수집."""
    cache.clear()
    quote = get_quote(TICKER)
    fundamentals = get_fundamentals(TICKER)
    technicals = get_technicals(TICKER)

    data = {"ticker": TICKER}
    if quote:
        data.update({
            "price": quote["price"],
            "change": quote.get("change"),
            "change_percent": quote.get("change_percent"),
        })
    if fundamentals:
        data.update({
            "pe": fundamentals.get("pe"),
            "forward_pe": fundamentals.get("forward_pe"),
            "eps": fundamentals.get("eps"),
            "peg": fundamentals.get("peg"),
            "market_cap": fundamentals.get("market_cap"),
            "week52_high": fundamentals.get("week52_high"),
            "week52_low": fundamentals.get("week52_low"),
            "de_ratio": fundamentals.get("de_ratio"),
            "sector": fundamentals.get("sector"),
            "industry": fundamentals.get("industry"),
        })
    if technicals:
        data.update({
            "rsi": technicals.get("rsi"),
            "macd": technicals.get("macd"),
            "ma50": technicals.get("ma50"),
            "ma200": technicals.get("ma200"),
        })

    print(f"\n  Quick Look: {TICKER} ${data.get('price')}, "
          f"sector={data.get('sector')}, PE={data.get('pe')}")
    return data


# ============================================================
# 1. claude_client - 실제 Claude API 호출
# ============================================================

def _call_claude_with_retry(system, user, max_retries=3):
    """529 Overloaded 대비 재시도."""
    import time
    for attempt in range(max_retries):
        result = call_claude(system, user)
        if result["parsed"] or "overloaded" not in result.get("error", "").lower():
            return result
        if attempt < max_retries - 1:
            time.sleep(5)
    return result


class TestClaudeClientReal:
    def test_call_claude_simple(self):
        """Claude API 기본 호출 - JSON 응답."""
        result = _call_claude_with_retry(
            "You are a helpful assistant. Always respond in JSON format.",
            'Respond with: {"status": "ok", "message": "hello"}'
        )
        assert result["parsed"] is True, f"Claude call failed: {result.get('error')}"
        assert "status" in result["data"]
        print(f"  Claude response: {result['data']}")

    def test_call_claude_stock_analysis_json(self):
        """Claude API - 주식 분석 JSON 응답 파싱."""
        result = _call_claude_with_retry(
            "You are a stock analyst. Always respond in JSON.",
            'Analyze: AAPL is at $260, PE=33. Respond with JSON: '
            '{"sentiment": "...", "reason": "..."}'
        )
        assert result["parsed"] is True, f"JSON parsing failed: {result.get('error')}"
        print(f"  Analysis: {result['data']}")

    def test_usage_tracker_increments(self):
        """Claude 호출 시 usage_tracker 증가."""
        before = usage_tracker.count
        result = _call_claude_with_retry(
            "Respond in JSON.",
            'Respond: {"test": true}'
        )
        after = usage_tracker.count
        if result["parsed"]:
            assert after == before + 1
            print(f"  Usage: {before} -> {after}")
        else:
            pytest.skip(f"Claude API unavailable: {result.get('error', '')[:50]}")


# ============================================================
# 2. News Agent - 실제 실행
# ============================================================

class TestNewsAgentReal:
    def test_run(self, quick_look_data):
        """News Agent - 실제 뉴스 수집 + Claude 분석."""
        result = asyncio.run(news_agent.run(TICKER, quick_look_data))

        assert result["agent"] == "news"
        assert result["status"] in ("success", "partial")
        print(f"  News Agent status: {result['status']}")

        if result["status"] == "success":
            assert "overall_sentiment" in result
            assert result["overall_sentiment"] in ("positive", "negative", "neutral", "mixed")
            print(f"  Sentiment: {result['overall_sentiment']} "
                  f"(score={result.get('sentiment_score')})")
            print(f"  Analyst consensus: {result.get('analyst_consensus')}")
            print(f"  Summary: {result.get('summary', '')[:100]}...")


# ============================================================
# 3. Data Agent - 실제 실행
# ============================================================

class TestDataAgentReal:
    def test_run(self, quick_look_data):
        """Data Agent - Quick Look 데이터 재사용 + Claude 해석."""
        result = asyncio.run(data_agent.run(TICKER, quick_look_data))

        assert result["agent"] == "data"
        assert result["status"] in ("success", "partial")
        print(f"  Data Agent status: {result['status']}")

        if result["status"] == "success":
            assert "valuation" in result
            assert "technicals_summary" in result
            print(f"  Valuation: {result['valuation'].get('assessment')}")
            print(f"  Trend: {result['technicals_summary'].get('trend')}")
            print(f"  Health: {result.get('financial_health', {}).get('rating')}")
            print(f"  Summary: {result.get('summary', '')[:100]}...")


# ============================================================
# 4. Macro Agent - 실제 실행
# ============================================================

class TestMacroAgentReal:
    def test_run(self, quick_look_data):
        """Macro Agent - FRED 데이터 수집 + Claude 분석."""
        result = asyncio.run(macro_agent.run(TICKER, quick_look_data))

        assert result["agent"] == "macro"
        assert result["status"] in ("success", "partial")
        print(f"  Macro Agent status: {result['status']}")

        if result["status"] == "success":
            assert "fed_rate" in result
            assert "market_sentiment" in result
            print(f"  Fed rate: {result.get('fed_rate')}")
            print(f"  Rate outlook: {result.get('rate_outlook')}")
            print(f"  Market sentiment: {result['market_sentiment']}")
            print(f"  Risk factors: {result.get('risk_factors', [])}")
            print(f"  Summary: {result.get('summary', '')[:100]}...")


# ============================================================
# 5. Cross-validation - 실제 실행
# ============================================================

class TestCrossValidationReal:
    def test_run(self, quick_look_data):
        """Cross-validation - 3개 Agent 실제 결과로 교차검증."""
        # 3개 Agent 실행
        news_result = asyncio.run(news_agent.run(TICKER, quick_look_data))
        data_result = asyncio.run(data_agent.run(TICKER, quick_look_data))
        macro_result = asyncio.run(macro_agent.run(TICKER, quick_look_data))

        agent_results = {}
        if news_result["status"] in ("success", "partial"):
            agent_results["news"] = news_result
        if data_result["status"] in ("success", "partial"):
            agent_results["data"] = data_result
        if macro_result["status"] in ("success", "partial"):
            agent_results["macro"] = macro_result

        assert len(agent_results) > 0, "All agents failed"

        # 교차검증
        result = cross_validation.run(agent_results)
        assert result["agent"] == "cross_validation"
        assert result["status"] in ("success", "partial", "skipped")
        print(f"  Cross-validation status: {result['status']}")

        if result["status"] == "success":
            print(f"  Conflicts: {len(result.get('conflicts', []))}")
            for c in result.get("conflicts", []):
                print(f"    - [{c.get('severity')}] {c.get('topic')}: {c.get('detail', '')[:60]}")
            print(f"  Agreements: {result.get('agreements', [])}")
            print(f"  Confidence adj: {result.get('confidence_adjustment')}")


# ============================================================
# 6. Full Pipeline - 오케스트레이터 실제 실행
# ============================================================

class TestFullPipelineReal:
    def test_run_analysis(self, quick_look_data):
        """전체 파이프라인 - 실제 AI Deep Analysis."""
        cache.clear()
        result = asyncio.run(run_analysis(quick_look_data))

        # 기본 구조 검증
        assert result["ticker"] == TICKER
        assert "agent_status" in result
        assert "agent_results" in result
        assert "cross_validation" in result
        assert "analyst" in result
        assert isinstance(result["errors"], list)

        # Agent 상태
        status = result["agent_status"]
        success_count = list(status.values()).count("success")
        print(f"\n  === AI Deep Analysis Complete: {TICKER} ===")
        print(f"  Agent status: {status}")
        print(f"  Success: {success_count}/3")
        print(f"  Errors: {result['errors']}")

        # 최소 1개 Agent는 성공해야 함
        assert success_count >= 1, f"All agents failed: {result['errors']}"

        # Cross-validation
        cv = result["cross_validation"]
        if cv:
            print(f"  Cross-validation: {cv.get('status')}")

        # Analyst (최종 판단)
        analyst = result["analyst"]
        if analyst:
            assert analyst["verdict"] in ("BUY", "HOLD", "SELL")
            assert analyst["confidence"] in ("high", "medium", "low")
            assert "disclaimer" in analyst

            print(f"\n  --- Final Verdict ---")
            print(f"  Verdict: {analyst['verdict']}")
            print(f"  Confidence: {analyst['confidence']}")
            print(f"  Risk: {analyst.get('risk_level')}")
            print(f"  Time horizon: {analyst.get('time_horizon')}")
            if analyst.get("bull_case"):
                print(f"  Bull: {analyst['bull_case'][:80]}...")
            if analyst.get("bear_case"):
                print(f"  Bear: {analyst['bear_case'][:80]}...")
            if analyst.get("key_factors"):
                print(f"  Key factors: {analyst['key_factors']}")
            print(f"  Summary: {analyst.get('summary', '')[:120]}...")
            print(f"  Disclaimer: OK")

    def test_usage_after_pipeline(self):
        """파이프라인 실행 후 usage_tracker 정상 동작 확인."""
        count = usage_tracker.count
        assert count > 0
        print(f"  Total AI usage today: {usage_tracker.status_text()}")
