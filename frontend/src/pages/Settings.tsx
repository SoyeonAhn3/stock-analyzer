import { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';
import { loadHoldings, saveHoldings } from '../services/portfolioApi';
import {
  loadSyncState,
  saveSyncState,
  createSync,
  connectSync,
  pushSync,
  pullSync,
  disconnectSync,
} from '../services/syncApi';
import type { SyncState } from '../services/syncApi';

type SyncView = 'idle' | 'create' | 'connect';

export default function Settings() {
  const { theme, mode, toggleTheme } = useTheme();

  const [syncState, setSyncState] = useState<SyncState | null>(loadSyncState);
  const [syncView, setSyncView] = useState<SyncView>('idle');
  const [pin, setPin] = useState('');
  const [code, setCode] = useState('');
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncMsg, setSyncMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  useEffect(() => {
    saveSyncState(syncState);
  }, [syncState]);

  const clearForm = useCallback(() => {
    setPin('');
    setCode('');
    setSyncView('idle');
  }, []);

  const handleCreate = async () => {
    if (pin.length !== 4) return;
    setSyncLoading(true);
    setSyncMsg(null);
    try {
      const { code: newCode } = await createSync(pin);
      const holdings = loadHoldings();
      await pushSync(newCode, pin, JSON.stringify(holdings));
      const now = new Date().toISOString();
      setSyncState({ code: newCode, pin, last_synced: now });
      setSyncMsg({ type: 'ok', text: `동기화 코드가 생성되었습니다: ${newCode}` });
      clearForm();
    } catch (e) {
      setSyncMsg({ type: 'err', text: e instanceof Error ? e.message : '생성 실패' });
    } finally {
      setSyncLoading(false);
    }
  };

  const handleConnect = async () => {
    if (code.length !== 14 || pin.length !== 4) return;
    setSyncLoading(true);
    setSyncMsg(null);
    try {
      await connectSync(code, pin);
      const result = await pullSync(code, pin);
      const holdings = JSON.parse(result.data);
      saveHoldings(holdings);
      setSyncState({ code, pin, last_synced: result.updated_at });
      setSyncMsg({ type: 'ok', text: '연결 완료! 포트폴리오 데이터를 불러왔습니다.' });
      clearForm();
    } catch (e) {
      setSyncMsg({ type: 'err', text: e instanceof Error ? e.message : '연결 실패' });
    } finally {
      setSyncLoading(false);
    }
  };

  const handlePush = async () => {
    if (!syncState) return;
    setSyncLoading(true);
    setSyncMsg(null);
    try {
      const holdings = loadHoldings();
      const result = await pushSync(syncState.code, syncState.pin, JSON.stringify(holdings));
      setSyncState((prev) => prev ? { ...prev, last_synced: result.updated_at } : prev);
      setSyncMsg({ type: 'ok', text: '서버에 동기화 완료!' });
    } catch (e) {
      setSyncMsg({ type: 'err', text: e instanceof Error ? e.message : '동기화 실패' });
    } finally {
      setSyncLoading(false);
    }
  };

  const handlePull = async () => {
    if (!syncState) return;
    setSyncLoading(true);
    setSyncMsg(null);
    try {
      const result = await pullSync(syncState.code, syncState.pin);
      const holdings = JSON.parse(result.data);
      saveHoldings(holdings);
      setSyncState((prev) => prev ? { ...prev, last_synced: result.updated_at } : prev);
      setSyncMsg({ type: 'ok', text: '서버에서 데이터를 불러왔습니다!' });
    } catch (e) {
      setSyncMsg({ type: 'err', text: e instanceof Error ? e.message : '불러오기 실패' });
    } finally {
      setSyncLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!syncState) return;
    setSyncLoading(true);
    setSyncMsg(null);
    try {
      await disconnectSync(syncState.code, syncState.pin);
      setSyncState(null);
      setSyncMsg({ type: 'ok', text: '동기화가 해제되었습니다.' });
    } catch (e) {
      setSyncMsg({ type: 'err', text: e instanceof Error ? e.message : '해제 실패' });
    } finally {
      setSyncLoading(false);
    }
  };

  const sectionLabel: React.CSSProperties = {
    color: theme.text_muted,
    fontSize: FONT_SIZES.xs,
    fontWeight: 600,
    letterSpacing: '0.05em',
    marginBottom: SPACING.md,
  };

  const cardStyle: React.CSSProperties = {
    background: theme.bg_card,
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.card,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  };

  const inputStyle: React.CSSProperties = {
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
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: FONT_SIZES.sm,
    fontWeight: 600,
    color: theme.bg_primary,
    background: theme.accent,
    border: 'none',
    borderRadius: RADIUS.button,
    cursor: 'pointer',
    opacity: syncLoading ? 0.5 : 1,
  };

  const btnOutline: React.CSSProperties = {
    padding: `${SPACING.sm} ${SPACING.lg}`,
    fontSize: FONT_SIZES.sm,
    fontWeight: 600,
    color: theme.text_secondary,
    background: 'transparent',
    border: `1px solid ${theme.border}`,
    borderRadius: RADIUS.button,
    cursor: 'pointer',
    opacity: syncLoading ? 0.5 : 1,
  };

  const formatCode = (val: string) => {
    const clean = val.replace(/[^A-Z0-9]/gi, '').toUpperCase().slice(0, 12);
    const parts = [clean.slice(0, 4), clean.slice(4, 8), clean.slice(8, 12)].filter(Boolean);
    return parts.join('-');
  };

  return (
    <div style={{ padding: SPACING.lg }}>
      <h1 style={{ color: theme.text_primary, fontSize: FONT_SIZES['2xl'], marginBottom: SPACING.xl }}>
        Settings
      </h1>

      {/* Theme Toggle */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
          marginBottom: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          THEME
        </div>
        <div style={{ display: 'flex', gap: SPACING.sm }}>
          {(['dark', 'light'] as const).map((m) => (
            <button
              key={m}
              onClick={mode !== m ? toggleTheme : undefined}
              style={{
                padding: `${SPACING.sm} ${SPACING.lg}`,
                borderRadius: RADIUS.button,
                fontSize: FONT_SIZES.sm,
                fontWeight: 600,
                background: mode === m ? theme.accent : 'transparent',
                color: mode === m ? '#FFFFFF' : theme.text_secondary,
                border: `1px solid ${mode === m ? theme.accent : theme.border}`,
                transition: 'all 0.15s ease',
              }}
            >
              {m === 'dark' ? 'Dark' : 'Light'}
            </button>
          ))}
        </div>
      </div>

      {/* AI Usage */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
          marginBottom: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          AI USAGE
        </div>
        <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg }}>
          <span className="numeric">0</span> / <span className="numeric">100</span> today
        </div>
        <div
          style={{
            height: '6px',
            background: theme.border,
            borderRadius: RADIUS.pill,
            marginTop: SPACING.sm,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: '0%',
              height: '100%',
              background: theme.accent,
              borderRadius: RADIUS.pill,
            }}
          />
        </div>
      </div>

      {/* Portfolio Sync */}
      <div style={cardStyle}>
        <div style={sectionLabel}>PORTFOLIO SYNC</div>

        {syncMsg && (
          <div
            style={{
              padding: SPACING.sm,
              marginBottom: SPACING.md,
              borderRadius: RADIUS.button,
              fontSize: FONT_SIZES.sm,
              color: syncMsg.type === 'ok' ? theme.up : theme.down,
              background: syncMsg.type === 'ok' ? `${theme.up}15` : `${theme.down}15`,
            }}
          >
            {syncMsg.text}
          </div>
        )}

        {syncState ? (
          <>
            <div style={{ marginBottom: SPACING.md }}>
              <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.xs }}>
                SYNC CODE
              </div>
              <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg, fontFamily: FONTS.numeric, letterSpacing: '2px' }}>
                {syncState.code}
              </div>
            </div>
            <div style={{ color: theme.text_muted, fontSize: FONT_SIZES.xs, marginBottom: SPACING.md }}>
              {syncState.last_synced
                ? `Last synced: ${new Date(syncState.last_synced).toLocaleString()}`
                : 'Not synced yet'}
            </div>
            <div style={{ display: 'flex', gap: SPACING.sm, flexWrap: 'wrap' }}>
              <button onClick={handlePush} disabled={syncLoading} style={btnPrimary}>
                {syncLoading ? '...' : 'Push'}
              </button>
              <button onClick={handlePull} disabled={syncLoading} style={btnOutline}>
                {syncLoading ? '...' : 'Pull'}
              </button>
              <button
                onClick={handleDisconnect}
                disabled={syncLoading}
                style={{ ...btnOutline, color: theme.down, borderColor: theme.down }}
              >
                Disconnect
              </button>
            </div>
          </>
        ) : syncView === 'create' ? (
          <>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginBottom: SPACING.md }}>
              4자리 PIN을 설정하세요. 다른 기기에서 이 PIN으로 데이터에 접근합니다.
            </div>
            <div style={{ display: 'flex', gap: SPACING.sm, alignItems: 'center', marginBottom: SPACING.md }}>
              <input
                style={{ ...inputStyle, width: 120 }}
                type="password"
                inputMode="numeric"
                maxLength={4}
                placeholder="PIN"
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
              />
              <button onClick={handleCreate} disabled={syncLoading || pin.length !== 4} style={{ ...btnPrimary, opacity: syncLoading || pin.length !== 4 ? 0.5 : 1 }}>
                {syncLoading ? 'Creating...' : 'Create'}
              </button>
              <button onClick={clearForm} style={btnOutline}>Cancel</button>
            </div>
          </>
        ) : syncView === 'connect' ? (
          <>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginBottom: SPACING.md }}>
              다른 기기에서 생성한 동기화 코드와 PIN을 입력하세요.
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: SPACING.sm, marginBottom: SPACING.md }}>
              <input
                style={{ ...inputStyle, width: 220 }}
                maxLength={14}
                placeholder="ABCD-1234-EFGH"
                value={code}
                onChange={(e) => setCode(formatCode(e.target.value))}
              />
              <div style={{ display: 'flex', gap: SPACING.sm, alignItems: 'center' }}>
                <input
                  style={{ ...inputStyle, width: 120 }}
                  type="password"
                  inputMode="numeric"
                  maxLength={4}
                  placeholder="PIN"
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                />
                <button
                  onClick={handleConnect}
                  disabled={syncLoading || code.length !== 14 || pin.length !== 4}
                  style={{ ...btnPrimary, opacity: syncLoading || code.length !== 14 || pin.length !== 4 ? 0.5 : 1 }}
                >
                  {syncLoading ? 'Connecting...' : 'Connect'}
                </button>
                <button onClick={clearForm} style={btnOutline}>Cancel</button>
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, marginBottom: SPACING.md }}>
              다른 기기와 포트폴리오 데이터를 동기화합니다. 회원가입 없이 코드+PIN으로 연결합니다.
            </div>
            <div style={{ display: 'flex', gap: SPACING.sm }}>
              <button onClick={() => setSyncView('create')} style={btnPrimary}>
                Create Sync Code
              </button>
              <button onClick={() => setSyncView('connect')} style={btnOutline}>
                Enter Existing Code
              </button>
            </div>
          </>
        )}
      </div>

      {/* Disclaimer */}
      <div
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.lg,
        }}
      >
        <div
          style={{
            color: theme.text_muted,
            fontSize: FONT_SIZES.xs,
            fontWeight: 600,
            letterSpacing: '0.05em',
            marginBottom: SPACING.md,
          }}
        >
          DISCLAIMER
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6 }}>
          AI-generated reference only. Not financial advice. All data is provided
          for informational purposes. Do your own research before making any
          investment decisions. Past performance does not guarantee future results.
        </p>
      </div>
    </div>
  );
}
