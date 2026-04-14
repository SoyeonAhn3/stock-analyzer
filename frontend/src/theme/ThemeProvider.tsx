import { createContext, useContext, useState, type ReactNode } from 'react';
import { darkTheme } from './dark';
import { lightTheme } from './light';

/** 컬러 토큰 타입 — 모든 테마가 이 형태를 가짐 */
export interface ThemeColors {
  bg_primary: string;
  bg_card: string;
  bg_card_hover: string;
  border: string;
  text_primary: string;
  text_secondary: string;
  text_muted: string;
  accent: string;
  accent_hover: string;
  up: string;
  down: string;
  warning: string;
}

interface ThemeContextValue {
  theme: ThemeColors;
  mode: 'dark' | 'light';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<'dark' | 'light'>('dark');
  const theme = mode === 'dark' ? darkTheme : lightTheme;

  const toggleTheme = () => setMode((m) => (m === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, mode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/** 어디서든 테마에 접근: const { theme, mode, toggleTheme } = useTheme() */
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
