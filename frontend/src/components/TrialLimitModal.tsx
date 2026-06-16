import { useTheme } from '../theme/ThemeProvider';
import { FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

/**
 * 무료체험 한도 도달 모달 — Phase 14.
 * 분석 요청이 HTTP 429(trial_limit_reached)를 받으면 표시. 단일 변형.
 * 기존 AlertModal 패턴(고정 오버레이 + 중앙 카드 + 외부 클릭 닫기) 준수.
 */

interface Props {
  onClose: () => void;
}

export default function TrialLimitModal({ onClose }: Props) {
  const { theme } = useTheme();

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 300,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: theme.bg_card,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.card,
          padding: SPACING.xl,
          width: 340,
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '32px', marginBottom: SPACING.md }}>🎯</div>
        <div style={{ color: theme.text_primary, fontSize: FONT_SIZES.lg, fontWeight: 700, marginBottom: SPACING.sm }}>
          Free Trial Limit Reached
        </div>
        <p style={{ color: theme.text_secondary, fontSize: FONT_SIZES.sm, lineHeight: 1.6, marginBottom: SPACING.lg }}>
          You've used all 3 free AI analyses. Premium plans are coming soon — thanks for trying QuantAI!
        </p>
        <button
          onClick={onClose}
          style={{
            width: '100%',
            padding: SPACING.md,
            background: theme.accent,
            color: '#FFFFFF',
            borderRadius: RADIUS.button,
            fontSize: FONT_SIZES.sm,
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Got it
        </button>
      </div>
    </div>
  );
}
