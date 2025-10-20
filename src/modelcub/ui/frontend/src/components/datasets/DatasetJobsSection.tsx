import { Play, Eye } from 'lucide-react';
import type { Job } from '@/lib/api/types';

interface DatasetJobsSectionProps {
    activeJobs: Job[];
    completedJobs: Job[];
    loading: boolean;
    onStartAnnotation: () => void;
    onContinueJob: (jobId: string) => void;
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
    return (
        <div className="dataset-section">
            <div className="section-header">
                <h2>Annotation Jobs</h2>
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    <button className="btn btn--xs btn--secondary" onClick={onRefresh}>
                        🔄 Refresh
                    </button>
                    <button className="btn btn--xs btn--primary" onClick={onStartAnnotation}>
                        ▶ Start Annotation
                    </button>
                </div>
            </div>

            <div className="section-body">
                {loading ? (
                    <p>Loading jobs...</p>
                ) : (
                    <>
                        {/* Active Jobs */}
                        {activeJobs.length > 0 && (
                            <>
                                <h3 style={{ marginBottom: 'var(--spacing-sm)' }}>Active Jobs</h3>
                                <div className="jobs-list">
                                    {activeJobs.map(job => (
                                        <JobCard
                                            key={job.job_id}
                                            job={job}
                                            onContinue={onContinueJob}
                                            onResume={onResumeJob}
                                            onClick={onJobClick}
                                        />
                                    ))}
                                </div>
                            </>
                        )}

                        {/* Completed Jobs */}
                        {completedJobs.length > 0 && (
                            <>
                                <h3 style={{ marginTop: 'var(--spacing-lg)', marginBottom: 'var(--spacing-sm)' }}>
                                    History
                                </h3>
                                <div className="jobs-list">
                                    {completedJobs.slice(0, 5).map(job => (
                                        <JobCard
                                            key={job.job_id}
                                            job={job}
                                            onContinue={onContinueJob}
                                            onClick={onJobClick}
                                        />
                                    ))}
                                </div>
                                {completedJobs.length > 5 && (
                                    <p className="jobs-more">
                                        + {completedJobs.length - 5} more completed jobs
                                    </p>
                                )}
                            </>
                        )}

                        {activeJobs.length === 0 && completedJobs.length === 0 && (
                            <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                                No annotation jobs yet. Click "Start Annotation" to begin.
                            </p>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

interface JobCardProps {
    job: Job;
    onContinue?: (jobId: string) => void;
    onResume?: (jobId: string) => void;
    onClick: (job: Job) => void;
}

const JobCard = ({ job, onContinue, onResume, onClick }: JobCardProps) => {
    const completionPercentage = Math.round((job.completed_tasks / job.total_tasks) * 100);

    // Active job card
    if (job.status === 'running' || job.status === 'paused' || job.status === 'pending') {
        return (
            <div className="job-card active" onClick={() => onClick(job)}>
                <div className="job-header">
                    <span className={`status-badge status-${job.status}`}>{job.status}</span>
                    <span className='job-id'>{job.job_id}</span>
                </div>
                <div className="job-meta">
                    <span className="job-time">Started {new Date(job.created_at).toLocaleDateString()}</span>
                </div>
                <div className="progress-container">
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${completionPercentage}%` }} />
                    </div>
                    <span className="progress-text">{job.completed_tasks} / {job.total_tasks}</span>
                </div>
                <div className="job-actions">
                    {(job.status === 'running' || job.status === 'paused') && onContinue && (
                        <button
                            className="btn btn--xs btn--primary"
                            onClick={() => onContinue(job.job_id)}
                        >
                            Continue
                        </button>
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

    // Completed/Failed job card
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
            {onContinue && (
                <div className="job-actions" style={{ marginTop: 'var(--spacing-sm)' }}>
                    <button
                        className="btn btn--xs btn--secondary"
                        onClick={(e) => {
                            e.stopPropagation();
                            onContinue(job.job_id);
                        }}
                    >
                        <Eye size={14} />
                        View
                    </button>
                </div>
            )}
        </div>
    );
};