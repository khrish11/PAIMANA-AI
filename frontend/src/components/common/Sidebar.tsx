import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { colors, spacing, typography, borderRadius } from '../../tokens';

interface NavItem {
  label: string;
  path: string;
  icon?: string;
}

interface SidebarProps {
  className?: string;
}

const navItems: NavItem[] = [
  { label: 'Overview', path: '/', icon: '📊' },
  { label: 'Projects', path: '/projects', icon: '🏗️' },
  { label: 'Risk Intelligence', path: '/risk', icon: '⚠️' },
  { label: 'Governance', path: '/governance', icon: '🏛️' },
  { label: 'Network', path: '/network', icon: '🔗' },
  { label: 'Decision Cockpit', path: '/decision-cockpit', icon: '🎯' },
  { label: 'Agency', path: '/agency', icon: '🏢' },
  { label: 'Models', path: '/models', icon: '🤖' },
  { label: 'Data Management', path: '/data-management', icon: '📁' },
  { label: 'Reports', path: '/reports', icon: '📈' },
  { label: 'Data Health', path: '/data-health', icon: '💚' },
  { label: 'Audit', path: '/audit', icon: '📋' },
];

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <aside
      className={className}
      style={{
        width: '280px',
        height: '100vh',
        backgroundColor: colors.background.primary,
        borderRight: `1px solid ${colors.border.default}`,
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        left: 0,
        top: 0,
        padding: spacing.lg,
        zIndex: 1000,
      }}
    >
      {/* Logo */}
      <div
        style={{
          marginBottom: spacing.xl,
          paddingBottom: spacing.lg,
          borderBottom: `1px solid ${colors.border.default}`,
        }}
      >
        <h1
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.xl,
            fontWeight: typography.fontWeight.bold as number,
            color: colors.text.primary,
            margin: 0,
            letterSpacing: '-0.5px',
          }}
        >
          PAIMANA-AI
        </h1>
        <p
          style={{
            fontFamily: typography.fontFamily.sans,
            fontSize: typography.fontSize.xs,
            color: colors.text.muted,
            margin: `${spacing.xs} 0 0 0`,
          }}
        >
          Infrastructure Intelligence
        </p>
      </div>

      {/* Navigation */}
      <nav
        style={{
          flex: 1,
          overflowY: 'auto',
        }}
      >
        <ul
          style={{
            listStyle: 'none',
            padding: 0,
            margin: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing.xs,
          }}
        >
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path !== '/' && location.pathname.startsWith(item.path));
            
            return (
              <li key={item.path}>
                <button
                  onClick={() => navigate(item.path)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: `${spacing.sm} ${spacing.md}`,
                    backgroundColor: isActive ? colors.background.secondary : 'transparent',
                    color: isActive ? colors.text.primary : colors.text.secondary,
                    border: 'none',
                    borderRadius: borderRadius.md,
                    cursor: 'pointer',
                    fontFamily: typography.fontFamily.sans,
                    fontSize: typography.fontSize.sm,
                    fontWeight: isActive ? (typography.fontWeight.semibold as number) : (typography.fontWeight.normal as number),
                    display: 'flex',
                    alignItems: 'center',
                    gap: spacing.md,
                    transition: 'background-color 0.2s ease, color 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = colors.background.tertiary;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  {item.icon && (
                    <span style={{ fontSize: typography.fontSize.base }}>{item.icon}</span>
                  )}
                  {item.label}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Section */}
      <div
        style={{
          paddingTop: spacing.lg,
          borderTop: `1px solid ${colors.border.default}`,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.md,
          }}
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: borderRadius.full,
              backgroundColor: colors.accent.primary,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: colors.text.primary,
              fontWeight: typography.fontWeight.bold as number,
              fontSize: typography.fontSize.sm,
            }}
          >
            U
          </div>
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.sm,
                fontWeight: typography.fontWeight.medium as number,
                color: colors.text.primary,
              }}
            >
              User
            </div>
            <div
              style={{
                fontFamily: typography.fontFamily.sans,
                fontSize: typography.fontSize.xs,
                color: colors.text.muted,
              }}
            >
              Analyst
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
