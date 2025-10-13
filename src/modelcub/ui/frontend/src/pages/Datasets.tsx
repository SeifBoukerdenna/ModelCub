import { useEffect, useState } from 'react';
import {
    Database,
    Upload,
    RefreshCw,
    AlertCircle,
    CheckCircle,
    Image as ImageIcon
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// NEW: Import from centralized API
import { api, useListDatasets, type Dataset } from '@/lib/api';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import { toast } from '@/lib/toast';

// Components
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import ImportDatasetModal from '@/components/ImportDatasetModal';

const Datasets = () => {
    const navigate = useNavigate();
    const selectedProject = useProjectStore(selectSelectedProject);

    // NEW: Use API hooks
    const {
        data: datasets,
        loading,
        error,
        execute: loadDatasets
    } = useListDatasets();

    const [showImportModal, setShowImportModal] = useState(false);

    // Set project context and load datasets when project changes
    useEffect(() => {
        if (selectedProject) {
            api.setProjectPath(selectedProject.path);
            loadDatasets();
        }
    }, [selectedProject?.path]);

    // Handle import success
    const handleImportSuccess = () => {
        setShowImportModal(false);
        loadDatasets();
        toast.success('Dataset imported successfully');
    };

    // No project selected
    if (!selectedProject) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Datasets</h1>
                </div>
                <div className="empty-state">
                    <AlertCircle size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No Project Selected</h3>
                    <p className="empty-state__description">
                        Select a project from the sidebar to manage datasets.
                    </p>
                </div>
            </div>
        );
    }

    // Loading state
    if (loading && !datasets) {
        return <Loading message={`Loading datasets for ${selectedProject.name}...`} />;
    }

    // Error state
    if (error && !datasets) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Datasets</h1>
                </div>
                <ErrorMessage message={error} />
                <button
                    onClick={() => loadDatasets()}
                    className="btn btn--secondary"
                    style={{ marginTop: 'var(--spacing-md)' }}
                >
                    <RefreshCw size={18} />
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-xs)'
                }}>
                    <div>
                        <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                            Datasets
                        </h1>
                        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                            Project: <strong>{selectedProject.name}</strong>
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            className="btn btn--secondary"
                            onClick={() => loadDatasets()}
                            disabled={loading}
                        >
                            <RefreshCw size={18} className={loading ? 'spinner' : ''} />
                            Refresh
                        </button>
                        <button
                            className="btn btn--primary"
                            onClick={() => setShowImportModal(true)}
                        >
                            <Upload size={18} />
                            Import Dataset
                        </button>
                    </div>
                </div>
            </div>

            {/* Datasets Grid */}
            {!datasets || datasets.length === 0 ? (
                <div className="empty-state">
                    <Database size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No datasets yet</h3>
                    <p className="empty-state__description">
                        Import images to create your first dataset
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => setShowImportModal(true)}
                    >
                        <Upload size={20} />
                        Import Dataset
                    </button>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {datasets.map((dataset: Dataset) => (
                        <DatasetCard
                            key={dataset.id}
                            dataset={dataset}
                            onClick={() => navigate(`/datasets/${dataset.id}`)}
                        />
                    ))}
                </div>
            )}

            {/* Import Modal */}
            <ImportDatasetModal
                isOpen={showImportModal}
                onClose={() => setShowImportModal(false)}
                onSuccess={handleImportSuccess}
            />
        </div>
    );
};

// Dataset Card Component
interface DatasetCardProps {
    dataset: Dataset;
    onClick: () => void;
}

const DatasetCard = ({ dataset, onClick }: DatasetCardProps) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ready':
                return {
                    bg: 'var(--color-success-100)',
                    text: 'var(--color-success-700)'
                };
            case 'processing':
                return {
                    bg: 'var(--color-warning-100)',
                    text: 'var(--color-warning-700)'
                };
            default:
                return {
                    bg: 'var(--color-gray-100)',
                    text: 'var(--color-gray-700)'
                };
        }
    };

    const statusColor = getStatusColor(dataset.status);

    return (
        <div
            className="card"
            onClick={onClick}
            style={{
                cursor: 'pointer',
                transition: 'all 0.2s ease',
            }}
        >
            {/* Card Header */}
            <div className="card__header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <Database size={20} style={{ color: 'var(--color-primary-500)' }} />
                    <h3 className="card__title">{dataset.name}</h3>
                </div>
                <span
                    className="badge"
                    style={{
                        backgroundColor: statusColor.bg,
                        color: statusColor.text
                    }}
                >
                    <CheckCircle size={14} />
                    {dataset.status}
                </span>
            </div>

            {/* Card Body */}
            <div className="card__body">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)'
                    }}>
                        <span style={{ color: 'var(--color-text-secondary)' }}>
                            <ImageIcon size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
                            Images:
                        </span>
                        <span style={{ fontWeight: 500 }}>{dataset.images}</span>
                    </div>

                    {dataset.classes && dataset.classes.length > 0 && (
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            fontSize: 'var(--font-size-sm)'
                        }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Classes:</span>
                            <span style={{ fontWeight: 500 }}>{dataset.classes.length}</span>
                        </div>
                    )}

                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)'
                    }}>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Size:</span>
                        <span style={{ fontWeight: 500 }}>{dataset.size_formatted}</span>
                    </div>
                </div>

                {/* Classes preview */}
                {dataset.classes && dataset.classes.length > 0 && (
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                        <div style={{
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--color-text-secondary)',
                            marginBottom: 'var(--spacing-xs)'
                        }}>
                            Classes:
                        </div>
                        <div style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: 'var(--spacing-xs)'
                        }}>
                            {dataset.classes.slice(0, 5).map((cls) => (
                                <span
                                    key={cls}
                                    className="badge"
                                    style={{
                                        fontSize: 'var(--font-size-xs)',
                                        backgroundColor: 'var(--color-primary-50)',
                                        color: 'var(--color-primary-700)'
                                    }}
                                >
                                    {cls}
                                </span>
                            ))}
                            {dataset.classes.length > 5 && (
                                <span
                                    className="badge"
                                    style={{
                                        fontSize: 'var(--font-size-xs)',
                                        backgroundColor: 'var(--color-gray-100)',
                                        color: 'var(--color-text-secondary)'
                                    }}
                                >
                                    +{dataset.classes.length - 5} more
                                </span>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Datasets;