import { useState, useEffect } from 'react';
import { Database, Upload, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { api, useListDatasets } from '@/lib/api';
import { toast } from '@/lib/toast';
import ImportDatasetModal from '@/components/ImportDatasetModal';
import ClassManagerModal from '@/components/ClassManagerModal';
import DeleteConfirmModal from '@/components/DeleteConfirmModal';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import { useApiSync } from '@/hooks/useApiSync';
import DatasetCard from '@/components/datasets/DatasetCard';
import { Dataset } from '@/lib/api/types';

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
        setClassManagerDataset(null)
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
                            onClick={() => navigate(`/datasets/${dataset.name}`)}
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
                    onClose={() => setClassManagerDataset(null)}
                    datasetId={classManagerDataset.name}
                    initialClasses={classManagerDataset.classes}
                    onUpdate={handleClassUpdate}
                />
            )}

            {/* Delete Confirmation Modal */}
            {datasetToDelete && (
                <DeleteConfirmModal
                    title="Delete Dataset"
                    message={
                        <>
                            <p>Are you sure you want to delete <strong>{datasetToDelete.name}</strong>?</p>
                            <p style={{ marginTop: 'var(--spacing-sm)' }}>
                                This will permanently delete the images and cannot be undone.
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

export default Datasets;