import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PlaybookEvidence from '../PlaybookEvidence';

describe('PlaybookEvidence', () => {
  const mockActions = [
    {
      action_id: '1',
      action_text: 'Weekly direct coordination with district administration',
      category: 'land_acquisition',
      source_month: '2026-03-01',
      quote_evidence: 'Weekly coordination with district',
      specificity_score: 4,
    },
    {
      action_id: '2',
      action_text: 'Regular meetings with district collector',
      category: 'land_acquisition',
      source_month: '2026-02-01',
      quote_evidence: 'Regular meetings with district collector',
      specificity_score: 5,
    },
  ];

  it('renders evidence actions', () => {
    render(<PlaybookEvidence actions={mockActions} />);

    expect(screen.getByText('Weekly direct coordination with district administration')).toBeInTheDocument();
    expect(screen.getByText('Regular meetings with district collector')).toBeInTheDocument();
  });

  it('displays quote evidence', () => {
    render(<PlaybookEvidence actions={mockActions} />);

    // Quote evidence appears in action title and quoted section
    expect(screen.getAllByText(/Weekly coordination with district/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Regular meetings with district collector/i).length).toBeGreaterThan(0);
  });

  it('shows source month', () => {
    render(<PlaybookEvidence actions={mockActions} />);

    expect(screen.getByText('2026-03-01')).toBeInTheDocument();
    expect(screen.getByText('2026-02-01')).toBeInTheDocument();
  });

  it('shows specificity score', () => {
    render(<PlaybookEvidence actions={mockActions} />);

    expect(screen.getAllByText(/Specificity:/)).toHaveLength(2);
  });

  it('expands and collapses on click', () => {
    render(<PlaybookEvidence actions={mockActions} />);

    const action = screen.getByText('Weekly direct coordination with district administration');
    fireEvent.click(action);

    // After clicking, evidence should be visible
    expect(screen.getByText(/Weekly coordination with district/i)).toBeInTheDocument();
  });

  it('renders empty state when no actions', () => {
    render(<PlaybookEvidence actions={[]} />);

    expect(screen.getByText(/no evidence/i)).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(<PlaybookEvidence actions={[]} loading={true} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
