import React, { useState } from 'react';
import { Play, Square, Trash2, Clock, TrendingUp, Database, Zap } from 'lucide-react';
import type { TrainingRun } from '@/lib/api/types';

interface RunCardProps {
    run: TrainingRun;
    onStart?: (run: TrainingRun) => void;
    onStop?: (run: TrainingRun) => void;
    onDelete?: (run: TrainingRun) => void;
}

const RunCard: React.FC<RunCardProps> = ({ run, onStart, onStop, onDelete }) => {
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const getStatusColor = (status: string) => {
        const colors = {
            pending: { bg: '#fef3c7', text: '#92400e', border: '#fbbf24' },
            running: { bg: '#dbeafe', text: '#1e40af', border: '#3b82f6' },
            completed: { bg: '#d1fae5', text: '#065f46', border: '#10b981' },
            failed: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444' },
            cancelled: { bg: '#e5e7eb', text: '#374151', border: '#6b7280' }
        };
        return colors[status as keyof typeof colors] || colors.cancelled;
    };

    const getStatusIcon = (status: string) => {
        const icons = {
            pending: '⏳',
            running: '▶️',
            completed: '✅',
            failed: '❌',
            cancelled: '⚠️'
        };
        return icons[status as keyof typeof icons] || '•';
    };

    const formatDuration = (ms?: number | null) => {
        if (!ms) return 'N/A';
        const seconds = ms / 1000;
        if (seconds < 60) return `${seconds.toFixed(0)}s`;
        if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
        return `${(seconds / 3600).toFixed(1)}h`;
    };

    const formatMetric = (value?: number) => {
        if (value === undefined || value === null) return 'N/A';
        return `${(value * 100).toFixed(1)}%`;
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="card" style={{ position: 'relative' }}>
            {/* Delete Confirmation Overlay */}
            {showDeleteConfirm && (
                <div
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.95)',
                        borderRadius: 'var(--border-radius-md)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-md)',
                        padding: 'var(--spacing-lg)',
                        zIndex: 20,
                    }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <Trash2 size={40} style={{ color: '#ef4444' }} />
                    <div style={{ textAlign: 'center' }}>
                        <h4 style={{
                            fontSize: 'var(--font-size-xl)',
                            fontWeight: 600,
                            marginBottom: 'var(--spacing-xs)',
                            color: 'white'
                        }}>
                            Delete Run?
                        </h4>
                        <p style={{
                            fontSize: 'var(--font-size-sm)',
                            color: '#9ca3af',
                            maxWidth: '300px'
                        }}>
                            This will permanently delete "{run.id}"
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginTop: 'var(--spacing-sm)' }}>
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(false); }}
                            style={{
                                padding: 'var(--spacing-sm) var(--spacing-lg)',
                                backgroundColor: '#374151',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); onDelete?.(run); setShowDeleteConfirm(false); }}
                            style={{
                                padding: 'var(--spacing-sm) var(--spacing-lg)',
                                backgroundColor: '#ef4444',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 600,
                            }}
                        >
                            Delete
                        </button>
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="card__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
                        <span style={{ fontSize: 'var(--font-size-lg)' }}>{getStatusIcon(run.status)}</span>
                        <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, margin: 0 }}>
                            {run.id}
                        </h3>
                    </div>
                    <div style={{
                        display: 'inline-block',
                        fontSize: 'var(--font-size-xs)',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        backgroundColor: getStatusColor(run.status).bg,
                        color: getStatusColor(run.status).text,
                        border: `1px solid ${getStatusColor(run.status).border}`,
                        fontWeight: 600,
                        letterSpacing: '0.5px'
                    }}>
                        {run.status.toUpperCase()}
                    </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                    {run.status === 'pending' && onStart && (
                        <button
                            onClick={(e) => { e.stopPropagation(); onStart(run); }}
                            title="Start training"
                            style={{
                                padding: '8px',
                                backgroundColor: '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'all 150ms',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#059669'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
                        >
                            <Play size={16} />
                        </button>
                    )}
                    {run.status === 'running' && onStop && (
                        <button
                            onClick={(e) => { e.stopPropagation(); onStop(run); }}
                            title="Stop training"
                            style={{
                                padding: '8px',
                                backgroundColor: '#f59e0b',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'all 150ms',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#d97706'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f59e0b'}
                        >
                            <Square size={16} />
                        </button>
                    )}
                    {run.status !== 'running' && onDelete && (
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(true); }}
                            title="Delete run"
                            style={{
                                padding: '8px',
                                backgroundColor: 'transparent',
                                color: '#6b7280',
                                border: '1px solid #374151',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'all 150ms',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#ef4444';
                                e.currentTarget.style.borderColor = '#ef4444';
                                e.currentTarget.style.color = 'white';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = 'transparent';
                                e.currentTarget.style.borderColor = '#374151';
                                e.currentTarget.style.color = '#6b7280';
                            }}
                        >
                            <Trash2 size={16} />
                        </button>
                    )}
                </div>
            </div>

            {/* Body */}
            <div className="card__body">
                {/* Config Summary */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: 'var(--spacing-sm)',
                    marginBottom: 'var(--spacing-md)',
                    padding: 'var(--spacing-sm)',
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: 'var(--border-radius-sm)',
                    fontSize: 'var(--font-size-xs)'
                }}>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Model:</span>{' '}
                        <strong>{run.config.model}</strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Epochs:</span>{' '}
                        <strong>{run.config.epochs}</strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Batch:</span>{' '}
                        <strong>{run.config.batch}</strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Device:</span>{' '}
                        <strong>{run.config.device}</strong>
                    </div>
                </div>

                {/* Metrics (if completed) */}
                {run.metrics && (
                    <div style={{
                        padding: 'var(--spacing-md)',
                        backgroundColor: '#d1fae5',
                        border: '1px solid #10b981',
                        borderRadius: 'var(--border-radius-md)',
                        marginBottom: 'var(--spacing-md)'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-sm)' }}>
                            <TrendingUp size={16} style={{ color: '#065f46' }} />
                            <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: '#065f46' }}>
                                Results
                            </span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-sm)', fontSize: 'var(--font-size-sm)', color: '#065f46' }}>
                            <div>mAP50: <strong>{formatMetric(run.metrics.map50)}</strong></div>
                            <div>mAP50-95: <strong>{formatMetric(run.metrics.map50_95)}</strong></div>
                        </div>
                    </div>
                )}

                {/* Error (if failed) */}
                {run.error && (
                    <div style={{
                        padding: 'var(--spacing-md)',
                        backgroundColor: '#fee2e2',
                        border: '1px solid #ef4444',
                        borderRadius: 'var(--border-radius-md)',
                        marginBottom: 'var(--spacing-md)',
                        fontSize: 'var(--font-size-sm)',
                        color: '#991b1b'
                    }}>
                        <strong>Error:</strong> {run.error}
                    </div>
                )}

                {/* Info */}
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-xs)' }}>
                        <Database size={12} />
                        <span>{run.dataset_name}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-xs)' }}>
                        <Clock size={12} />
                        <span>{formatDate(run.created)}</span>
                    </div>
                    {run.duration_ms && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                            <Zap size={12} />
                            <span>Duration: {formatDuration(run.duration_ms)}</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RunCard;