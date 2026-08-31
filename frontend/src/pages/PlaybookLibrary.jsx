import { Card, LoadingState, EmptyState } from '../components/common';
import { PlaybookLibrary as PlaybookLibraryComponent } from '../components/playbooks';
import { usePositiveDeviance } from '../hooks';
import { colors, spacing, typography } from '../tokens';

function PlaybookLibrary() {
  const {
    playbooks,
    loading,
    error,
    fetchPlaybooks,
    retry,
  } = usePositiveDeviance();

  const handleFilterChange = (newFilters) => {
    fetchPlaybooks(newFilters);
  };

  if (loading) return <LoadingState message="Loading playbook library..." />;

  if (error) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: 700, color: colors.text.danger, marginBottom: spacing.md }}>
              Playbook Library Loading Failed
            </h2>
            <p style={{ fontSize: typography.fontSize.base, color: colors.text.secondary, marginBottom: spacing.lg }}>
              {error}
            </p>
            <button
              onClick={retry}
              style={{
                padding: `${spacing.sm} ${spacing.lg}`,
                fontSize: typography.fontSize.base,
                color: 'white',
                backgroundColor: colors.accent.primary,
                border: 'none',
                borderRadius: '0.25rem',
                cursor: 'pointer',
              }}
            >
              Retry
            </button>
          </div>
        </Card>
      </div>
    );
  }

  if (!playbooks || playbooks.playbooks.length === 0) {
    return (
      <div style={{ padding: spacing.xl }}>
        <Card padding="xl">
          <EmptyState
            icon="📚"
            title="No Playbooks Available"
            description="Playbooks are evidence-backed practices extracted from positive deviant projects. None have been created yet."
          />
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: spacing.xl }}>
      <PlaybookLibraryComponent
        playbooks={playbooks.playbooks}
        loading={loading}
        error={error}
        onFilterChange={handleFilterChange}
      />
    </div>
  );
}

export default PlaybookLibrary;
