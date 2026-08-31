import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PlaybookLibrary from '../PlaybookLibrary';

describe('PlaybookLibrary', () => {
  const mockPlaybooks = [
    {
      playbook_id: '1',
      category: 'land_acquisition',
      label: 'Weekly coordination with district administration',
      confidence_tier: 'HIGH',
      source_project_count: 8,
      created_at: '2026-03-15T10:00:00',
    },
    {
      playbook_id: '2',
      category: 'contractor_management',
      label: 'Regular contractor performance reviews',
      confidence_tier: 'MEDIUM',
      source_project_count: 5,
      created_at: '2026-03-15T10:00:00',
    },
  ];

  it('renders playbook library with playbooks', () => {
    render(
      <PlaybookLibrary 
        playbooks={mockPlaybooks}
        loading={false}
        error={null}
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Weekly coordination with district administration/i)).toBeInTheDocument();
    expect(screen.getByText(/Regular contractor performance reviews/i)).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(
      <PlaybookLibrary 
        playbooks={[]}
        loading={true}
        error={null}
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders error state', () => {
    render(
      <PlaybookLibrary 
        playbooks={[]}
        loading={false}
        error="Failed to load playbooks"
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Failed to load playbooks/)).toBeInTheDocument();
  });

  it('renders empty state when no playbooks', () => {
    render(
      <PlaybookLibrary 
        playbooks={[]}
        loading={false}
        error={null}
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText(/no playbooks/i)).toBeInTheDocument();
  });

  it('calls onFilterChange when category filter is changed', () => {
    const mockOnFilterChange = vi.fn();
    render(
      <PlaybookLibrary 
        playbooks={mockPlaybooks}
        loading={false}
        error={null}
        onFilterChange={mockOnFilterChange}
      />
    );

    const categoryFilter = screen.getByLabelText(/category/i);
    fireEvent.change(categoryFilter, { target: { value: 'land_acquisition' } });

    expect(mockOnFilterChange).toHaveBeenCalled();
  });

  it('calls onFilterChange when confidence filter is changed', () => {
    const mockOnFilterChange = vi.fn();
    render(
      <PlaybookLibrary 
        playbooks={mockPlaybooks}
        loading={false}
        error={null}
        onFilterChange={mockOnFilterChange}
      />
    );

    const confidenceFilter = screen.getByLabelText(/confidence/i);
    fireEvent.change(confidenceFilter, { target: { value: 'HIGH' } });

    expect(mockOnFilterChange).toHaveBeenCalled();
  });

  it('displays playbook count', () => {
    render(
      <PlaybookLibrary 
        playbooks={mockPlaybooks}
        loading={false}
        error={null}
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText(/Showing 2 of 2 playbooks/)).toBeInTheDocument();
  });
});
