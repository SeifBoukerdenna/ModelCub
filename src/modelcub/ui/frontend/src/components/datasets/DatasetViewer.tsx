import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/useToast';
import { api } from '@/lib/api';

// Hooks

import { useDatasetJobs } from '@/hooks/useDatasetJobs';
import { useJobActions } from '@/hooks/useJobActions';

// Components
import { DatasetHeader } from '@/components/datasets/DatasetHeader';
import { DatasetStats } from '@/components/datasets/DatasetStats';
import { DatasetClasses } from '@/components/datasets/DatasetClasses';
import { DatasetJobsSection } from '@/components/datasets/DatasetJobsSection';
import { JobDetailsModal } from '@/components/datasets/JobDetailsModal';
import ClassManagerModal from '@/components/ClassManagerModal';
import DeleteConfirmModal from '@/components/DeleteConfirmModal';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';

import type { Dataset, Job } from '@/lib/api/types';
import { useDatasetDetails } from '@/hooks/useDatasetDetail';

const DatasetViewer = () => {
    const { name } = useParams<{ name: string }>();
    const navigate = useNavigate();
    const { showToast } = useToast();

    // Modal states
    const [classManagerDataset, setClassManagerDataset] = useState<Dataset | null>(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [selectedJob, setSelectedJob] = useState<Job | null>(null);

    // Load dataset
    const { dataset, loading, error, reload: reloadDataset } = useDatasetDetails(name);

    // Load jobs
    const {
        activeJobs,
        completedJobs,
        loading: jobsLoading,
        reload: reloadJobs
    } = useDatasetJobs(dataset?.name);

    // Job actions
    const { startAnnotation, continueJob, resumeJob } = useJobActions(
        dataset?.name,
        reloadJobs
    );

    // Delete dataset
    const handleDelete = async () => {
        if (!dataset) return;
        setIsDeleting(true);
        try {
            await api.deleteDataset(dataset.name);
            showToast('Dataset deleted successfully', 'success');
            navigate('/datasets');
        } catch (err: any) {
            showToast(err.message || 'Failed to delete dataset', 'error');
        } finally {
            setIsDeleting(false);
            setShowDeleteModal(false);
        }
    };

    // Loading and error states
    if (loading) return <Loading message="Loading dataset..." />;
    if (error || !dataset) return <ErrorMessage message={error || 'Dataset not found'} />;

    return (
        <div className="dataset-viewer">
            {/* Header */}
            <DatasetHeader
                datasetName={dataset.name}
                onBack={() => navigate('/datasets')}
                onManageClasses={() => setClassManagerDataset(dataset)}
                onDelete={() => setShowDeleteModal(true)}
            />

            {/* Stats */}
            <DatasetStats
                dataset={dataset}
                totalJobs={activeJobs.length + completedJobs.length}
            />

            {/* Classes */}
            <DatasetClasses
                classes={dataset.classes || []}
                onManage={() => setClassManagerDataset(dataset)}
            />

            {/* Jobs */}
            <DatasetJobsSection
                activeJobs={activeJobs}
                completedJobs={completedJobs}
                loading={jobsLoading}
                onStartAnnotation={startAnnotation}
                onContinueJob={continueJob}
                onResumeJob={resumeJob}
                onRefresh={reloadJobs}
                onJobClick={(job) => {
                    setSelectedJob(job)
                    console.log("clicked the selected JOB")
                }
                }
            />

            {/* Modals */}
            {classManagerDataset && (
                <ClassManagerModal
                    isOpen={true}
                    onClose={() => setClassManagerDataset(null)}
                    datasetId={classManagerDataset.name}
                    initialClasses={classManagerDataset.classes || []}
                    onUpdate={reloadDataset}
                />
            )}

            {showDeleteModal && (
                <DeleteConfirmModal
                    isOpen={true}
                    title="Delete Dataset"
                    message={
                        <>
                            <p>Are you sure you want to delete <strong>{dataset.name}</strong>?</p>
                            <p style={{ marginTop: 'var(--spacing-sm)' }}>
                                This will permanently delete all images and annotations.
                            </p>
                        </>
                    }
                    onConfirm={handleDelete}
                    onCancel={() => setShowDeleteModal(false)}
                    isDeleting={isDeleting}
                />
            )}

            {selectedJob && (
                <JobDetailsModal job={selectedJob} onClose={() => setSelectedJob(null)} />
            )}
        </div>
    );
};

export default DatasetViewer;