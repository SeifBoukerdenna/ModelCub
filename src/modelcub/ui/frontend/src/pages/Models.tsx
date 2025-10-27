import React, { useState, useEffect } from 'react';
import { RefreshCw, Package } from 'lucide-react';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { toast } from '@/lib/toast';
import { useApiSync } from '@/hooks/useApiSync';
import { PromotedModel } from '@/lib/api/types';
import { api } from '@/lib/api';
import ModelCard from '@/components/ModelCard';



const Models: React.FC = () => {
    useApiSync();
    const selectedProject = useProjectStore(selectSelectedProject);
    const [models, setModels] = useState<PromotedModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);

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

    const handleModelClick = (model: PromotedModel) => {
        // TODO: Navigate to model details page or show modal
        console.log('Model clicked:', model);
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
                <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="btn btn--secondary"
                    style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                >
                    <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Content */}
            {models.length === 0 ? (
                /* Empty State */
                <div className="empty-state">
                    <Package size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No models promoted yet</h3>
                    <p className="empty-state__description">
                        Train a model and promote it for production use
                    </p>
                    <code style={{
                        display: 'block',
                        marginTop: 'var(--spacing-md)',
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        backgroundColor: 'var(--color-surface)',
                        borderRadius: 'var(--border-radius-md)',
                        fontSize: 'var(--font-size-sm)'
                    }}>
                        modelcub model promote &lt;run-id&gt; &lt;model-name&gt;
                    </code>
                </div>
            ) : (
                /* Models Grid */
                <>
                    <div style={{
                        marginBottom: 'var(--spacing-md)',
                        color: 'var(--color-text-secondary)',
                        fontSize: 'var(--font-size-sm)'
                    }}>
                        {models.length} {models.length === 1 ? 'model' : 'models'} promoted
                    </div>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                        gap: 'var(--spacing-lg)',
                    }}>
                        {models.map((model) => (
                            <ModelCard
                                key={model.name}
                                model={model}
                                onClick={() => handleModelClick(model)}
                                onDelete={() => {
                                    api.deleteModel(model.name)
                                    handleRefresh()
                                }}
                            />
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

export default Models;