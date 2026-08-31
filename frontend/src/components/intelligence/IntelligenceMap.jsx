import { Card } from '../common';
import { colors, spacing, typography } from '../../tokens';
import { useNavigate } from 'react-router-dom';

export default function IntelligenceMap({ intelligence, projectId }) {
  const navigate = useNavigate();
  const { data, availability } = intelligence;

  const risk = data.risk;
  const pbe = data.pbe;
  const rcf = data.rcf;
  const dcs = risk?.dcs;
  const nid = data.nid;
  const network = data.network;

  const getNodeColor = (available) => {
    return available ? colors.accent.primary : colors.text.muted;
  };

  const getNodeBorder = (available) => {
    return available ? `2px solid ${colors.accent.primary}` : `2px solid ${colors.border.light}`;
  };

  const handleNodeClick = (node) => {
    switch (node) {
      case 'risk':
        navigate(`/projects/${projectId}/risk-intelligence`);
        break;
      case 'nid':
        navigate(`/projects/${projectId}/narrative-intelligence`);
        break;
      case 'pbe':
        navigate(`/projects/${projectId}/peer-intelligence`);
        break;
      case 'forecast':
        // Navigate to forecast section or page
        break;
      case 'dcs':
        // Navigate to data health page
        navigate('/data-health');
        break;
      case 'network':
        navigate('/network');
        break;
      case 'decision':
        navigate(`/projects/${projectId}/decision-cockpit`);
        break;
      default:
        break;
    }
  };

  return (
    <Card padding="lg">
      <div style={{ marginBottom: spacing.lg }}>
        <h2 style={{ 
          fontSize: typography.fontSize['2xl'], 
          fontWeight: 700, 
          color: colors.text.primary,
          marginBottom: spacing.xs 
        }}>
          INTELLIGENCE MAP
        </h2>
        <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary }}>
          Interactive information architecture. Click a node to explore.
        </p>
      </div>

      {/* Intelligence Map Visualization */}
      <div style={{ 
        padding: spacing.xl,
        backgroundColor: colors.background.tertiary,
        borderRadius: '0.5rem',
        border: `1px solid ${colors.border.light}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: spacing.lg
      }}>
        {/* RISK */}
        <div 
          onClick={() => handleNodeClick('risk')}
          style={{ 
            padding: spacing.lg,
            backgroundColor: colors.background.secondary,
            borderRadius: '0.5rem',
            border: getNodeBorder(availability.risk === 'available'),
            cursor: 'pointer',
            textAlign: 'center',
            minWidth: '200px',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = `${colors.accent.primary}10`;
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = colors.background.secondary;
          }}
        >
          <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.risk === 'available') }}>
            RISK
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            {availability.risk === 'available' ? `${risk?.composite_score?.toFixed(1) || 'N/A'}` : 'UNAVAILABLE'}
          </div>
        </div>

        {/* Middle Row */}
        <div style={{ display: 'flex', gap: spacing.xl, alignItems: 'center' }}>
          {/* NID */}
          <div 
            onClick={() => handleNodeClick('nid')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.secondary,
              borderRadius: '0.5rem',
              border: getNodeBorder(availability.nid === 'available'),
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.primary}10`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = colors.background.secondary;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.nid === 'available') }}>
              NID
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {availability.nid === 'available' ? nid?.status || 'AVAILABLE' : 'UNAVAILABLE'}
            </div>
          </div>

          {/* PBE */}
          <div 
            onClick={() => handleNodeClick('pbe')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.secondary,
              borderRadius: '0.5rem',
              border: getNodeBorder(availability.pbe === 'available'),
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.primary}10`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = colors.background.secondary;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.pbe === 'available') }}>
              PBE
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {availability.pbe === 'available' ? `${pbe?.percentile?.toFixed(0) || 'N/A'}%` : 'UNAVAILABLE'}
            </div>
          </div>

          {/* FORECAST */}
          <div 
            onClick={() => handleNodeClick('forecast')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.secondary,
              borderRadius: '0.5rem',
              border: getNodeBorder(availability.rcf === 'available'),
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.primary}10`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = colors.background.secondary;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.rcf === 'available') }}>
              FORECAST
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {availability.rcf === 'available' ? `${rcf?.p80_completion_months?.toFixed(0) || 'N/A'}mo` : 'UNAVAILABLE'}
            </div>
          </div>
        </div>

        {/* PROJECT */}
        <div 
          style={{ 
            padding: spacing.lg,
            backgroundColor: `${colors.accent.primary}20`,
            borderRadius: '0.5rem',
            border: `2px solid ${colors.accent.primary}`,
            cursor: 'default',
            textAlign: 'center',
            minWidth: '200px'
          }}
        >
          <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: colors.accent.primary }}>
            PROJECT
          </div>
          <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
            {risk?.project_name || 'Current Project'}
          </div>
        </div>

        {/* Bottom Row */}
        <div style={{ display: 'flex', gap: spacing.xl, alignItems: 'center' }}>
          {/* DCS */}
          <div 
            onClick={() => handleNodeClick('dcs')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.secondary,
              borderRadius: '0.5rem',
              border: getNodeBorder(availability.risk === 'available'),
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.primary}10`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = colors.background.secondary;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.risk === 'available') }}>
              DCS
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {availability.risk === 'available' ? `${dcs?.dcs_score?.toFixed(0) || 'N/A'}%` : 'UNAVAILABLE'}
            </div>
          </div>

          {/* NETWORK */}
          <div 
            onClick={() => handleNodeClick('network')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: colors.background.secondary,
              borderRadius: '0.5rem',
              border: getNodeBorder(availability.network === 'available'),
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.primary}10`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = colors.background.secondary;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: getNodeColor(availability.network === 'available') }}>
              NETWORK
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              {availability.network === 'available' 
                ? `${network?.metadata?.total_nodes || 0} nodes` 
                : 'UNAVAILABLE'}
            </div>
          </div>

          {/* DECISION */}
          <div 
            onClick={() => handleNodeClick('decision')}
            style={{ 
              padding: spacing.lg,
              backgroundColor: `${colors.accent.success}20`,
              borderRadius: '0.5rem',
              border: `2px solid ${colors.accent.success}`,
              cursor: 'pointer',
              textAlign: 'center',
              minWidth: '150px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = `${colors.accent.success}30`;
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = `${colors.accent.success}20`;
            }}
          >
            <div style={{ fontSize: typography.fontSize.lg, fontWeight: 700, color: colors.accent.success }}>
              DECISION
            </div>
            <div style={{ fontSize: typography.fontSize.sm, color: colors.text.muted }}>
              Cockpit
            </div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: spacing.lg, fontSize: typography.fontSize.sm, color: colors.text.muted }}>
        <strong>NOTE:</strong> This is an information architecture visualization. Click nodes to navigate to detailed intelligence pages.
      </div>
    </Card>
  );
}
