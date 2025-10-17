import { X, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import type { Job, Task } from '@/lib/api/types';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface JobDetailsModalProps {
    job: Job;
    onClose: () => void;
}

export const JobDetailsModal = ({ job, onClose }: JobDetailsModalProps) => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadTasks = async () => {
            try {
                const data = await api.getJobTasks(job.job_id);
                setTasks(data);
            } catch (err) {
                console.error('Failed to load tasks:', err);
            } finally {
                setLoading(false);
            }
        };
        loadTasks();
    }, [job.job_id]);

    const completedTasks = tasks.filter(t => t.status === 'completed');
    const failedTasks = tasks.filter(t => t.status === 'failed');
    const pendingTasks = tasks.filter(t => t.status === 'pending');

    const duration = job.completed_at && job.started_at
        ? new Date(job.completed_at).getTime() - new Date(job.started_at).getTime()
        : job.started_at
            ? Date.now() - new Date(job.started_at).getTime()
            : 0;

    const formatDuration = (ms: number) => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    };

    const progressPercentage = (job.completed_tasks / job.total_tasks) * 100;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal job-details-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h2>Job Details</h2>
                    <button className="modal__close" onClick={onClose} aria-label="Close">
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="modal-body">
                    {/* Overview */}
                    <div className="job-details-section">
                        <h3>Overview</h3>
                        <div className="details-grid">
                            <div className="detail-item">
                                <span className="label">Job ID</span>
                                <span className="value" style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-sm)' }}>
                                    {job.job_id}
                                </span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Dataset</span>
                                <span className="value" style={{ fontSize: 'var(--font-size-sm)' }}>
                                    {job.dataset_name}
                                </span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Status</span>
                                <span className={`status-badge status-${job.status}`}>
                                    {job.status}
                                </span>
                            </div>
                            <div className="detail-item">
                                <span className="label">Duration</span>
                                <span className="value" style={{ fontSize: 'var(--font-size-sm)' }}>
                                    {formatDuration(duration)}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Progress */}
                    <div className="job-details-section">
                        <h3>Progress</h3>
                        <div className="progress-stats">
                            <div className="stat">
                                <CheckCircle size={16} style={{ color: 'var(--color-success)' }} />
                                <span>{completedTasks.length} Completed</span>
                            </div>
                            <div className="stat">
                                <Clock size={16} style={{ color: 'var(--color-text-secondary)' }} />
                                <span>{pendingTasks.length} Pending (only counted loaded tasks)</span>
                            </div>
                            {failedTasks.length > 0 && (
                                <div className="stat">
                                    <XCircle size={16} style={{ color: 'var(--color-error)' }} />
                                    <span>{failedTasks.length} Failed</span>
                                </div>
                            )}
                        </div>

                        {/* Enhanced Progress Bar */}
                        <div className="enhanced-progress-container">
                            <div className="progress-bar-enhanced">
                                <div
                                    className="progress-fill-enhanced"
                                    style={{ width: `${progressPercentage}%` }}
                                >
                                    <div className="progress-shimmer"></div>
                                    <div className="progress-glow"></div>
                                </div>
                                <div className="progress-overlay-text">
                                    {job.completed_tasks} / {job.total_tasks} tasks ({Math.round(progressPercentage)}%)
                                </div>
                            </div>

                            {/* Progress Indicator Dots */}
                            <div className="progress-dots">
                                {Array.from({ length: job.total_tasks }).map((_, i) => (
                                    <div
                                        key={i}
                                        className={`progress-dot ${i < job.completed_tasks ? 'completed' : ''}`}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Timestamps */}
                    <div className="job-details-section">
                        <h3>Timestamps</h3>
                        <div className="details-grid">
                            <div className="detail-item">
                                <span className="label">Created</span>
                                <span className="value" style={{ fontSize: 'var(--font-size-sm)' }}>
                                    {new Date(job.created_at).toLocaleString()}
                                </span>
                            </div>
                            {job.started_at && (
                                <div className="detail-item">
                                    <span className="label">Started</span>
                                    <span className="value" style={{ fontSize: 'var(--font-size-sm)' }}>
                                        {new Date(job.started_at).toLocaleString()}
                                    </span>
                                </div>
                            )}
                            {job.completed_at && (
                                <div className="detail-item">
                                    <span className="label">Completed</span>
                                    <span className="value" style={{ fontSize: 'var(--font-size-sm)' }}>
                                        {new Date(job.completed_at).toLocaleString()}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Tasks */}
                    <div className="job-details-section" style={{ borderBottom: 'none', paddingBottom: 0 }}>
                        <h3>Tasks ({tasks.length})</h3>
                        {loading ? (
                            <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 'var(--spacing-lg)' }}>
                                Loading tasks...
                            </p>
                        ) : (
                            <div className="tasks-list">
                                {tasks.slice(0, 20).map(task => (
                                    <div key={task.task_id} className="task-item">
                                        <div>
                                            {task.status === 'completed' && <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />}
                                            {task.status === 'failed' && <XCircle size={14} style={{ color: 'var(--color-error)' }} />}
                                            {task.status === 'pending' && <Clock size={14} style={{ color: 'var(--color-text-secondary)' }} />}
                                            {task.status === 'in_progress' && <AlertCircle size={14} style={{ color: 'var(--color-warning)' }} />}
                                        </div>
                                        <span className="task-name">
                                            {task.image_id}
                                        </span>
                                        <span className="task-path">
                                            {task.image_path}
                                        </span>
                                    </div>
                                ))}
                                {tasks.length > 20 && (
                                    <p style={{ padding: 'var(--spacing-sm)', textAlign: 'center', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
                                        + {tasks.length - 20} more tasks
                                    </p>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="modal__footer">
                    <button className="btn btn--secondary" onClick={onClose}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};