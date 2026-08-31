import { useState } from 'react';
import { Card, EmptyState } from '../common';
import { colors, spacing, typography, borderRadius } from '../../tokens';

function RiskJourney({ historyData, onPointClick }) {
  const [selectedPoint, setSelectedPoint] = useState(null);

  if (!historyData || historyData.length === 0) {
    return (
      <Card padding="lg">
        <EmptyState icon="📈" title="No Risk History" description="Historical risk observations are unavailable for this project." />
      </Card>
    );
  }

  const maxRisk = Math.max(...historyData.map(d => d.risk_score || 0), 100);
  const minRisk = Math.min(...historyData.map(d => d.risk_score || 0), 0);

  const chartHeight = 200;
  const chartWidth = '100%';
  const padding = { top: 20, right: 20, bottom: 40, left: 40 };

  const getX = (index) => {
    const usableWidth = 100 - (padding.left / chartWidth * 100) - (padding.right / chartWidth * 100);
    return padding.left + (index / (historyData.length - 1)) * usableWidth;
  };

  const getY = (value) => {
    const usableHeight = chartHeight - padding.top - padding.bottom;
    const normalized = (value - minRisk) / (maxRisk - minRisk || 1);
    return chartHeight - padding.bottom - (normalized * usableHeight);
  };

  const getRiskColor = (score) => {
    if (score >= 80) return colors.risk.critical;
    if (score >= 65) return colors.risk.high;
    if (score >= 45) return colors.risk.medium;
    return colors.risk.low;
  };

  return (
    <Card padding="lg">
      <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: 600, color: colors.text.primary, marginBottom: spacing.lg }}>
        Risk Journey
      </h3>

      <div style={{ position: 'relative', height: `${chartHeight}px`, width: chartWidth }}>
        <svg width="100%" height="100%" viewBox={`0 0 100 ${chartHeight}`} preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((fraction) => {
            const y = padding.top + fraction * (chartHeight - padding.top - padding.bottom);
            return (
              <line
                key={fraction}
                x1={padding.left}
                y1={y}
                x2={100 - padding.right}
                y2={y}
                stroke={colors.border.light}
                strokeWidth="0.2"
                strokeDasharray="1,1"
              />
            );
          })}

          {/* Risk line */}
          <polyline
            points={historyData.map((d, i) => `${getX(i)},${getY(d.risk_score || 0)}`).join(' ')}
            fill="none"
            stroke={colors.accent.primary}
            strokeWidth="0.5"
          />

          {/* Data points */}
          {historyData.map((d, i) => {
            const x = getX(i);
            const y = getY(d.risk_score || 0);
            const isSelected = selectedPoint === i;
            return (
              <g key={i}>
                <circle
                  cx={x}
                  cy={y}
                  r={isSelected ? 1.5 : 0.8}
                  fill={getRiskColor(d.risk_score || 0)}
                  stroke={colors.background.primary}
                  strokeWidth="0.3"
                  style={{ cursor: 'pointer', transition: 'r 150ms' }}
                  onClick={() => {
                    setSelectedPoint(i);
                    onPointClick?.(d, i);
                  }}
                  onMouseEnter={(e) => {
                    e.target.setAttribute('r', '1.5');
                  }}
                  onMouseLeave={(e) => {
                    if (selectedPoint !== i) {
                      e.target.setAttribute('r', '0.8');
                    }
                  }}
                />
                {/* X-axis labels */}
                <text
                  x={x}
                  y={chartHeight - 5}
                  fontSize="2"
                  fill={colors.text.muted}
                  textAnchor="middle"
                >
                  {d.month || ''}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Selected point details */}
      {selectedPoint !== null && historyData[selectedPoint] && (
        <div style={{ marginTop: spacing.md, padding: spacing.md, backgroundColor: colors.background.tertiary, borderRadius: borderRadius.md }}>
          <div style={{ marginBottom: spacing.sm, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            {historyData[selectedPoint].month || 'Selected Period'}
          </div>
          <div style={{ display: 'flex', gap: spacing.lg }}>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>Risk Score</div>
              <div style={{ fontSize: typography.fontSize.xl, fontWeight: 600, color: colors.text.primary }}>
                {historyData[selectedPoint].risk_score?.toFixed(1) || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>Category</div>
              <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: getRiskColor(historyData[selectedPoint].risk_score || 0) }}>
                {historyData[selectedPoint].risk_category || 'N/A'}
              </div>
            </div>
            {historyData[selectedPoint].change !== undefined && (
              <div>
                <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted }}>Change</div>
                <div style={{ fontSize: typography.fontSize.base, fontWeight: 600, color: historyData[selectedPoint].change >= 0 ? colors.accent.danger : colors.accent.success }}>
                  {historyData[selectedPoint].change >= 0 ? '+' : ''}{historyData[selectedPoint].change?.toFixed(1) || 'N/A'}
                </div>
              </div>
            )}
          </div>
          {historyData[selectedPoint].drivers && historyData[selectedPoint].drivers.length > 0 && (
            <div style={{ marginTop: spacing.sm }}>
              <div style={{ fontSize: typography.fontSize.xs, color: colors.text.muted, marginBottom: spacing.xs }}>
                Primary Drivers
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: spacing.xs }}>
                {historyData[selectedPoint].drivers.slice(0, 3).map((driver, idx) => (
                  <span
                    key={idx}
                    style={{
                      padding: `${spacing.xs} ${spacing.sm}`,
                      backgroundColor: colors.background.secondary,
                      borderRadius: borderRadius.sm,
                      fontSize: typography.fontSize.xs,
                      color: colors.text.secondary,
                    }}
                  >
                    {driver}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default RiskJourney;
