import { useState, useEffect } from 'react';
import { Database, Upload, RefreshCw, CheckCircle, Settings, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { api, useListDatasets, type Dataset } from '@/lib/api';
import { toast } from '@/lib/toast';
import ImportDatasetModal from '@/components/ImportDatasetModal';
import ClassManagerModal from '@/components/ClassManagerModal';
import DeleteConfirmModal from '@/components/DeleteConfirmModal';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { useApiSync } from '@/hooks/useApiSync';

const Datasets = () => {
    useApiSync();
    const navigate = useNavigate();
    const [showImportModal, setShowImportModal] = useState(false);
    const [classManagerDataset, setClassManagerDataset] = useState<Dataset | null>(null);
    const [datasetToDelete, setDatasetToDelete] = useState<Dataset | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);
    const [refreshing, setRefreshing] = useState(false);

    const {
        data: datasets,
        loading,
        error,
        execute: loadDatasets
    } = useListDatasets();

    useEffect(() => {
        loadDatasets();
    }, []);

    const handleRefresh = async () => {
        setRefreshing(true);
        await loadDatasets();
        setRefreshing(false);
        toast.success('Datasets refreshed');
    };

    const handleImportSuccess = () => {
        setShowImportModal(false);
        toast.success('Dataset imported successfully');
        loadDatasets();
    };

    const handleClassUpdate = () => {
        loadDatasets();
    };

    const handleDeleteConfirm = async () => {
        if (!datasetToDelete) return;

        setIsDeleting(true);
        try {
            await api.deleteDataset(datasetToDelete.name);
            toast.success(`Dataset "${datasetToDelete.name}" deleted`);
            setDatasetToDelete(null);
            loadDatasets();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to delete dataset');
        } finally {
            setIsDeleting(false);
        }
    };

    if (loading && !datasets) {
        return <Loading message="Loading datasets..." />;
    }

    if (error) {
        return <ErrorMessage message={error} />;
    }

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-md)'
                }}>
                    <div>
                        <h1 style={{
                            fontSize: 'var(--font-size-2xl)',
                            fontWeight: 700,
                            color: 'var(--color-text-primary)',
                            margin: 0
                        }}>
                            Datasets
                        </h1>
                        <p style={{
                            fontSize: 'var(--font-size-sm)',
                            color: 'var(--color-text-secondary)',
                            margin: 'var(--spacing-xs) 0 0 0'
                        }}>
                            Manage your training datasets
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            className="btn btn--secondary"
                            onClick={handleRefresh}
                            disabled={refreshing}
                        >
                            <RefreshCw size={18} className={refreshing ? 'spinner' : ''} />
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
                            onManageClasses={(e) => {
                                e.stopPropagation();
                                setClassManagerDataset(dataset);
                            }}
                            onDelete={(e) => {
                                e.stopPropagation();
                                setDatasetToDelete(dataset);
                            }}
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

            {/* Class Manager Modal */}
            {classManagerDataset && (
                <ClassManagerModal
                    isOpen={!!classManagerDataset}
                    onClose={() => setClassManagerDataset(null)}
                    datasetId={classManagerDataset.name}
                    initialClasses={classManagerDataset.classes}
                    onUpdate={handleClassUpdate}
                />
            )}

            {/* Delete Confirmation Modal */}
            {datasetToDelete && (
                <DeleteConfirmModal
                    isOpen={!!datasetToDelete}
                    title="Delete Dataset"
                    message={
                        <>
                            <p>Are you sure you want to delete <strong>{datasetToDelete.name}</strong>?</p>
                            <p style={{ marginTop: 'var(--spacing-sm)' }}>
                                This will permanently delete {datasetToDelete.images} images and cannot be undone.
                            </p>
                        </>
                    }
                    onConfirm={handleDeleteConfirm}
                    onCancel={() => setDatasetToDelete(null)}
                    isDeleting={isDeleting}
                />
            )}
        </div>
    );
};

// Dataset Card Component
interface DatasetCardProps {
    dataset: Dataset;
    onClick: () => void;
    onManageClasses: (e: React.MouseEvent) => void;
    onDelete: (e: React.MouseEvent) => void;
}

const DatasetCard = ({ dataset, onClick, onManageClasses, onDelete }: DatasetCardProps) => {
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
            <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                marginBottom: 'var(--spacing-md)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <Database size={20} style={{ color: 'var(--color-primary-500)' }} />
                    <h3 style={{
                        fontSize: 'var(--font-size-lg)',
                        fontWeight: 600,
                        color: 'var(--color-text-primary)',
                        margin: 0
                    }}>
                        {dataset.name}
                    </h3>
                </div>
                <span
                    className="badge"
                    style={{
                        backgroundColor: statusColor.bg,
                        color: statusColor.text,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-xs)'
                    }}
                >
                    <CheckCircle size={14} />
                    {dataset.status}
                </span>
            </div>

            {/* Card Body */}
            <div>
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--spacing-xs)',
                    marginBottom: 'var(--spacing-md)'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)'
                    }}>
                        <span>Images:</span>
                        <strong style={{ color: 'var(--color-text-primary)' }}>
                            {dataset.images}
                        </strong>
                    </div>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)'
                    }}>
                        <span>Size:</span>
                        <strong style={{ color: 'var(--color-text-primary)' }}>
                            {dataset.size_formatted}
                        </strong>
                    </div>
                </div>

                {/* Classes */}
                {(
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: 'var(--spacing-xs)'
                        }}>
                            <div style={{
                                fontSize: 'var(--font-size-xs)',
                                fontWeight: 500,
                                color: 'var(--color-text-secondary)'
                            }}>
                                {dataset.classes && dataset.classes.length > 0 &&
                                    <>
                                        Classes:
                                    </>
                                }
                            </div>
                            <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                                <button
                                    className="btn btn--xs btn--secondary"
                                    onClick={onManageClasses}
                                    title="Manage classes"
                                    style={{
                                        padding: '4px 8px',
                                        fontSize: 'var(--font-size-xs)'
                                    }}
                                >
                                    <Settings size={12} />
                                    Edit
                                </button>
                                <button
                                    className="btn btn--xs btn--danger"
                                    onClick={onDelete}
                                    title="Delete dataset"
                                    style={{ padding: '4px 8px', fontSize: 'var(--font-size-xs)' }}
                                >
                                    <Trash2 size={12} />
                                </button>
                            </div>
                        </div>
                        <div className="classes-list">
                            {dataset.classes && dataset.classes.length > 0 && dataset.classes.slice(0, 5).map((cls, idx) => (
                                <span key={`${cls}-${idx}`} className="class-badge">
                                    {cls}
                                </span>
                            ))}
                            {dataset.classes.length > 5 && (
                                <span className="badge badge--gray">
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