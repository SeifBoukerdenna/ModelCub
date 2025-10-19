import { useState } from 'react';
import { Play, RefreshCw } from 'lucide-react';
import type { Job } from '@/lib/api/types';

interface DatasetJobsSectionProps {
    activeJobs: Job[];
    completedJobs: Job[];
    loading: boolean;
    onStartAnnotation: () => void;
    onContinueJob: (jobId: string) => void;
    onPauseJob: (jobId: string) => void;
    onResumeJob: (jobId: string) => void;
    onRefresh: () => void;
    onJobClick: (job: Job) => void;
}

export const DatasetJobsSection = ({
    activeJobs,
    completedJobs,
    loading,
    onStartAnnotation,
    onContinueJob,
    onResumeJob,
    onRefresh,
    onJobClick,
}: DatasetJobsSectionProps) => {
    const [showAllHistory, setShowAllHistory] = useState(false);
    const historyToShow = showAllHistory ? completedJobs : completedJobs.slice(0, 5);
    const hasMoreHistory = completedJobs.length > 5;
    const totalJobs = activeJobs.length + completedJobs.length;

    return (
        <div className="dataset-section">
            <div className="section-header">
                <h3>Annotation Jobs</h3>
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    <button
                        className="btn btn--xs btn--secondary"
                        onClick={onRefresh}
                        disabled={loading}
                    >
                        <RefreshCw size={14} className={loading ? 'spinner' : ''} />
                        Refresh
                    </button>
                    <button className="btn btn--sm btn--primary" onClick={onStartAnnotation}>
                        <Play size={16} />
                        Start Annotation
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="loading-jobs">
                    <RefreshCw size={18} className="spinner" />
                    Loading jobs...
                </div>
            ) : totalJobs === 0 ? (
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
                                <JobCard
                                    key={job.job_id}
                                    job={job}
                                    type="active"
                                    onContinue={onContinueJob}
                                    onResume={onResumeJob}
                                    onClick={onJobClick}
                                />
                            ))}
                        </>
                    )}

                    {/* Job History */}
                    {completedJobs.length > 0 && (
                        <>
                            <h4 style={{ marginTop: activeJobs.length > 0 ? 'var(--spacing-xl)' : 0 }}>
                                History
                            </h4>
                            {historyToShow.map(job => (
                                <JobCard
                                    key={job.job_id}
                                    job={job}
                                    type="history"
                                    onClick={onJobClick}
                                />
                            ))}
                            {hasMoreHistory && (
                                <button
                                    className="jobs-more-button"
                                    onClick={() => setShowAllHistory(!showAllHistory)}
                                >
                                    {showAllHistory
                                        ? '− Show less'
                                        : `+ ${completedJobs.length - 5} more completed job(s)`}
                                </button>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

// Job Card Component
interface JobCardProps {
    job: Job;
    type: 'active' | 'history';
    onContinue?: (jobId: string) => void;
    onResume?: (jobId: string) => void;
    onClick: (job: Job) => void;
}

const JobCard = ({ job, type, onContinue, onResume, onClick }: JobCardProps) => {
    if (type === 'active') {
        return (
            <div className="job-card active" onClick={() => onClick(job)}>
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
                    <span className="progress-text">
                        {job.completed_tasks} / {job.total_tasks}
                    </span>
                </div>
                <div className="job-meta">
                    <span className="job-time">
                        Started {new Date(job.created_at).toLocaleString()}
                    </span>
                </div>
                <div className="job-actions" onClick={(e) => e.stopPropagation()}>
                    {job.status === 'running' && onContinue && (
                        <button
                            className="btn btn--xs btn--primary"
                            onClick={() => onContinue(job.job_id)}
                        >
                            Continue
                        </button>
                    )}
                    {job.status === 'paused' && (
                        <>
                            {onResume && (
                                <button
                                    className="btn btn--xs btn--primary"
                                    onClick={() => onResume(job.job_id)}
                                >
                                    <Play size={14} />
                                    Resume
                                </button>
                            )}
                            {onContinue && (
                                <button
                                    className="btn btn--xs btn--secondary"
                                    onClick={() => onContinue(job.job_id)}
                                >
                                    View
                                </button>
                            )}
                        </>
                    )}
                    {job.status === 'pending' && onResume && (
                        <button
                            className="btn btn--xs btn--primary"
                            onClick={() => onResume(job.job_id)}
                        >
                            <Play size={14} />
                            Start
                        </button>
                    )}
                </div>
            </div>
        );
    }

    // History card
    return (
        <div className="job-card history" onClick={() => onClick(job)}>
            <div className="job-header">
                <span className={`status-badge status-${job.status}`}>{job.status}</span>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className='job-id'>{job.job_id}</span>
                    <span className="job-time">
                        {new Date(job.created_at).toLocaleDateString()}
                    </span>
                </div>
            </div>
            <div className="job-summary">
                {job.completed_tasks} / {job.total_tasks} completed
                {job.failed_tasks > 0 && ` (${job.failed_tasks} failed)`}
            </div>
        </div>
    );
};