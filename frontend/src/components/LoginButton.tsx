import { GoogleLogin } from '@react-oauth/google';
import { useTheme } from '../theme/ThemeProvider';
import { useAuth } from '../auth/AuthProvider';

/**
 * Google 로그인 버튼 — Phase 14 무료체험.
 *
 * `@react-oauth/google`의 `<GoogleLogin>`은 ID 토큰(credential)을 직접 반환하며,
 * 이를 useAuth.login()으로 보관한다. 백엔드는 이 토큰을 verify_oauth2_token으로 검증.
 */

interface Props {
  size?: 'large' | 'medium' | 'small';
}

export default function LoginButton({ size = 'medium' }: Props) {
  const { mode } = useTheme();
  const { login } = useAuth();

  return (
    <GoogleLogin
      onSuccess={(cred) => {
        if (cred.credential) login(cred.credential);
      }}
      onError={() => {
        /* 사용자가 취소했거나 실패 — 별도 처리 없이 무시 */
      }}
      theme={mode === 'dark' ? 'filled_black' : 'outline'}
      size={size}
      shape="pill"
      text="signin_with"
    />
  );
}
