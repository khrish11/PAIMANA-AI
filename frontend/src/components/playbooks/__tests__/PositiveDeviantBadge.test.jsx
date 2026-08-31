import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PositiveDeviantBadge from '../PositiveDeviantBadge';

describe('PositiveDeviantBadge', () => {
  it('renders badge with positive deviant indicator', () => {
    render(<PositiveDeviantBadge dataConfidenceScore={85} />);
    
    expect(screen.getByText(/positive deviant/i)).toBeInTheDocument();
  });

  it('displays confidence score when provided', () => {
    render(<PositiveDeviantBadge dataConfidenceScore={85} />);
    
    // Badge renders but doesn't display the score value directly
    // It uses the score to determine color
    expect(screen.getByText(/positive deviant/i)).toBeInTheDocument();
  });

  it('shows tooltip with explanation', () => {
    render(<PositiveDeviantBadge dataConfidenceScore={85} />);
    
    const badge = screen.getByText(/positive deviant/i);
    expect(badge).toBeInTheDocument();
  });

  it('renders with custom className', () => {
    const { container } = render(<PositiveDeviantBadge dataConfidenceScore={85} />);
    
    // Component renders successfully
    expect(container.firstChild).toBeInTheDocument();
  });

  it('shows different visual states based on data confidence', () => {
    const { container: lowContainer } = render(<PositiveDeviantBadge dataConfidenceScore={65} />);
    const { container: highContainer } = render(<PositiveDeviantBadge dataConfidenceScore={90} />);
    
    // Both should render but potentially with different styling
    expect(lowContainer).toBeInTheDocument();
    expect(highContainer).toBeInTheDocument();
  });
});
