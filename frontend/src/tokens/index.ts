/**
 * PAIMANA-AI Design Tokens
 * Centralized design system based on modern analytics dashboard aesthetic
 */

export const colors = {
  // Backgrounds
  background: {
    primary: '#0f172a', // Dark slate - main background
    secondary: '#1e293b', // Lighter slate - card background
    tertiary: '#334155', // Border/separator
    elevated: '#1e293b', // Elevated surfaces
  },
  
  // Text
  text: {
    primary: '#f8fafc', // White-ish - primary text
    secondary: '#cbd5e1', // Light gray - secondary text
    muted: '#64748b', // Muted gray - labels/hints
    inverse: '#0f172a', // Dark text on light backgrounds
  },
  
  // Accents
  accent: {
    primary: '#3b82f6', // Blue - primary actions
    secondary: '#8b5cf6', // Purple - secondary actions
    success: '#10b981', // Green - success states
    warning: '#f59e0b', // Amber - warnings
    danger: '#ef4444', // Red - danger/critical
    critical: '#dc2626', // Darker red - critical risk
    info: '#06b6d4', // Cyan - informational
  },
  
  // Risk levels
  risk: {
    low: '#10b981', // Green
    medium: '#f59e0b', // Amber
    high: '#f97316', // Orange
    critical: '#ef4444', // Red
  },
  
  // Borders
  border: {
    default: '#334155',
    light: '#475569',
    focus: '#3b82f6',
  },
};

export const spacing = {
  xs: '0.25rem', // 4px
  sm: '0.5rem', // 8px
  md: '1rem', // 16px
  lg: '1.5rem', // 24px
  xl: '2rem', // 32px
  '2xl': '3rem', // 48px
  '3xl': '4rem', // 64px
};

export const borderRadius = {
  sm: '0.375rem', // 6px
  md: '0.5rem', // 8px
  lg: '0.75rem', // 12px
  xl: '1rem', // 16px
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

export const typography = {
  fontFamily: {
    sans: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'JetBrains Mono, "Fira Code", Consolas, Monaco, monospace',
  },
  fontSize: {
    xs: '0.75rem', // 12px
    sm: '0.875rem', // 14px
    base: '1rem', // 16px
    lg: '1.125rem', // 18px
    xl: '1.25rem', // 20px
    '2xl': '1.5rem', // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
};

export const chart = {
  colors: {
    primary: '#3b82f6',
    secondary: '#8b5cf6',
    tertiary: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
  },
  dimensions: {
    height: {
      sm: '200px',
      md: '300px',
      lg: '400px',
      xl: '500px',
    },
  },
};

export const transitions = {
  fast: '150ms ease-in-out',
  normal: '300ms ease-in-out',
  slow: '500ms ease-in-out',
};

export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
};

export const breakpoints = {
  sm: '640px', // Mobile
  md: '768px', // Tablet
  lg: '1024px', // Desktop
  xl: '1280px', // Large desktop
  '2xl': '1536px', // Extra large
};

export default {
  colors,
  spacing,
  borderRadius,
  shadows,
  typography,
  chart,
  transitions,
  zIndex,
  breakpoints,
};
