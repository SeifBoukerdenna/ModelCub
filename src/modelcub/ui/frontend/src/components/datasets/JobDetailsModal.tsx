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

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ maxWidth: '700px' }} onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <h2 className="modal__title">Job Details</h2>
                    <button className="modal__close" onClick={onClose} aria-label="Close">
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="modal__body">
                    {/* Overview */}
                    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                        <label className="form-label">Overview</label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-md)' }}>
                            <div>
                                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                    JOB ID
                                </span>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>
                                    {job.job_id}
                                </span>
                            </div>
                            <div>
                                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                    DATASET
                                </span>
                                <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>
                                    {job.dataset_name}
                                </span>
                            </div>
                            <div>
                                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                    STATUS
                                </span>
                                <span className={`status-badge status-${job.status}`}>
                                    {job.status}
                                </span>
                            </div>
                            <div>
                                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                    DURATION
                                </span>
                                <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>
                                    {formatDuration(duration)}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Progress */}
                    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                        <label className="form-label">Progress</label>
                        <div style={{ display: 'flex', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-md)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                                <CheckCircle size={16} style={{ color: 'var(--color-success)' }} />
                                <span>{completedTasks.length} Completed</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                                <Clock size={16} style={{ color: 'var(--color-text-secondary)' }} />
                                <span>{pendingTasks.length} Pending</span>
                            </div>
                            {failedTasks.length > 0 && (
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                                    <XCircle size={16} style={{ color: 'var(--color-error)' }} />
                                    <span>{failedTasks.length} Failed</span>
                                </div>
                            )}
                        </div>
                        <div style={{ height: '16px', background: 'var(--color-background)', border: '1px solid var(--color-border)', borderRadius: 'var(--border-radius-full)', overflow: 'hidden', marginBottom: 'var(--spacing-sm)' }}>
                            <div
                                style={{
                                    height: '100%',
                                    background: 'var(--color-primary)',
                                    width: `${(job.completed_tasks / job.total_tasks) * 100}%`,
                                    transition: 'width 0.3s ease'
                                }}
                            />
                        </div>
                        <div style={{ textAlign: 'center', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                            {job.completed_tasks} / {job.total_tasks} tasks
                            ({Math.round((job.completed_tasks / job.total_tasks) * 100)}%)
                        </div>
                    </div>

                    {/* Timestamps */}
                    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                        <label className="form-label">Timestamps</label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-md)' }}>
                            <div>
                                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                    CREATED
                                </span>
                                <span style={{ fontSize: 'var(--font-size-sm)' }}>
                                    {new Date(job.created_at).toLocaleString()}
                                </span>
                            </div>
                            {job.started_at && (
                                <div>
                                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                        STARTED
                                    </span>
                                    <span style={{ fontSize: 'var(--font-size-sm)' }}>
                                        {new Date(job.started_at).toLocaleString()}
                                    </span>
                                </div>
                            )}
                            {job.completed_at && (
                                <div>
                                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', display: 'block', marginBottom: 'var(--spacing-xs)' }}>
                                        COMPLETED
                                    </span>
                                    <span style={{ fontSize: 'var(--font-size-sm)' }}>
                                        {new Date(job.completed_at).toLocaleString()}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Tasks */}
                    <div>
                        <label className="form-label">Tasks ({tasks.length})</label>
                        {loading ? (
                            <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 'var(--spacing-lg)' }}>
                                Loading tasks...
                            </p>
                        ) : (
                            <div style={{ maxHeight: '300px', overflowY: 'auto', border: '1px solid var(--color-border)', borderRadius: 'var(--border-radius-md)', background: 'var(--color-background)' }}>
                                {tasks.slice(0, 20).map(task => (
                                    <div
                                        key={task.task_id}
                                        style={{
                                            display: 'grid',
                                            gridTemplateColumns: '24px 140px 1fr',
                                            alignItems: 'center',
                                            gap: 'var(--spacing-sm)',
                                            padding: 'var(--spacing-sm) var(--spacing-md)',
                                            borderBottom: '1px solid var(--color-border)',
                                            fontSize: 'var(--font-size-sm)'
                                        }}
                                    >
                                        <div>
                                            {task.status === 'completed' && <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />}
                                            {task.status === 'failed' && <XCircle size={14} style={{ color: 'var(--color-error)' }} />}
                                            {task.status === 'pending' && <Clock size={14} style={{ color: 'var(--color-text-secondary)' }} />}
                                            {task.status === 'in_progress' && <AlertCircle size={14} style={{ color: 'var(--color-warning)' }} />}
                                        </div>
                                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>
                                            {task.image_id}
                                        </span>
                                        <span style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-xs)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
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