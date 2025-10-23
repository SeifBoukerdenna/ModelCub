import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { Job, Task } from '@/lib/api/types';

interface AnnotationSidebarProps {
    job: Job | null;
    currentTask: Task | null;
    completedCount: number;
    classes: Array<{ id: number; name: string; color?: string }>;
    currentClassId: number;
    onClassChange: (classId: number) => void;
    onNext: () => void;
    onPrevious: () => void;
    onComplete: () => void;
    onMarkNull?: () => void;  // NEW: Null marking handler
}

export const AnnotationSidebar = ({
    job,
    currentTask,
    completedCount,
    classes,
    currentClassId,
    onClassChange,
    onNext,
    onPrevious,
    onComplete,
    onMarkNull,
}: AnnotationSidebarProps) => {
    const [showClasses, setShowClasses] = useState(true);
    const [showTaskInfo, setShowTaskInfo] = useState(true);
    const [showShortcuts, setShowShortcuts] = useState(true);

    return (
        <div className="annotation-sidebar-compact">
            {/* Navigation controls */}
            <div style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderBottom: '1px solid var(--color-border)' }}>
                <div className="nav-controls" style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                    <button
                        onClick={onPrevious}
                        className="btn btn--secondary"
                        style={{ flex: 1 }}
                    >
                        ← Previous
                    </button>
                    <button
                        onClick={onNext}
                        className="btn btn--secondary"
                        style={{ flex: 1 }}
                    >
                        Next →
                    </button>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={onComplete}
                        className="btn btn--primary"
                        style={{ flex: 1 }}
                    >
                        ✓ Complete
                    </button>
                    {onMarkNull && (
                        <button
                            onClick={onMarkNull}
                            className="btn"
                            style={{
                                flex: 1,
                                background: 'var(--color-warning)',
                                border: 'none',
                                color: 'white',
                            }}
                            title="Mark as null (negative example)"
                        >
                            ⚠️ Null
                        </button>
                    )}
                </div>
            </div>

            {/* Classes - Collapsible */}
            <div className="sidebar-section" style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderBottom: '1px solid var(--color-border)' }}>
                <button
                    onClick={() => setShowClasses(!showClasses)}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        color: 'var(--color-text-secondary)',
                        fontSize: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        marginBottom: showClasses ? '12px' : 0,
                        width: '100%',
                    }}
                >
                    {showClasses ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    Classes ({classes.length})
                </button>

                {showClasses && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {classes.map((cls) => (
                            <button
                                key={cls.id}
                                onClick={() => onClassChange(cls.id)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    padding: '8px 12px',
                                    background: currentClassId === cls.id ? 'var(--color-primary-alpha)' : 'var(--color-background)',
                                    border: `2px solid ${currentClassId === cls.id ? 'var(--color-primary)' : 'var(--color-border)'}`,
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '13px',
                                    textAlign: 'left',
                                    transition: 'all 0.15s ease',
                                }}
                            >
                                <div
                                    style={{
                                        width: '12px',
                                        height: '12px',
                                        borderRadius: '2px',
                                        background: cls.color || `hsl(${cls.id * 137.5}, 70%, 60%)`,
                                    }}
                                />
                                <span style={{ flex: 1 }}>{cls.name}</span>
                                <kbd style={{
                                    padding: '2px 6px',
                                    background: 'var(--color-background)',
                                    border: '1px solid var(--color-border)',
                                    borderRadius: '3px',
                                    fontSize: '11px',
                                    fontFamily: 'var(--font-mono)',
                                }}>
                                    {cls.id}
                                </kbd>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Task Info - Collapsible */}
            <div className="sidebar-section" style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderBottom: '1px solid var(--color-border)' }}>
                <button
                    onClick={() => setShowTaskInfo(!showTaskInfo)}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        color: 'var(--color-text-secondary)',
                        fontSize: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        width: '100%',
                    }}
                >
                    {showTaskInfo ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    Task Info
                </button>

                {showTaskInfo && (
                    <div style={{ marginTop: 'var(--spacing-sm)', fontSize: '13px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Image</span>
                            <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                                {currentTask?.image_id || '-'}
                            </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Progress</span>
                            <span>{completedCount} / {job?.total_tasks || 0}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Shortcuts - Collapsible */}
            <div className="sidebar-section" style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderTop: '1px solid var(--color-border)' }}>
                <button
                    onClick={() => setShowShortcuts(!showShortcuts)}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        color: 'var(--color-text-secondary)',
                        fontSize: '12px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        width: '100%',
                    }}
                >
                    {showShortcuts ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    Shortcuts
                </button>

                {showShortcuts && (
                    <div style={{ marginTop: 'var(--spacing-sm)' }}>
                        <div className="shortcuts-list">
                            <div className="shortcut-item">
                                <span>Next image</span>
                                <kbd>D / →</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Previous image</span>
                                <kbd>A / ←</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Complete task</span>
                                <kbd>Space</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span style={{ fontWeight: 600, color: 'var(--color-warning)' }}>Mark as null</span>
                                <kbd>N</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Delete box</span>
                                <kbd>Del</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Save</span>
                                <kbd>Ctrl+S</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Undo</span>
                                <kbd>Ctrl+Z</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Redo</span>
                                <kbd>Ctrl+Y</kbd>
                            </div>
                            <div className="shortcut-item">
                                <span>Exit</span>
                                <kbd>Esc</kbd>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};