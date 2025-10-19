import { Settings } from 'lucide-react';
import type { Job, Task } from '@/lib/api/types';
import { getClassColor } from '@/lib/canvas/coordinates';

interface AnnotationSidebarProps {
    classes: Array<{ id: number; name: string }>;
    currentTask: Task | null;
    job: Job | null;
    completedCount: number;
    currentClassId: number;
    onClassSelect: (classId: number) => void;
    onManageClasses: () => void;
}

export const AnnotationSidebar = ({
    classes,
    currentTask,
    job,
    completedCount,
    currentClassId,
    onClassSelect,
    onManageClasses,
}: AnnotationSidebarProps) => {
    return (
        <div className="annotation-sidebar-compact">
            {/* Class Selector */}
            <div className="sidebar-section">
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-sm)'
                }}>
                    <h3>Select Class ({classes.length})</h3>
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
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 'var(--spacing-xs)'
                    }}>
                        {classes.map((cls, index) => {
                            const shortcutKey = index + 1;
                            const showShortcut = shortcutKey <= 9;
                            const color = getClassColor(cls.id);

                            return (
                                <label
                                    key={cls.id}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 'var(--spacing-sm)',
                                        padding: 'var(--spacing-sm)',
                                        background: currentClassId === cls.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                        border: `2px solid ${currentClassId === cls.id ? color : 'var(--color-border)'}`,
                                        borderRadius: 'var(--border-radius-sm)',
                                        cursor: 'pointer',
                                        transition: 'all 0.2s',
                                    }}
                                >
                                    <input
                                        type="radio"
                                        name="class-selector"
                                        checked={currentClassId === cls.id}
                                        onChange={() => onClassSelect(cls.id)}
                                        style={{ cursor: 'pointer' }}
                                    />
                                    {/* Color indicator */}
                                    <div style={{
                                        width: '16px',
                                        height: '16px',
                                        borderRadius: '3px',
                                        background: color,
                                        flexShrink: 0,
                                    }} />
                                    <span style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        minWidth: '24px',
                                        height: '24px',
                                        background: 'var(--color-surface)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        fontSize: 'var(--font-size-xs)',
                                        fontWeight: 600,
                                        flexShrink: 0,
                                    }}>
                                        {cls.id}
                                    </span>
                                    <span style={{
                                        flex: 1,
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: currentClassId === cls.id ? 600 : 400,
                                    }}>
                                        {cls.name}
                                    </span>
                                    {showShortcut && (
                                        <kbd style={{
                                            padding: '2px 6px',
                                            background: 'var(--color-surface)',
                                            border: '1px solid var(--color-border)',
                                            borderRadius: '3px',
                                            fontSize: '11px',
                                            fontFamily: 'monospace',
                                            color: 'var(--color-text-secondary)',
                                        }}>
                                            {shortcutKey}
                                        </kbd>
                                    )}
                                </label>
                            );
                        })}
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
                        <kbd>1-9</kbd>
                        <span>Select class</span>
                    </div>
                    <div className="shortcut-item">
                        <kbd>R</kbd>
                        <span>Draw tool</span>
                    </div>
                    <div className="shortcut-item">
                        <kbd>E</kbd>
                        <span>Edit tool</span>
                    </div>
                    <div className="shortcut-item">
                        <kbd>Del</kbd>
                        <span>Delete selected box</span>
                    </div>
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
                            <kbd>Ctrl</kbd>+<kbd>Z</kbd>
                        </div>
                        <span>Undo</span>
                    </div>
                    <div className="shortcut-item">
                        <div>
                            <kbd>Ctrl</kbd>+<kbd>Y</kbd>
                        </div>
                        <span>Redo</span>
                    </div>
                </div>
            </div>
        </div>
    );
};