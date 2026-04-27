import { useEffect, useRef, useState } from 'react';
import { createChart, createSeriesMarkers, type IChartApi, type ISeriesApi, type ISeriesMarkersPluginApi, CandlestickSeries, HistogramSeries, LineSeries, ColorType } from 'lightweight-charts';
import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { API_BASE } from '../config';
import type { HistoryRecord } from '../types/api';

const PERIODS = ['1D', '1M', '3M', '6M', '1Y', '5Y'] as const;

export interface ChartMarker {
  time: string;
  position: 'aboveBar' | 'belowBar' | 'inBar';
  color: string;
  shape: 'arrowUp' | 'arrowDown' | 'circle' | 'square';
  text: string;
}

interface Props {
  ticker: string;
  markers?: ChartMarker[];
  initialPeriod?: string;
}

export default function Chart({ ticker, markers, initialPeriod }: Props) {
  const { theme, mode } = useTheme();
  const bp = useBreakpoint();
  const chartHeight = bp === 'mobile' ? 250 : bp === 'tablet' ? 320 : 400;
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const candleRef = useRef<ISeriesApi<any> | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const volumeRef = useRef<ISeriesApi<any> | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ma50Ref = useRef<ISeriesApi<any> | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ma200Ref = useRef<ISeriesApi<any> | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersRef = useRef<ISeriesMarkersPluginApi<any> | null>(null);
  const [period, setPeriod] = useState<string>(initialPeriod ?? '1Y');
  const [loading, setLoading] = useState(false);

  // Create chart on mount
  useEffect(() => {
    if (!containerRef.current) return;

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
      height: chartHeight,
    });

    const candle = chart.addSeries(CandlestickSeries, {
      upColor: theme.up,
      downColor: theme.down,
      borderUpColor: theme.up,
      borderDownColor: theme.down,
      wickUpColor: theme.up,
      wickDownColor: theme.down,
    });

    const volume = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });
    volume.priceScale().applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    const ma50 = chart.addSeries(LineSeries, { color: theme.accent, lineWidth: 2 });
    const ma200 = chart.addSeries(LineSeries, { color: theme.warning, lineWidth: 2 });

    chartRef.current = chart;
    candleRef.current = candle;
    volumeRef.current = volume;
    ma50Ref.current = ma50;
    ma200Ref.current = ma200;

    const handleResize = () => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth, height: chartHeight });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update theme colors
  useEffect(() => {
    if (!chartRef.current) return;
    chartRef.current.applyOptions({
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: theme.text_secondary,
      },
      grid: {
        vertLines: { color: theme.border },
        horzLines: { color: theme.border },
      },
    });
    candleRef.current?.applyOptions({
      upColor: theme.up,
      downColor: theme.down,
      borderUpColor: theme.up,
      borderDownColor: theme.down,
      wickUpColor: theme.up,
      wickDownColor: theme.down,
    });
    ma50Ref.current?.applyOptions({ color: theme.accent });
    ma200Ref.current?.applyOptions({ color: theme.warning });
  }, [mode, theme]);

  // Fetch data on ticker/period change
  useEffect(() => {
    if (!ticker) return;
    setLoading(true);

    fetch(`${API_BASE}/history/${ticker}?period=${period}`)
      .then((r) => (r.ok ? r.json() : []))
      .then((records: HistoryRecord[]) => {
        if (!records.length) return;

        const candles = records.map((r) => ({
          time: r.Date.split('T')[0] as string,
          open: r.Open,
          high: r.High,
          low: r.Low,
          close: r.Close,
        }));

        const volumes = records.map((r) => ({
          time: r.Date.split('T')[0] as string,
          value: r.Volume,
          color: r.Close >= r.Open ? theme.up + '40' : theme.down + '40',
        }));

        candleRef.current?.setData(candles);
        volumeRef.current?.setData(volumes);

        const ma50Data = records
          .filter((r) => r.MA50 != null)
          .map((r) => ({ time: r.Date.split('T')[0] as string, value: r.MA50! }));
        const ma200Data = records
          .filter((r) => r.MA200 != null)
          .map((r) => ({ time: r.Date.split('T')[0] as string, value: r.MA200! }));

        ma50Ref.current?.setData(ma50Data);
        ma200Ref.current?.setData(ma200Data);

        if (markers?.length && candleRef.current) {
          const validDates = new Set(candles.map((c) => c.time));
          const filtered = markers
            .filter((m) => validDates.has(m.time))
            .sort((a, b) => a.time.localeCompare(b.time));
          if (filtered.length) {
            if (markersRef.current) {
              markersRef.current.setMarkers(filtered);
            } else {
              markersRef.current = createSeriesMarkers(candleRef.current, filtered);
            }
          }
        }

        chartRef.current?.timeScale().fitContent();
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [ticker, period, theme.up, theme.down]);

  return (
    <div style={{ flex: 1 }}>
      {/* Period tabs */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: SPACING.xs, marginBottom: SPACING.md }}>
        {PERIODS.map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            style={{
              padding: `${SPACING.xs} ${SPACING.sm}`,
              borderRadius: RADIUS.button,
              fontSize: FONT_SIZES.xs,
              fontWeight: 600,
              background: period === p ? theme.accent : 'transparent',
              color: period === p ? '#FFFFFF' : theme.text_secondary,
              border: `1px solid ${period === p ? theme.accent : theme.border}`,
              transition: 'all 0.15s ease',
            }}
          >
            {p}
          </button>
        ))}
        <div style={{ marginLeft: bp === 'mobile' ? 0 : 'auto', display: 'flex', gap: SPACING.md, alignItems: 'center' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: SPACING.xs, fontSize: FONT_SIZES.xs }}>
            <span style={{ width: 16, height: 2, background: theme.accent, display: 'inline-block' }} />
            <span style={{ color: theme.text_muted }}>MA(50)</span>
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: SPACING.xs, fontSize: FONT_SIZES.xs }}>
            <span style={{ width: 16, height: 2, background: theme.warning, display: 'inline-block' }} />
            <span style={{ color: theme.text_muted }}>MA(200)</span>
          </span>
        </div>
      </div>

      {/* Chart container */}
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
