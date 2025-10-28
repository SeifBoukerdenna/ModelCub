import React, { useEffect, useState } from 'react';
import { Activity, RefreshCw, Plus } from 'lucide-react';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { toast } from '@/lib/toast';
import { useApiSync } from '@/hooks/useApiSync';
import type { TrainingRun } from '@/lib/api/types';
import { useListRuns } from '@/lib/api/useListRuns';
import { api } from '@/lib/api';
import RunCard from '@/components/RunCard';
import CreateRunModal from '@/components/CreateRunModal';

const Runs: React.FC = () => {
    useApiSync();
    const selectedProject = useProjectStore(selectSelectedProject);
    const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);

    const {
        data: runs,
        loading,
        error,
        execute: loadRuns
    } = useListRuns(statusFilter);

    useEffect(() => {
        loadRuns();
    }, [statusFilter]);

    // Refresh once when training completes
    useEffect(() => {
        const hasActiveRuns = runs?.some(
            run => run.status === 'pending' || run.status === 'running'
        );

        if (!hasActiveRuns) return;

        // Check status once every 3 seconds, refresh page when complete
        const interval = setInterval(async () => {
            try {
                const updated = await api.listRuns(statusFilter);
                const stillActive = updated.some(
                    run => run.status === 'pending' || run.status === 'running'
                );

                // If no longer active, do final refresh and stop polling
                if (!stillActive) {
                    await loadRuns();
                }
            } catch (err) {
                console.error('Failed to check run status:', err);
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [runs, statusFilter, loadRuns]);

    const handleRefresh = async () => {
        await loadRuns();
        toast.success('Runs refreshed');
    };

    const handleStart = async (run: TrainingRun) => {
        setIsProcessing(true);
        try {
            await api.startRun(run.id);
            toast.success(`Run "${run.id}" started`);
            await loadRuns();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to start run');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleStop = async (run: TrainingRun) => {
        setIsProcessing(true);
        try {
            await api.stopRun(run.id);
            toast.success(`Run "${run.id}" stopped`);
            await loadRuns();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to stop run');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleDelete = async (run: TrainingRun) => {
        setIsProcessing(true);
        try {
            await api.deleteRun(run.id);
            toast.success(`Run "${run.id}" deleted`);
            await loadRuns();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to delete run');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleCreateSuccess = () => {
        loadRuns();
    };

    if (loading) {
        return <Loading message="Loading runs..." />;
    }

    if (error) {
        return <ErrorMessage message={error} onRetry={loadRuns} />;
    }

    return (
        <div>
            {/* Header */}
            <div style={{
                marginBottom: 'var(--spacing-xl)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div>
                    <h1 style={{
                        fontSize: 'var(--font-size-2xl)',
                        fontWeight: 700,
                        marginBottom: 'var(--spacing-xs)'
                    }}>
                        Training Runs
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: <strong>{selectedProject?.name}</strong>
                    </p>
                </div>
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    {/* Status Filter */}
                    <select
                        value={statusFilter || 'all'}
                        onChange={(e) => setStatusFilter(e.target.value === 'all' ? undefined : e.target.value)}
                        style={{
                            padding: 'var(--spacing-xs) var(--spacing-sm)',
                            borderRadius: 'var(--border-radius-sm)',
                            border: '1px solid var(--color-border)',
                            backgroundColor: 'var(--color-surface)',
                            cursor: 'pointer'
                        }}
                    >
                        <option value="all">All Runs</option>
                        <option value="pending">Pending</option>
                        <option value="running">Running</option>
                        <option value="completed">Completed</option>
                        <option value="failed">Failed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="btn btn--primary"
                        style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        <Plus size={16} />
                        Create Run
                    </button>
                    <button
                        onClick={handleRefresh}
                        disabled={isProcessing}
                        className="btn btn--secondary"
                        style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        <RefreshCw size={16} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Content */}
            {runs?.length === 0 ? (
                <div style={{
                    textAlign: 'center',
                    padding: 'var(--spacing-2xl)',
                    color: 'var(--color-text-secondary)'
                }}>
                    <Activity size={48} style={{ opacity: 0.3, marginBottom: 'var(--spacing-md)' }} />
                    <p style={{ fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-sm)' }}>
                        No training runs yet
                    </p>
                    <p style={{ fontSize: 'var(--font-size-sm)' }}>
                        Create your first training run to get started
                    </p>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: 'var(--spacing-md)'
                }}>
                    {runs?.map(run => (
                        <RunCard
                            key={run.id}
                            run={run}
                            onStart={handleStart}
                            onStop={handleStop}
                            onDelete={handleDelete}
                            onRunUpdated={loadRuns}
                        />
                    ))}
                </div>
            )}

            {/* Create Run Modal */}
            {showCreateModal && (
                <CreateRunModal
                    isOpen={showCreateModal}
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={handleCreateSuccess}
                />
            )}
        </div>
    );
};

export default Runs;