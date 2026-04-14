import { useEffect, useRef, useState } from 'react';
import { createChart, type IChartApi, LineSeries, ColorType } from 'lightweight-charts';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import type { HistoryRecord } from '../types/api';

const LINE_COLORS = ['#00D4FF', '#F59E0B', '#10B981', '#EF4444', '#A78BFA'];

interface Props {
  tickers: string[];
}

export default function CompareChart({ tickers }: Props) {
  const { theme, mode } = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!containerRef.current || tickers.length < 2) return;

    // Clean up previous chart
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: theme.text_secondary,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: theme.border },
        horzLines: { color: theme.border },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: theme.border },
      timeScale: { borderColor: theme.border },
      width: containerRef.current.clientWidth,
      height: 300,
    });

    chartRef.current = chart;

    setLoading(true);

    Promise.all(
      tickers.map((t) =>
        fetch(`/api/history/${t}?period=1Y`)
          .then((r) => (r.ok ? r.json() : []))
          .then((records: HistoryRecord[]) => ({ ticker: t, records }))
      )
    ).then((results) => {
      results.forEach(({ ticker, records }, i) => {
        if (!records.length) return;
        const baseClose = records[0].Close;
        if (!baseClose) return;

        const normalized = records.map((r) => ({
          time: r.Date.split('T')[0] as string,
          value: (r.Close / baseClose) * 100,
        }));

        const series = chart.addSeries(LineSeries, {
          color: LINE_COLORS[i % LINE_COLORS.length],
          lineWidth: 2,
          title: ticker,
        });
        series.setData(normalized);
      });

      chart.timeScale().fitContent();
      setLoading(false);
    });

    const handleResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickers.join(','), mode]);

  if (tickers.length < 2) return null;

  return (
    <div
      style={{
        background: theme.bg_card,
        border: `1px solid ${theme.border}`,
        borderRadius: RADIUS.card,
        padding: SPACING.lg,
        marginBottom: SPACING.lg,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: SPACING.md }}>
        <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, fontWeight: 600, letterSpacing: '0.05em' }}>
          NORMALIZED RETURNS (Base 100, 1Y)
        </div>
        <div style={{ display: 'flex', gap: SPACING.md }}>
          {tickers.map((t, i) => (
            <span key={t} style={{ display: 'flex', alignItems: 'center', gap: SPACING.xs, fontSize: FONT_SIZES.xs }}>
              <span
                style={{
                  width: 12,
                  height: 3,
                  background: LINE_COLORS[i % LINE_COLORS.length],
                  display: 'inline-block',
                  borderRadius: 2,
                }}
              />
              <span style={{ color: theme.text_secondary, fontWeight: 600 }}>{t}</span>
            </span>
          ))}
        </div>
      </div>

      <div style={{ position: 'relative' }}>
        {loading && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: theme.text_muted,
              fontSize: FONT_SIZES.sm,
              zIndex: 10,
            }}
          >
            Loading chart...
          </div>
        )}
        <div ref={containerRef} />
      </div>
    </div>
  );
}
