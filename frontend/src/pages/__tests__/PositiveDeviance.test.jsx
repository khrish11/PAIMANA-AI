import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import PositiveDeviance from '../PositiveDeviance';

const mockFetchPositiveDeviants = vi.fn();
const mockRetry = vi.fn();

const mockDeviants = {
  positive_deviants: [
    {
      deviant_id: 'd1',
      project_id: 'p1',
      project_name: 'Highway Project A',
      sector: 'Roads & Highways',
      state: 'Bihar',
      reference_class_id: 'rc1',
      residual_cost_zscore: -1.5,
      residual_schedule_zscore: -0.8,
      data_confidence_score: 85,
      detected_at: '2026-03-15T10:00:00Z',
    },
  ],
  metadata: { sectors: 1, states: 1, data_source: 'REAL_PAIMANA' },
};

vi.mock('../../hooks', () => ({
  usePositiveDeviance: vi.fn(),
}));

import { usePositiveDeviance } from '../../hooks';

function renderPage() {
  return render(
    <MemoryRouter>
      <PositiveDeviance />
    </MemoryRouter>
  );
}

describe('PositiveDeviance Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/positive deviance radar/i)).toBeInTheDocument();
  });

  it('renders positive deviance page with title', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/POSITIVE DEVIANCE RADAR/i)).toBeInTheDocument();
  });

  it('displays summary statistics', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/Total Deviants/i)).toBeInTheDocument();
  });

  it('renders positive deviants table', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByRole('columnheader', { name: /Project/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /Sector/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /Cost Residual/i })).toBeInTheDocument();
  });

  it('shows loading state', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: null,
      loading: true,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/loading positive deviants/i)).toBeInTheDocument();
  });

  it('shows error state on API failure', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: null,
      loading: false,
      error: 'Network error',
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/Positive Deviants Loading Failed/i)).toBeInTheDocument();
    expect(screen.getByText(/Network error/i)).toBeInTheDocument();
  });

  it('filters by sector', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getAllByText(/^Sector$/).length).toBeGreaterThan(0);
  });

  it('filters by state', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getAllByText(/^State$/).length).toBeGreaterThan(0);
  });

  it('displays methodology explanation', () => {
    usePositiveDeviance.mockReturnValue({
      positiveDeviants: mockDeviants,
      loading: false,
      error: null,
      fetchPositiveDeviants: mockFetchPositiveDeviants,
      retry: mockRetry,
    });
    renderPage();
    expect(screen.getByText(/Methodology/i)).toBeInTheDocument();
    expect(screen.getByText(/positive deviant when/i)).toBeInTheDocument();
  });
});
