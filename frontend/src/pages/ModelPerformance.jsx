import { useEffect, useState } from 'react';
import { getModelPerformance } from '../services/api';
import { Card, Badge, LoadingState, EmptyState } from '../components/common';
import { ModelCard } from '../components/domain';
import { colors, spacing, typography, borderRadius } from '../tokens';

function ModelPerformance() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await getModelPerformance();
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingState message="Loading model performance data..." />;
  if (error) return <EmptyState icon="⚠️" title="Error" description={error} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Experimental Warning Banner */}
      <div style={{
        padding: spacing.md,
        backgroundColor: `${colors.accent.warning}10`,
        borderLeft: `4px solid ${colors.accent.warning}`,
        borderRadius: borderRadius.sm,
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: spacing.sm }}>
          <span style={{ fontSize: '1.25rem' }}>⚠️</span>
          <div>
            <div style={{ 
              fontWeight: 600,
              color: colors.accent.warning,
              marginBottom: spacing.xs 
            }}>
              EXPERIMENTAL MODELS
            </div>
            <div style={{ 
              fontSize: typography.fontSize.sm,
              color: colors.text.secondary 
            }}>
              Limited completed outcomes (160 projects). Not production validated.
            </div>
          </div>
        </div>
      </div>

      {/* Holdout Warning */}
      {data.holdout_size && (
        <div style={{
          padding: spacing.md,
          backgroundColor: `${colors.accent.danger}10`,
          borderLeft: `4px solid ${colors.accent.danger}`,
          borderRadius: borderRadius.sm,
        }}>
          <div style={{ fontWeight: 600, color: colors.accent.danger }}>
            Holdout Size: {data.holdout_size} projects — {data.holdout_warning}
          </div>
        </div>
      )}

      {/* Data Source Badge */}
      <div>
        <Badge variant="info">REAL PAIMANA DATA — {data.data_source}</Badge>
      </div>

      {/* Model Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(3, 1fr)', 
        gap: spacing.lg 
      }}>
        {data.models.map((model) => (
          <ModelCard
            key={model.model_type}
            name={model.model_type.replace('_', ' ')}
            version={model.version}
            status={model.is_active ? 'production' : 'deprecated'}
            metrics={{
              precision: model.precision,
              recall: model.recall,
              f1: model.f1,
              rocAuc: model.roc_auc,
            }}
          />
        ))}
      </div>

      {/* Active Model Info */}
      {data.active_model && (
        <Card padding="md">
          <div style={{ 
            fontSize: typography.fontSize.sm,
            color: colors.accent.primary,
            fontWeight: 600 
          }}>
            Active Model: {data.active_model}
          </div>
        </Card>
      )}
    </div>
  );
}

export default ModelPerformance;
