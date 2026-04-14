import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { FONTS, FONT_SIZES, SPACING, RADIUS } from '../theme/tokens';

interface SearchResult {
  ticker: string;
  name: string;
}

export default function SearchAutocomplete() {
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [show, setShow] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setShow(false);
      return;
    }

    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(query.trim())}&limit=8`)
        .then((r) => r.json())
        .then((data) => {
          setResults(data.results ?? []);
          setShow(true);
          setActiveIndex(-1);
        })
        .catch(() => setResults([]));
    }, 200);

    return () => clearTimeout(timerRef.current);
  }, [query]);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShow(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const selectTicker = (ticker: string) => {
    navigate(`/quick-look/${ticker.toUpperCase()}`);
    setQuery('');
    setResults([]);
    setShow(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShow(false);
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => Math.min(prev + 1, results.length - 1));
      return;
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => Math.max(prev - 1, -1));
      return;
    }
    if (e.key === 'Enter') {
      if (activeIndex >= 0 && results[activeIndex]) {
        selectTicker(results[activeIndex].ticker);
      } else if (query.trim()) {
        selectTicker(query.trim());
      }
    }
  };

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <input
        type="text"
        placeholder="Search ticker..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => results.length > 0 && setShow(true)}
        style={{
          width: '100%',
          padding: `${SPACING.sm} ${SPACING.md}`,
          background: theme.bg_primary,
          color: theme.text_primary,
          border: `1px solid ${theme.border}`,
          borderRadius: RADIUS.button,
          fontSize: FONT_SIZES.sm,
          fontFamily: FONTS.body,
        }}
      />

      {/* Dropdown */}
      {show && results.length > 0 && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            marginTop: 4,
            background: theme.bg_card,
            border: `1px solid ${theme.border}`,
            borderRadius: RADIUS.card,
            boxShadow: '0 8px 24px rgba(0,0,0,0.3)',
            zIndex: 200,
            maxHeight: 320,
            overflowY: 'auto',
          }}
        >
          {results.map((r, i) => (
            <button
              key={r.ticker}
              onClick={() => selectTicker(r.ticker)}
              onMouseEnter={() => setActiveIndex(i)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: SPACING.sm,
                width: '100%',
                padding: `${SPACING.sm} ${SPACING.md}`,
                background: i === activeIndex ? theme.bg_card_hover : 'transparent',
                color: theme.text_primary,
                fontSize: FONT_SIZES.sm,
                borderBottom: i < results.length - 1 ? `1px solid ${theme.border}` : 'none',
                transition: 'background 0.1s',
              }}
            >
              <span
                style={{
                  fontWeight: 700,
                  fontFamily: FONTS.numeric,
                  color: theme.accent,
                  minWidth: 55,
                }}
              >
                {r.ticker}
              </span>
              <span
                style={{
                  color: theme.text_secondary,
                  fontSize: FONT_SIZES.xs,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {r.name}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
