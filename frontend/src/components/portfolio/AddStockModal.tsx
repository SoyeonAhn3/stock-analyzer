import { useState, useEffect, useRef, useCallback } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';
import { validateTicker } from '../../services/portfolioApi';
import type { Holding } from '../../services/portfolioApi';

interface Props {
  editing: Holding | null;
  onSave: (data: Omit<Holding, 'id' | 'created_at'>) => void;
  onUpdate: (id: string, updates: Partial<Holding>) => void;
  onClose: () => void;
}

export default function AddStockModal({ editing, onSave, onUpdate, onClose }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const [ticker, setTicker] = useState('');
  const [shares, setShares] = useState('');
  const [avgCost, setAvgCost] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [purchaseDate, setPurchaseDate] = useState('');
  const [memo, setMemo] = useState('');

  const [tickerValid, setTickerValid] = useState<boolean | null>(null);
  const [tickerName, setTickerName] = useState('');
  const [tickerChecking, setTickerChecking] = useState(false);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (editing) {
      setTicker(editing.ticker);
      setShares(String(editing.shares));
      setAvgCost(String(editing.avg_cost));
      setCurrency(editing.currency);
      setPurchaseDate(editing.purchase_date ?? '');
      setMemo(editing.memo ?? '');
      setTickerValid(true);
      setTickerName('');
    }
  }, [editing]);

  const checkTicker = useCallback((value: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const upper = value.toUpperCase().trim();
    if (!upper) {
      setTickerValid(null);
      setTickerName('');
      return;
    }

    setTickerChecking(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const result = await validateTicker(upper);
        setTickerValid(result.valid);
        setTickerName(result.valid && result.name ? result.name : '');
      } catch {
        setTickerValid(null);
        setTickerName('');
      } finally {
        setTickerChecking(false);
      }
    }, 500);
  }, []);

  const handleTickerChange = (value: string) => {
    const upper = value.toUpperCase();
    setTicker(upper);
    if (!editing) checkTicker(upper);
  };

  const sharesNum = parseInt(shares, 10);
  const costNum = parseFloat(avgCost);
  const canSave =
    ticker.trim().length > 0 &&
    tickerValid !== false &&
    !isNaN(sharesNum) && sharesNum > 0 &&
    !isNaN(costNum) && costNum > 0;

  const handleSubmit = () => {
    if (!canSave) return;

    if (editing) {
      onUpdate(editing.id, {
        shares: sharesNum,
        avg_cost: costNum,
        currency,
        purchase_date: purchaseDate || null,
        memo: memo || '',
      });
    } else {
      onSave({
        ticker: ticker.trim().toUpperCase(),
        shares: sharesNum,
        avg_cost: costNum,
        currency,
        purchase_date: purchaseDate || null,
        memo: memo || '',
      });
    }
    onClose();
  };

  const overlay: React.CSSProperties = {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.6)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: SPACING.md,
  };

  const modal: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    width: '100%',
    maxWidth: isMobile ? '100%' : 480,
    maxHeight: '90vh',
    overflowY: 'auto',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    marginBottom: SPACING.xs,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: `${SPACING.sm} ${SPACING.md}`,
    fontSize: FONT_SIZES.md,
    fontFamily: FONTS.numeric,
    color: theme.text_primary,
    background: theme.bg_primary,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.button,
    outline: 'none',
    boxSizing: 'border-box',
  };

  return (
    <div style={overlay} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>
        {/* 헤더 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.lg }}>
          <span style={{ color: theme.text_primary, fontSize: FONT_SIZES.xl, fontWeight: 700 }}>
            {editing ? 'Edit Stock' : 'Add Stock'}
          </span>
          <button
            onClick={onClose}
            style={{ color: theme.text_muted, fontSize: '20px', background: 'none', border: 'none', cursor: 'pointer', padding: SPACING.xs }}
          >
            ✕
          </button>
        </div>

        {/* Ticker */}
        <div style={{ marginBottom: SPACING.md }}>
          <label style={labelStyle}>Ticker *</label>
          <div style={{ position: 'relative' }}>
            <input
              style={{
                ...inputStyle,
                borderColor: tickerValid === false ? theme.down : tickerValid === true ? theme.up : theme.border,
              }}
              value={ticker}
              onChange={(e) => handleTickerChange(e.target.value)}
              placeholder="e.g. AAPL"
              disabled={!!editing}
              maxLength={10}
            />
            {tickerChecking && (
              <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: theme.text_muted, fontSize: FONT_SIZES.xs }}>
                ...
              </span>
            )}
            {!tickerChecking && tickerValid === true && !editing && (
              <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: theme.up, fontSize: FONT_SIZES.md }}>
                ✓
              </span>
            )}
            {!tickerChecking && tickerValid === false && (
              <span style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', color: theme.down, fontSize: FONT_SIZES.md }}>
                ✗
              </span>
            )}
          </div>
          {tickerName && (
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.xs, marginTop: SPACING.xs }}>
              {tickerName}
            </div>
          )}
          {tickerValid === false && (
            <div style={{ color: theme.down, fontSize: FONT_SIZES.xs, marginTop: SPACING.xs }}>
              유효하지 않은 티커입니다.
            </div>
          )}
        </div>

        {/* Shares + Avg Cost (가로 배치) */}
        <div style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.md }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Shares *</label>
            <input
              style={inputStyle}
              type="number"
              min="1"
              step="1"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              placeholder="0"
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Avg Cost *</label>
            <input
              style={inputStyle}
              type="number"
              min="0.01"
              step="0.01"
              value={avgCost}
              onChange={(e) => setAvgCost(e.target.value)}
              placeholder="$ 0.00"
            />
          </div>
        </div>

        {/* Currency + Purchase Date (가로 배치) */}
        <div style={{ display: 'flex', gap: SPACING.md, marginBottom: SPACING.md }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Currency</label>
            <select
              style={{ ...inputStyle, cursor: 'pointer' }}
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="KRW">KRW</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Purchase Date</label>
            <input
              style={inputStyle}
              type="date"
              value={purchaseDate}
              onChange={(e) => setPurchaseDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        {/* Memo */}
        <div style={{ marginBottom: SPACING.lg }}>
          <label style={labelStyle}>Memo (optional)</label>
          <input
            style={inputStyle}
            value={memo}
            onChange={(e) => setMemo(e.target.value.slice(0, 100))}
            placeholder="e.g. 실적 발표 전 매수"
            maxLength={100}
          />
          <div style={{ textAlign: 'right', color: theme.text_muted, fontSize: FONT_SIZES.xs, marginTop: '2px' }}>
            {memo.length}/100
          </div>
        </div>

        {/* 저장 버튼 */}
        <button
          onClick={handleSubmit}
          disabled={!canSave}
          style={{
            width: '100%',
            padding: SPACING.sm,
            fontSize: FONT_SIZES.md,
            fontWeight: 600,
            color: canSave ? theme.bg_primary : theme.text_muted,
            background: canSave ? theme.accent : theme.border,
            border: 'none',
            borderRadius: RADIUS.button,
            cursor: canSave ? 'pointer' : 'not-allowed',
          }}
        >
          {editing ? 'Update' : 'Save'}
        </button>
      </div>
    </div>
  );
}
