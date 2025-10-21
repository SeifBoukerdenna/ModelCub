import { useState } from 'react';
import { Settings, ChevronDown, ChevronRight } from 'lucide-react';
import type { Job, Task } from '@/lib/api/types';
import { getClassColor } from '@/lib/canvas/coordinates';

interface AnnotationSidebarProps {
    classes: Array<{ id: number; name: string }>;
    currentTask: Task | null;
    job: Job | null;
    completedCount: number;
    currentClassId: number;
    onClassSelect: (classId: number) => void;
    onComplete: () => void;
}

export const AnnotationSidebar = ({
    classes,
    currentTask,
    job,
    completedCount,
    currentClassId,
    onClassSelect,
    onComplete,
}: AnnotationSidebarProps) => {
    const [showTaskInfo, setShowTaskInfo] = useState(false);
    const [showShortcuts, setShowShortcuts] = useState(false);

    return (
        <div className="annotation-sidebar-compact">
            {/* Class Selector - Always visible */}
            <div className="sidebar-section" style={{ padding: 'var(--spacing-lg)' }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-md)'
                }}>
                    <h3 style={{ fontSize: '13px', margin: 0, textTransform: 'none', letterSpacing: 0 }}>
                        Classes
                    </h3>
                </div>

                {classes.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {classes.map((cls, index) => {
                            const color = getClassColor(cls.id);
                            const isActive = currentClassId === cls.id;
                            const shortcut = index < 9 ? index + 1 : null;

                            return (
                                <button
                                    key={cls.id}
                                    onClick={() => onClassSelect(cls.id)}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        padding: '10px 12px',
                                        background: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                        border: `2px solid ${isActive ? color : 'var(--color-border)'}`,
                                        borderRadius: '6px',
                                        cursor: 'pointer',
                                        transition: 'all 0.15s',
                                        textAlign: 'left',
                                        width: '100%',
                                    }}
                                >
                                    <div style={{
                                        width: '20px',
                                        height: '20px',
                                        borderRadius: '4px',
                                        background: color,
                                        flexShrink: 0,
                                    }} />
                                    <span style={{
                                        flex: 1,
                                        fontSize: '14px',
                                        fontWeight: isActive ? 600 : 400,
                                        color: 'var(--color-text-primary)',
                                    }}>
                                        {cls.name}
                                    </span>
                                    {shortcut && (
                                        <kbd style={{
                                            padding: '2px 8px',
                                            background: 'var(--color-surface)',
                                            border: '1px solid var(--color-border)',
                                            borderRadius: '4px',
                                            fontSize: '12px',
                                            fontFamily: 'monospace',
                                            color: 'var(--color-text-secondary)',
                                        }}>
                                            {shortcut}
                                        </kbd>
                                    )}
                                </button>
                            );
                        })}
                    </div>
                ) : (
                    <p style={{ fontSize: '13px', color: 'var(--color-text-secondary)', margin: 0 }}>
                        No classes. Click <Settings size={12} style={{ display: 'inline' }} /> to add.
                    </p>
                )}
            </div>

            {/* Task Info - Collapsible */}
            <div className="sidebar-section" style={{ padding: 'var(--spacing-md) var(--spacing-lg)', borderTop: '1px solid var(--color-border)' }}>
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
                    <div style={{ marginTop: 'var(--spacing-sm)', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Select class</span>
                            <kbd style={{ fontSize: '11px' }}>1-9</kbd>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Draw / Edit</span>
                            <span><kbd style={{ fontSize: '11px' }}>R</kbd> / <kbd style={{ fontSize: '11px' }}>E</kbd></span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Delete box</span>
                            <kbd style={{ fontSize: '11px' }}>Del</kbd>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-secondary)' }}>Next image</span>
                            <span><kbd style={{ fontSize: '11px' }}>→</kbd> / <kbd style={{ fontSize: '11px' }}>D</kbd></span>
                        </div>
                    </div>
                )}
            </div>

            {/* Complete Button - Fixed at bottom */}
            <div style={{
                marginTop: 'auto',
                padding: 'var(--spacing-lg)',
                borderTop: '1px solid var(--color-border)',
            }}>
                <button
                    className="btn btn--primary"
                    onClick={onComplete}
                    style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '14px',
                        fontWeight: 600,
                    }}
                >
                    Complete (Space)
                </button>
            </div>
        </div>
    );
};