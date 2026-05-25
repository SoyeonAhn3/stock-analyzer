import { useState } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../../theme/tokens';
import { useBreakpoint } from '../../hooks/useBreakpoint';
import { createSync, connectSync, saveSession, saveRememberedCode, loadRememberedCode } from '../../services/syncApi';

interface Props {
  onLogin: (code: string, pin: string) => void;
}

type View = 'login' | 'register' | 'issued';

export default function PortfolioLoginGate({ onLogin }: Props) {
  const { theme } = useTheme();
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  const [view, setView] = useState<View>('login');
  const [code, setCode] = useState(loadRememberedCode() ?? '');
  const [pin, setPin] = useState('');
  const [pinConfirm, setPinConfirm] = useState('');
  const [remember, setRemember] = useState(!!loadRememberedCode());
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [issuedCode, setIssuedCode] = useState('');
  const [copied, setCopied] = useState(false);

  const formatCode = (val: string) => {
    const clean = val.replace(/[^A-Z0-9]/gi, '').toUpperCase().slice(0, 12);
    const parts = [clean.slice(0, 4), clean.slice(4, 8), clean.slice(8, 12)].filter(Boolean);
    return parts.join('-');
  };

  const handleLogin = async () => {
    if (code.length !== 14 || pin.length !== 4) return;
    setLoading(true);
    setError(null);
    try {
      await connectSync(code, pin);
      saveSession(code, pin);
      if (remember) saveRememberedCode(code);
      onLogin(code, pin);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (pin.length !== 4) {
      setError('PIN must be 4 digits');
      return;
    }
    if (pin !== pinConfirm) {
      setError('PINs do not match');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await createSync(pin);
      setIssuedCode(result.code);
      saveSession(result.code, pin);
      saveRememberedCode(result.code);
      setView('issued');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Creation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(issuedCode).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleStartPortfolio = () => {
    onLogin(issuedCode, pin);
  };

  const goToRegister = () => {
    setView('register');
    setPin('');
    setPinConfirm('');
    setError(null);
  };

  const goToLogin = () => {
    setView('login');
    setPin('');
    setError(null);
  };

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: isMobile ? SPACING.lg : SPACING['2xl'],
    width: '100%',
    maxWidth: 420,
    margin: '0 auto',
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
    letterSpacing: '2px',
    textAlign: 'center' as const,
  };

  const btnPrimary: React.CSSProperties = {
    width: '100%',
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: FONT_SIZES.md,
    fontWeight: 600,
    color: theme.bg_primary,
    background: theme.accent,
    border: 'none',
    borderRadius: RADIUS.button,
    cursor: loading ? 'default' : 'pointer',
    opacity: loading ? 0.5 : 1,
  };

  const btnOutline: React.CSSProperties = {
    width: '100%',
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: FONT_SIZES.md,
    fontWeight: 600,
    color: theme.text_secondary,
    background: 'transparent',
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.button,
    cursor: 'pointer',
  };

  const labelStyle: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    marginBottom: SPACING.xs,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', paddingTop: SPACING['2xl'] }}>
      <h1
        style={{
          color: theme.text_primary,
          fontSize: FONT_SIZES['2xl'],
          fontWeight: 700,
          marginBottom: SPACING.xl,
          textAlign: 'center',
        }}
      >
        Portfolio
      </h1>

      {/* ── Login View ── */}
      {view === 'login' && (
        <div style={cardStyle}>
          <div
            style={{
              color: theme.text_primary,
              fontSize: FONT_SIZES.lg,
              fontWeight: 600,
              textAlign: 'center',
              marginBottom: SPACING.lg,
            }}
          >
            My Portfolio
          </div>

          {error && (
            <div
              style={{
                padding: SPACING.sm,
                marginBottom: SPACING.md,
                borderRadius: RADIUS.button,
                fontSize: FONT_SIZES.sm,
                color: theme.down,
                background: `${theme.down}15`,
                textAlign: 'center',
              }}
            >
              {error}
            </div>
          )}

          <div style={{ marginBottom: SPACING.md }}>
            <div style={labelStyle}>CODE</div>
            <input
              style={inputStyle}
              maxLength={14}
              placeholder="ABCD-1234-EFGH"
              value={code}
              onChange={(e) => setCode(formatCode(e.target.value))}
            />
          </div>

          <div style={{ marginBottom: SPACING.md }}>
            <div style={labelStyle}>PIN</div>
            <input
              style={inputStyle}
              type="password"
              inputMode="numeric"
              maxLength={4}
              placeholder="••••"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            />
          </div>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: SPACING.sm,
              marginBottom: SPACING.lg,
              cursor: 'pointer',
              color: theme.text_secondary,
              fontSize: FONT_SIZES.sm,
            }}
          >
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              style={{ accentColor: theme.accent }}
            />
            Remember on this browser
          </label>

          <button
            onClick={handleLogin}
            disabled={loading || code.length !== 14 || pin.length !== 4}
            style={{
              ...btnPrimary,
              opacity: loading || code.length !== 14 || pin.length !== 4 ? 0.5 : 1,
              marginBottom: SPACING.lg,
            }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

          <div style={{ textAlign: 'center', color: theme.text_muted, fontSize: FONT_SIZES.sm }}>
            Don't have a code?{' '}
            <span
              onClick={goToRegister}
              style={{ color: theme.accent, cursor: 'pointer', fontWeight: 600 }}
            >
              Get a Code
            </span>
          </div>
        </div>
      )}

      {/* ── Register View ── */}
      {view === 'register' && (
        <div style={cardStyle}>
          <div
            style={{
              color: theme.text_primary,
              fontSize: FONT_SIZES.lg,
              fontWeight: 600,
              textAlign: 'center',
              marginBottom: SPACING.sm,
            }}
          >
            Create New Portfolio
          </div>
          <div
            style={{
              color: theme.text_muted,
              fontSize: FONT_SIZES.sm,
              textAlign: 'center',
              marginBottom: SPACING.lg,
              lineHeight: 1.5,
            }}
          >
            Set a 4-digit PIN.<br />
            This PIN cannot be changed, please remember it.
          </div>

          {error && (
            <div
              style={{
                padding: SPACING.sm,
                marginBottom: SPACING.md,
                borderRadius: RADIUS.button,
                fontSize: FONT_SIZES.sm,
                color: theme.down,
                background: `${theme.down}15`,
                textAlign: 'center',
              }}
            >
              {error}
            </div>
          )}

          <div style={{ marginBottom: SPACING.md }}>
            <div style={labelStyle}>SET PIN</div>
            <input
              style={inputStyle}
              type="password"
              inputMode="numeric"
              maxLength={4}
              placeholder="••••"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
            />
          </div>

          <div style={{ marginBottom: SPACING.lg }}>
            <div style={labelStyle}>CONFIRM PIN</div>
            <input
              style={{
                ...inputStyle,
                borderColor: pinConfirm.length === 4 && pin !== pinConfirm ? theme.down : theme.border,
              }}
              type="password"
              inputMode="numeric"
              maxLength={4}
              placeholder="••••"
              value={pinConfirm}
              onChange={(e) => setPinConfirm(e.target.value.replace(/\D/g, '').slice(0, 4))}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            />
            {pinConfirm.length === 4 && pin !== pinConfirm && (
              <div style={{ color: theme.down, fontSize: FONT_SIZES.xs, marginTop: SPACING.xs }}>
                PINs do not match
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: SPACING.sm }}>
            <button
              onClick={handleCreate}
              disabled={loading || pin.length !== 4 || pin !== pinConfirm}
              style={{
                ...btnPrimary,
                opacity: loading || pin.length !== 4 || pin !== pinConfirm ? 0.5 : 1,
              }}
            >
              {loading ? 'Creating...' : 'Create'}
            </button>
            <button onClick={goToLogin} style={btnOutline}>
              Back
            </button>
          </div>
        </div>
      )}

      {/* ── Issued View ── */}
      {view === 'issued' && (
        <div style={cardStyle}>
          <div
            style={{
              color: theme.up,
              fontSize: FONT_SIZES.lg,
              fontWeight: 600,
              textAlign: 'center',
              marginBottom: SPACING.lg,
            }}
          >
            Portfolio Created!
          </div>

          <div style={{ marginBottom: SPACING.md }}>
            <div style={labelStyle}>YOUR UNIQUE CODE</div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: SPACING.sm,
                padding: SPACING.md,
                background: theme.bg_primary,
                border: `1px solid ${theme.border}`,
                borderRadius: RADIUS.button,
              }}
            >
              <span
                style={{
                  fontSize: FONT_SIZES.xl,
                  fontFamily: FONTS.numeric,
                  fontWeight: 700,
                  color: theme.text_primary,
                  letterSpacing: '2px',
                }}
              >
                {issuedCode}
              </span>
              <button
                onClick={handleCopy}
                style={{
                  padding: `${SPACING.xs} ${SPACING.sm}`,
                  fontSize: FONT_SIZES.xs,
                  fontWeight: 600,
                  color: copied ? theme.up : theme.accent,
                  background: 'transparent',
                  border: `1px solid ${copied ? theme.up : theme.accent}`,
                  borderRadius: RADIUS.badge,
                  cursor: 'pointer',
                }}
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>

          <div
            style={{
              color: theme.warning,
              fontSize: FONT_SIZES.sm,
              textAlign: 'center',
              marginBottom: SPACING.lg,
              lineHeight: 1.5,
            }}
          >
            Save this code! You cannot access your portfolio without it.
          </div>

          <button onClick={handleStartPortfolio} style={btnPrimary}>
            Start Portfolio
          </button>
        </div>
      )}
    </div>
  );
}
