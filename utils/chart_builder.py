"""차트 빌더 모듈 — Plotly figure 객체 생성.

사용법:
    from utils.chart_builder import build_price_chart
    fig = build_price_chart(df, chart_type="candlestick")
    # UI에서: st.plotly_chart(fig)
"""

import logging
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

# 차트 색상
COLOR_UP = "#26a69a"
COLOR_DOWN = "#ef5350"
COLOR_MA50 = "#ff9800"
COLOR_MA200 = "#2196f3"
COLOR_VOLUME = "rgba(100, 100, 100, 0.3)"


def build_price_chart(
    df: pd.DataFrame,
    chart_type: str = "line",
    show_ma: bool = True,
    title: str = "",
) -> Optional[go.Figure]:
    """주가 차트 + 거래량 바 차트 생성.

    Args:
        df: DataFrame (Date, Open, High, Low, Close, Volume, MA50, MA200)
        chart_type: 'line' | 'candlestick'
        show_ma: True면 MA50/MA200 오버레이
        title: 차트 제목

    Returns:
        Plotly Figure 객체. 실패 시 None.
    """
    if df is None or df.empty or "Close" not in df.columns:
        return None

    has_volume = "Volume" in df.columns
    row_heights = [0.7, 0.3] if has_volume else [1.0]
    rows = 2 if has_volume else 1

    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    x = df["Date"] if "Date" in df.columns else df.index

    # 주가 차트
    if chart_type == "candlestick" and all(c in df.columns for c in ["Open", "High", "Low", "Close"]):
        fig.add_trace(
            go.Candlestick(
                x=x,
                open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"],
                increasing_line_color=COLOR_UP,
                decreasing_line_color=COLOR_DOWN,
                name="Price",
            ),
            row=1, col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(
                x=x, y=df["Close"],
                mode="lines",
                name="Price",
                line=dict(color=COLOR_UP, width=1.5),
            ),
            row=1, col=1,
        )

    # 이동평균 오버레이
    if show_ma:
        if "MA50" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x, y=df["MA50"],
                    mode="lines", name="MA50",
                    line=dict(color=COLOR_MA50, width=1, dash="dot"),
                ),
                row=1, col=1,
            )
        if "MA200" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x, y=df["MA200"],
                    mode="lines", name="MA200",
                    line=dict(color=COLOR_MA200, width=1, dash="dot"),
                ),
                row=1, col=1,
            )

    # 거래량 바 차트
    if has_volume:
        colors = []
        for i in range(len(df)):
            if i == 0:
                colors.append(COLOR_UP)
            elif df["Close"].iloc[i] >= df["Close"].iloc[i - 1]:
                colors.append(COLOR_UP)
            else:
                colors.append(COLOR_DOWN)

        fig.add_trace(
            go.Bar(
                x=x, y=df["Volume"],
                marker_color=colors,
                opacity=0.4,
                name="Volume",
            ),
            row=2, col=1,
        )

    # 레이아웃
    fig.update_layout(
        title=title,
        height=500,
        margin=dict(l=50, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=1.02, x=0),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    if has_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig
