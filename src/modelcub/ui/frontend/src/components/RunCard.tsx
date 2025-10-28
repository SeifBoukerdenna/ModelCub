import React, { useState } from 'react';
import { Play, Square, Trash2, Clock, TrendingUp, Database, Zap } from 'lucide-react';
import type { TrainingRun } from '@/lib/api/types';
import RunDetailsModal from './RunDetailsModal';

interface RunCardProps {
    run: TrainingRun;
    onStart?: (run: TrainingRun) => void;
    onStop?: (run: TrainingRun) => void;
    onDelete?: (run: TrainingRun) => void;
    onRunUpdated?: () => void;
}

const RunCard: React.FC<RunCardProps> = ({ run, onStart, onStop, onDelete, onRunUpdated }) => {
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [showDetailsModal, setShowDetailsModal] = useState(false);

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

    const formatMetric = (value?: number | null) => {
        if (value === null || value === undefined) return 'N/A';
        return `${(value * 100).toFixed(1)}%`;
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleString();
    };

    const handleCardClick = () => {
        setShowDetailsModal(true);
    };

    const handleRunUpdated = () => {
        if (onRunUpdated) onRunUpdated();
    };

    return (
        <>
            {/* Delete Confirmation */}
            {showDeleteConfirm && (
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 'var(--border-radius-lg)',
                    zIndex: 10,
                    padding: 'var(--spacing-lg)'
                }}>
                    <p style={{ color: 'white', fontSize: 'var(--font-size-md)', marginBottom: 'var(--spacing-md)' }}>
                        Delete this training run?
                    </p>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(false); }}
                            style={{
                                padding: 'var(--spacing-sm) var(--spacing-lg)',
                                backgroundColor: '#6b7280',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: 'pointer',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 600,
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); if (onDelete) onDelete(run); setShowDeleteConfirm(false); }}
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

            <div
                className="card run-card"
                style={{
                    position: 'relative',
                    padding: 'var(--spacing-lg)',
                    cursor: 'pointer',
                    transition: 'transform 0.2s, box-shadow 0.2s'
                }}
                onClick={handleCardClick}
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '';
                }}
            >
                {/* Header */}
                <div className="card__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 'var(--spacing-md)' }}>
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
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }} onClick={(e) => e.stopPropagation()}>
                        {run.status === 'pending' && onStart && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onStart(run); }}
                                style={{
                                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                                    backgroundColor: '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: 'var(--border-radius-sm)',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                }}
                                title="Start training"
                            >
                                <Play size={14} />
                            </button>
                        )}
                        {run.status === 'running' && onStop && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onStop(run); }}
                                style={{
                                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                                    backgroundColor: '#ef4444',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: 'var(--border-radius-sm)',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                }}
                                title="Stop training"
                            >
                                <Square size={14} />
                            </button>
                        )}
                        {run.status !== 'running' && onDelete && (
                            <button
                                onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(true); }}
                                style={{
                                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                                    backgroundColor: 'transparent',
                                    color: '#6b7280',
                                    border: '1px solid #6b7280',
                                    borderRadius: 'var(--border-radius-sm)',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                }}
                                title="Delete run"
                            >
                                <Trash2 size={14} />
                            </button>
                        )}
                    </div>
                </div>

                {/* Config */}
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

            {/* Run Details Modal */}
            {showDetailsModal && (
                <RunDetailsModal
                    run={run}
                    isOpen={showDetailsModal}
                    onClose={() => setShowDetailsModal(false)}
                    onRunUpdated={handleRunUpdated}
                />
            )}
        </>
    );
};

export default RunCard;