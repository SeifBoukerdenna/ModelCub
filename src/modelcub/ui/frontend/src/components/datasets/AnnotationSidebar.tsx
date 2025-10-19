import { Settings } from 'lucide-react';
import type { Job, Task } from '@/lib/api/types';

interface AnnotationSidebarProps {
    classes: Array<{ id: number; name: string }>;
    currentTask: Task | null;
    job: Job | null;
    completedCount: number;
    onManageClasses: () => void;
}

export const AnnotationSidebar = ({
    classes,
    currentTask,
    job,
    completedCount,
    onManageClasses,
}: AnnotationSidebarProps) => {
    return (
        <div className="annotation-sidebar-compact">
            {/* Classes */}
            <div className="sidebar-section">
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-sm)'
                }}>
                    <h3>Classes ({classes.length})</h3>
                    <button
                        className="btn btn--xs btn--secondary"
                        onClick={onManageClasses}
                        title="Manage classes"
                        style={{ padding: '4px 8px', fontSize: 'var(--font-size-xs)' }}
                    >
                        <Settings size={12} />
                        Edit
                    </button>
                </div>
                {classes.length > 0 ? (
                    <div className="classes-list" style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 'var(--spacing-xs)'
                    }}>
                        {classes.map((cls) => (
                            <span
                                key={cls.id}
                                className="class-tag"
                                style={{
                                    padding: '4px 8px',
                                    background: 'var(--color-primary-alpha)',
                                    border: '1px solid var(--color-primary)',
                                    borderRadius: 'var(--border-radius-sm)',
                                    fontSize: 'var(--font-size-xs)',
                                    fontWeight: 500
                                }}
                            >
                                {cls.name}
                            </span>
                        ))}
                    </div>
                ) : (
                    <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                        No classes defined. Click Edit to add.
                    </p>
                )}
            </div>

            {/* Current Task */}
            <div className="sidebar-section">
                <h3>Current Task</h3>
                <div className="info-grid">
                    <div className="info-item">
                        <span className="label">Image</span>
                        <span className="value">{currentTask?.image_id || '-'}</span>
                    </div>
                    <div className="info-item">
                        <span className="label">Status</span>
                        <span className={`value status-badge status-${currentTask?.status || 'pending'}`}>
                            {currentTask?.status?.replace('_', ' ').toUpperCase() || 'PENDING'}
                        </span>
                    </div>
                    <div className="info-item">
                        <span className="label">Path</span>
                        <span className="value mono small" title={currentTask?.image_path || '-'}>
                            {currentTask?.image_path || '-'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Job Info */}
            <div className="sidebar-section">
                <h3>Job Info</h3>
                {job && (
                    <div className="info-grid">
                        <div className="info-item">
                            <span className="label">Job ID</span>
                            <span className="value mono small" title={job.job_id}>
                                {job.job_id}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="label">Status</span>
                            <span className={`value status-badge status-${job.status}`}>
                                {job.status.toUpperCase()}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="label">Progress</span>
                            <span className="value">
                                {completedCount} / {job.total_tasks} completed
                            </span>
                        </div>
                        {job.failed_tasks > 0 && (
                            <div className="info-item">
                                <span className="label">Failed</span>
                                <span className="value error">{job.failed_tasks}</span>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Keyboard Shortcuts */}
            <div className="sidebar-section">
                <h3>Keyboard Shortcuts</h3>
                <div className="shortcuts-list">
                    <div className="shortcut-item">
                        <div>
                            <kbd>→</kbd> <kbd>D</kbd>
                        </div>
                        <span>Next image</span>
                    </div>
                    <div className="shortcut-item">
                        <div>
                            <kbd>←</kbd> <kbd>A</kbd>
                        </div>
                        <span>Previous image</span>
                    </div>
                    <div className="shortcut-item">
                        <kbd>ESC</kbd>
                        <span>Exit annotation</span>
                    </div>
                    <div className="shortcut-item">
                        <div>
                            <kbd>Ctrl</kbd>+<kbd>S</kbd>
                        </div>
                        <span>Save (auto-save enabled)</span>
                    </div>
                </div>
            </div>
        </div>
    );
};