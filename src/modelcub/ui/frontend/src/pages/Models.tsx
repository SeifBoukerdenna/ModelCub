import React, { useState, useEffect } from 'react';
import { RefreshCw, Package, Upload } from 'lucide-react';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { toast } from '@/lib/toast';
import { useApiSync } from '@/hooks/useApiSync';
import { PromotedModel } from '@/lib/api/types';
import { api } from '@/lib/api';
import ModelCard from '@/components/ModelCard';
import ImportModelModal from '@/components/ImportModelModal';

const Models: React.FC = () => {
    useApiSync();
    const selectedProject = useProjectStore(selectSelectedProject);
    const [models, setModels] = useState<PromotedModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);
    const [showImportModal, setShowImportModal] = useState(false);

    const loadModels = async () => {
        try {
            setError(null);
            const data = await api.listModels();
            setModels(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load models');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadModels();
    }, []);

    const handleRefresh = async () => {
        setRefreshing(true);
        await loadModels();
        setRefreshing(false);
        toast.success('Models refreshed');
    };

    const handleImportSuccess = () => {
        setShowImportModal(false);
        loadModels();
        toast.success('Model imported successfully');
    };

    const handleModelClick = (model: PromotedModel) => {
        // TODO: Navigate to model details page or show modal
        console.log('Model clicked:', model);
    };

    const handleDeleteModel = async (model: PromotedModel) => {
        if (!confirm(`Are you sure you want to delete model "${model.name}"?`)) {
            return;
        }

        try {
            await api.deleteModel(model.name);
            toast.success(`Model "${model.name}" deleted successfully`);
            loadModels();
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete model';
            toast.error(message);
        }
    };

    if (loading) {
        return <Loading message="Loading models..." />;
    }

    if (error) {
        return <ErrorMessage message={error} onRetry={loadModels} />;
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
                        Models
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: <strong>{selectedProject?.name}</strong>
                    </p>
                </div>

                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="btn btn--secondary"
                        style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
                        Refresh
                    </button>

                    <button
                        onClick={() => setShowImportModal(true)}
                        className="btn btn--primary"
                        style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        <Upload size={16} />
                        Import Model
                    </button>
                </div>
            </div>

            {/* Models Grid */}
            {models.length === 0 ? (
                <div style={{
                    textAlign: 'center',
                    padding: 'var(--spacing-3xl)',
                    background: 'var(--color-surface)',
                    border: '2px dashed var(--color-border)',
                    borderRadius: 'var(--border-radius-lg)'
                }}>
                    <Package size={48} style={{
                        color: 'var(--color-text-tertiary)',
                        marginBottom: 'var(--spacing-md)'
                    }} />
                    <h3 style={{
                        fontSize: 'var(--font-size-lg)',
                        fontWeight: 600,
                        marginBottom: 'var(--spacing-xs)',
                        color: 'var(--color-text-primary)'
                    }}>
                        No models yet
                    </h3>
                    <p style={{
                        color: 'var(--color-text-secondary)',
                        marginBottom: 'var(--spacing-lg)'
                    }}>
                        Get started by importing a model or training a new one
                    </p>
                    <button
                        onClick={() => setShowImportModal(true)}
                        className="btn btn--primary"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        <Upload size={18} />
                        Import Your First Model
                    </button>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {models.map((model) => (
                        <ModelCard
                            key={model.name}
                            model={model}
                            onClick={() => handleModelClick(model)}
                            onDelete={() => handleDeleteModel(model)}
                        />
                    ))}
                </div>
            )}

            {/* Import Modal */}
            <ImportModelModal
                isOpen={showImportModal}
                onClose={() => setShowImportModal(false)}
                onSuccess={handleImportSuccess}
            />
        </div>
    );
};

export default Models;