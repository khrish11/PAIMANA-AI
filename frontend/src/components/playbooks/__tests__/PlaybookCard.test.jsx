import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PlaybookCard from '../PlaybookCard';

describe('PlaybookCard', () => {
  const mockPlaybook = {
    playbook_id: '123',
    suggestion_id: '456',
    category: 'land_acquisition',
    label: 'Weekly coordination with district administration',
    confidence_tier: 'HIGH',
    source_project_count: 8,
    created_at: '2026-03-15T10:00:00',
    evidence_actions: [
      {
        action_id: '1',
        action_text: 'Weekly direct coordination with district administration',
        category: 'land_acquisition',
        source_month: '2026-03-01',
        quote_evidence: 'Weekly coordination with district',
        specificity_score: 4,
      },
    ],
  };

  it('renders playbook card with correct information', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        triggerReason="Land acquisition delay is a key risk driver"
        isSuggestion={true}
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/Weekly coordination with district administration/i)).toBeInTheDocument();
    expect(screen.getByText(/HIGH/i)).toBeInTheDocument();
    expect(screen.getByText(/8 comparable projects/i)).toBeInTheDocument();
  });

  it('calls onDismiss when dismiss button is clicked', () => {
    const mockOnDismiss = vi.fn();
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        isSuggestion={true}
        onDismiss={mockOnDismiss}
        onViewed={vi.fn()}
      />
    );

    fireEvent.click(screen.getByText(/dismiss/i));
    expect(mockOnDismiss).toHaveBeenCalledWith('456');
  });

  it('calls onView when view button is clicked', () => {
    const mockOnViewed = vi.fn();
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        onDismiss={vi.fn()}
        onViewed={mockOnViewed}
      />
    );

    fireEvent.click(screen.getByText(/view evidence/i));
    expect(mockOnViewed).toHaveBeenCalledWith('456');
  });

  it('displays confidence tier with correct color', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/HIGH CONFIDENCE/i)).toBeInTheDocument();
  });

  it('shows trigger reason when suggestion is provided', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        triggerReason="Land acquisition delay is a key risk driver"
        isSuggestion={true}
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/Land acquisition delay is a key risk driver/)).toBeInTheDocument();
  });

  it('renders without suggestion', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/Weekly coordination with district administration/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        loading={true}
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows error state', () => {
    render(
      <PlaybookCard
        playbook={mockPlaybook}
        error="Failed to load playbook"
        onDismiss={vi.fn()}
        onViewed={vi.fn()}
      />
    );

    expect(screen.getByText(/Failed to load playbook/)).toBeInTheDocument();
  });
});
