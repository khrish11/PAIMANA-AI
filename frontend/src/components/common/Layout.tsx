import React from 'react';
import { colors, spacing } from '../../tokens';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface LayoutProps {
  children: React.ReactNode;
  title: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: colors.background.primary,
        color: colors.text.primary,
      }}
    >
      <Sidebar />
      <TopBar title={title} />
      <main
        style={{
          marginLeft: '280px',
          marginTop: '64px',
          padding: spacing.xl,
        }}
      >
        {children}
      </main>
    </div>
  );
};
