/** API base URL — 개발 시 Vite proxy, 프로덕션 시 Render 백엔드 URL 사용 */
export const API_BASE = import.meta.env.VITE_API_BASE || '/api';

/** Google OAuth Client ID — Phase 14 무료체험 로그인 (frontend/.env의 VITE_GOOGLE_CLIENT_ID) */
export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
