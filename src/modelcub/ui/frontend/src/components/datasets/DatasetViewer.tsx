import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, Settings, Trash2, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import type { Dataset, Job } from '@/lib/api/types';
import { useToast } from '@/hooks/useToast';
import Loading from '../Loading';
import ErrorMessage from '../ErrorMessage';
import ClassManagerModal from '../ClassManagerModal';
import DeleteConfirmModal from '../DeleteConfirmModal';
import { JobDetailsModal } from './JobDetailsModal';

const DatasetViewer = () => {
    const { name } = useParams<{ name: string }>();
    const navigate = useNavigate();
    const { showToast } = useToast();

    const [dataset, setDataset] = useState<Dataset | null>(null);
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingJobs, setLoadingJobs] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [classManagerDataset, setClassManagerDataset] = useState<Dataset | null>(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [showAllHistory, setShowAllHistory] = useState(false);
    const [selectedJob, setSelectedJob] = useState<Job | null>(null);

    const loadDataset = useCallback(async () => {
        if (!name) return;
        try {
            setLoading(true);
            setError(null);
            const data = await api.getDataset(name);
            setDataset(data);
        } catch (err: any) {
            setError(err.message || 'Failed to load dataset');
        } finally {
            setLoading(false);
        }
    }, [name]);

    const loadJobs = useCallback(async () => {
        if (!dataset) return;
        setLoadingJobs(true);
        try {
            const allJobs = await api.listJobs();
            const datasetJobs = allJobs.filter(j => j.dataset_name === dataset.name);
            setJobs(datasetJobs);
        } catch (err) {
            console.error('Failed to load jobs:', err);
        } finally {
            setLoadingJobs(false);
        }
    }, [dataset?.name]);

    useEffect(() => {
        if (dataset) loadJobs();
    }, [dataset?.name, loadJobs]);

    useEffect(() => {
        loadDataset();
    }, [loadDataset]);

    const handleStartAnnotation = async () => {
        if (!dataset) return;
        try {
            const job = await api.createJob({
                dataset_name: dataset.name,
                auto_start: true
            });
            showToast('Annotation job started', 'success');
            navigate(`/datasets/${dataset.name}/annotate?job_id=${job.job_id}`);
        } catch (err: any) {
            showToast(err.message || 'Failed to start annotation', 'error');
        }
    };

    const handleContinueJob = (jobId: string) => {
        navigate(`/datasets/${dataset?.name}/annotate?job_id=${jobId}`);
    };

    const handlePauseJob = async (jobId: string) => {
        try {
            await api.pauseJob(jobId);
            showToast('Job paused', 'success');
            loadJobs();
        } catch (err: any) {
            showToast(err.message || 'Failed to pause job', 'error');
        }
    };

    const handleResumeJob = async (jobId: string) => {
        try {
            await api.startJob(jobId);
            showToast('Job resumed', 'success');
            loadJobs();
        } catch (err: any) {
            showToast(err.message || 'Failed to resume job', 'error');
        }
    };

    const handleClassUpdate = useCallback(() => {
        loadDataset();
    }, [loadDataset]);

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

    if (loading) return <Loading message="Loading dataset..." />;
    if (error || !dataset) return <ErrorMessage message={error || 'Dataset not found'} />;

    const activeJobs = jobs.filter(j => ['pending', 'running', 'paused'].includes(j.status));
    const completedJobs = jobs.filter(j => ['completed', 'failed', 'cancelled'].includes(j.status));
    const historyToShow = showAllHistory ? completedJobs : completedJobs.slice(0, 5);
    const hasMoreHistory = completedJobs.length > 5;

    return (
        <div className="dataset-viewer">
            {/* Header */}
            <div className="dataset-header">
                <button className="btn btn--ghost" onClick={() => navigate('/datasets')}>
                    <ArrowLeft size={18} />
                    Back to Datasets
                </button>

                <div className="dataset-header__title">
                    <h1>{dataset.name}</h1>
                    <div className="dataset-header__actions">
                        <button className="btn btn--secondary" onClick={() => setClassManagerDataset(dataset)}>
                            <Settings size={18} />
                            Manage Classes
                        </button>
                        <button className="btn btn--danger" onClick={() => setShowDeleteModal(true)}>
                            <Trash2 size={18} />
                            Delete
                        </button>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-label">Total Images</div>
                    <div className="stat-value">{dataset?.images?.toLocaleString()}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Classes</div>
                    <div className="stat-value">{dataset.classes?.length || 0}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Size</div>
                    <div className="stat-value">{dataset.size_formatted}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Number of jobs</div>
                    <div className="stat-value">{activeJobs.length + completedJobs.length}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Created</div>
                    <div className="stat-value">{dataset.created ? new Date(dataset.created).toLocaleDateString() : '-'}</div>
                </div>
            </div>

            {/* Classes Section */}
            <div className="dataset-section">
                <div className="section-header">
                    <h3>Classes</h3>
                    <button className="btn btn--sm btn--secondary" onClick={() => setClassManagerDataset(dataset)}>
                        <Settings size={16} />
                        Manage
                    </button>
                </div>
                {dataset.classes && dataset.classes.length > 0 ? (
                    <div className="classes-list">
                        {dataset.classes.map((cls, idx) => (
                            <span key={idx} className="class-badge">{cls}</span>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>No classes defined yet</p>
                        <button className="btn btn--sm btn--primary" onClick={() => setClassManagerDataset(dataset)}>
                            Add Classes
                        </button>
                    </div>
                )}
            </div>

            {/* Annotation Jobs Section */}
            <div className="dataset-section">
                <div className="section-header">
                    <h3>Annotation Jobs</h3>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button className="btn btn--xs btn--secondary" onClick={loadJobs} disabled={loadingJobs}>
                            <RefreshCw size={14} className={loadingJobs ? 'spinner' : ''} />
                            Refresh
                        </button>
                        <button className="btn btn--sm btn--primary" onClick={handleStartAnnotation}>
                            <Play size={16} />
                            Start Annotation
                        </button>
                    </div>
                </div>

                {loadingJobs ? (
                    <div className="loading-jobs">
                        <RefreshCw size={18} className="spinner" />
                        Loading jobs...
                    </div>
                ) : jobs.length === 0 ? (
                    <div className="empty-state">
                        <p>No annotation jobs yet</p>
                        <p className="empty-state__hint">Start annotating to create your first job</p>
                    </div>
                ) : (
                    <div className="jobs-list">
                        {/* Active Jobs */}
                        {activeJobs.length > 0 && (
                            <>
                                <h4>Active Jobs</h4>
                                {activeJobs.map(job => (
                                    <div key={job.job_id} className="job-card active" onClick={() => setSelectedJob(job)}>
                                        <div className="job-header">
                                            <span className={`status-badge status-${job.status}`}>{job.status}</span>
                                            <span className="job-id">{job.job_id}</span>
                                        </div>
                                        <div className="job-progress">
                                            <div className="progress-bar">
                                                <div
                                                    className="progress-fill"
                                                    style={{ width: `${(job.completed_tasks / job.total_tasks) * 100}%` }}
                                                />
                                            </div>
                                            <span className="progress-text">{job.completed_tasks} / {job.total_tasks}</span>
                                        </div>
                                        <div className="job-meta">
                                            <span className="job-time">Started {new Date(job.created_at).toLocaleString()}</span>
                                        </div>
                                        <div className="job-actions" onClick={(e) => e.stopPropagation()}>
                                            {job.status === 'running' && (
                                                <button className="btn btn--xs btn--primary" onClick={() => handleContinueJob(job.job_id)}>
                                                    Continue
                                                </button>
                                            )}
                                            {job.status === 'paused' && (
                                                <>
                                                    <button className="btn btn--xs btn--primary" onClick={() => handleResumeJob(job.job_id)}>
                                                        <Play size={14} />
                                                        Resume
                                                    </button>
                                                    <button className="btn btn--xs btn--secondary" onClick={() => handleContinueJob(job.job_id)}>
                                                        View
                                                    </button>
                                                </>
                                            )}
                                            {job.status === 'pending' && (
                                                <button className="btn btn--xs btn--primary" onClick={() => handleResumeJob(job.job_id)}>
                                                    <Play size={14} />
                                                    Start
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </>
                        )}

                        {/* Job History */}
                        {completedJobs.length > 0 && (
                            <>
                                <h4 style={{ marginTop: activeJobs.length > 0 ? 'var(--spacing-xl)' : 0 }}>History</h4>
                                {historyToShow.map(job => (
                                    <div key={job.job_id} className="job-card history" onClick={() => setSelectedJob(job)}>
                                        <div className="job-header">
                                            <span className={`status-badge status-${job.status}`}>{job.status}</span>
                                            <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                                <span className='job-id'>{job.job_id}</span>
                                                <span className="job-time">{new Date(job.created_at).toLocaleDateString()}</span>
                                            </div>
                                        </div>
                                        <div className="job-summary">
                                            {job.completed_tasks} / {job.total_tasks} completed
                                            {job.failed_tasks > 0 && ` (${job.failed_tasks} failed)`}
                                        </div>
                                    </div>
                                ))}
                                {hasMoreHistory && (
                                    <button className="jobs-more-button" onClick={() => setShowAllHistory(!showAllHistory)}>
                                        {showAllHistory ? '− Show less' : `+ ${completedJobs.length - 5} more completed job(s)`}
                                    </button>
                                )}
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Modals */}
            {classManagerDataset && (
                <ClassManagerModal
                    isOpen={true}
                    onClose={() => setClassManagerDataset(null)}
                    datasetId={classManagerDataset.name}
                    initialClasses={classManagerDataset.classes || []}
                    onUpdate={handleClassUpdate}
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