import React, { useState, useEffect, useRef } from 'react';
import { X, Zap, Play, Square, Trash2, RefreshCw, Terminal, TrendingUp, Clock, AlertCircle, Upload } from 'lucide-react';
import type { TrainingRun } from '@/lib/api/types';
import { api } from '@/lib/api';
import { toast } from '@/lib/toast';
import LogViewer from './LogViewer';


interface RunDetailsModalProps {
    run: TrainingRun;
    isOpen: boolean;
    onClose: () => void;
    onRunUpdated: () => void;
}

const RunDetailsModal: React.FC<RunDetailsModalProps> = ({ run: initialRun, isOpen, onClose, onRunUpdated }) => {
    const [run, setRun] = useState<TrainingRun>(initialRun);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isStarting, setIsStarting] = useState(false);
    const [isStopping, setIsStopping] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);
    const [logStream, setLogStream] = useState<'stdout' | 'stderr'>('stdout');
    const [isLoadingLogs, setIsLoadingLogs] = useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);

    // Fetch logs
    const fetchLogs = async () => {
        setIsLoadingLogs(true);
        try {
            const logsData = await api.getLogs(run.id, logStream, 200);
            if (logsData.exists) {
                setLogs(logsData.logs);
                // Auto-scroll to bottom
                setTimeout(() => logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
            }
        } catch (err) {
            console.error('Failed to fetch logs:', err);
        } finally {
            setIsLoadingLogs(false);
        }
    };

    // Fetch logs on mount and when stream changes
    useEffect(() => {
        if (isOpen) {
            fetchLogs();
        }
    }, [isOpen, logStream, run.id]);

    // Auto-refresh for running jobs every 3 seconds
    useEffect(() => {
        if (!isOpen || run.status !== 'running') return;

        const interval = setInterval(async () => {
            try {
                const updated = await api.getRun(run.id);
                if (updated) setRun(updated);
                // Also fetch logs
                fetchLogs();
            } catch (err) {
                console.error('Failed to refresh run:', err);
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [isOpen, run.id, run.status, logStream]);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            const updated = await api.getRun(run.id);
            if (updated) {
                setRun(updated);
                toast.success('Run refreshed');
            }
        } catch (err) {
            toast.error('Failed to refresh run');
        } finally {
            setIsRefreshing(false);
        }
    };

    const handleStart = async () => {
        setIsStarting(true);
        try {
            await api.startRun(run.id);
            const updated = await api.getRun(run.id);
            if (updated) setRun(updated);
            toast.success('Training started');
            onRunUpdated();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to start run');
        } finally {
            setIsStarting(false);
        }
    };

    const handleStop = async () => {
        setIsStopping(true);
        try {
            await api.stopRun(run.id);
            const updated = await api.getRun(run.id);
            if (updated) setRun(updated);
            toast.success('Training stopped');
            onRunUpdated();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to stop run');
        } finally {
            setIsStopping(false);
        }
    };

    const handleDelete = async () => {
        setIsDeleting(true);
        try {
            await api.deleteRun(run.id);
            toast.success('Run deleted');
            onRunUpdated();
            onClose();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to delete run');
            setIsDeleting(false);
        }
    };

    const getStatusColor = (status: string) => {
        const colors = {
            pending: '#fbbf24',
            running: '#3b82f6',
            completed: '#10b981',
            failed: '#ef4444',
            cancelled: '#6b7280'
        };
        return colors[status as keyof typeof colors] || colors.cancelled;
    };

    const formatDuration = (ms?: number | null) => {
        if (!ms) return 'N/A';
        const seconds = ms / 1000;
        if (seconds < 60) return `${seconds.toFixed(0)}s`;
        if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
        return `${(seconds / 3600).toFixed(1)}h`;
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleString();
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal run-details-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Zap size={20} />
                        </div>
                        <div>
                            <h2 className="modal__title" style={{ marginBottom: '4px' }}>Training Run Details</h2>
                            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>
                                {run.id}
                            </div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                        {run.status === "completed" && <button
                            className="modal__close"
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                            title="Refresh"
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
                        >
                            <Upload size={18} />
                        </button>}
                        <button
                            className="modal__close"
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                            title="Refresh"
                            style={{ padding: 'var(--spacing-xs)' }}
                        >
                            <RefreshCw size={18} className={isRefreshing ? 'spinner' : ''} />
                        </button>
                        <button
                            className="modal__close"
                            onClick={onClose}
                            aria-label="Close modal"
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                <div className="modal__body">
                    {/* Status Section */}
                    <div className="form-group">
                        <label className="form-label">Status</label>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 'var(--spacing-xs)',
                            padding: 'var(--spacing-sm) var(--spacing-md)',
                            backgroundColor: `${getStatusColor(run.status)}20`,
                            border: `2px solid ${getStatusColor(run.status)}`,
                            borderRadius: 'var(--border-radius-md)',
                            fontSize: 'var(--font-size-sm)',
                            fontWeight: 600,
                            color: getStatusColor(run.status),
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                        }}>
                            {run.status === 'running' && <div className="status-pulse" />}
                            {run.status}
                        </div>
                    </div>

                    {/* Configuration */}
                    <div className="form-group">
                        <label className="form-label">Configuration</label>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: 'var(--spacing-sm)',
                            padding: 'var(--spacing-md)',
                            backgroundColor: 'var(--color-surface)',
                            borderRadius: 'var(--border-radius-md)',
                            border: '1px solid var(--color-border)'
                        }}>
                            <ConfigItem label="Dataset" value={run.dataset_name} />
                            <ConfigItem label="Model" value={run.config.model} />
                            <ConfigItem label="Epochs" value={run.config.epochs} />
                            <ConfigItem label="Batch Size" value={run.config.batch} />
                            <ConfigItem label="Image Size" value={run.config.imgsz} />
                            <ConfigItem label="Device" value={run.config.device} />
                            <ConfigItem label="Patience" value={run.config.patience} />
                            <ConfigItem label="Task" value={run.task} />
                        </div>
                    </div>

                    {/* Metrics (if completed) */}
                    {run.status === 'completed' && run.metrics && (
                        <div className="form-group">
                            <label className="form-label">
                                <TrendingUp size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                                Performance Metrics
                            </label>
                            <div style={{
                                padding: 'var(--spacing-md)',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                borderRadius: 'var(--border-radius-md)',
                                border: '2px solid #10b981'
                            }}>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-md)' }}>
                                    <MetricItem label="mAP50" value={run.metrics.map50} />
                                    <MetricItem label="mAP50-95" value={run.metrics.map50_95} />
                                    <MetricItem label="Precision" value={run.metrics.precision} />
                                    <MetricItem label="Recall" value={run.metrics.recall} />
                                </div>
                                {run.metrics.best_epoch && (
                                    <div style={{ marginTop: 'var(--spacing-sm)', fontSize: 'var(--font-size-sm)', color: '#065f46' }}>
                                        <strong>Best Epoch:</strong> {run.metrics.best_epoch}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Error (if failed) */}
                    {run.status === 'failed' && run.error && (
                        <div className="alert alert--error">
                            <AlertCircle size={20} />
                            <div>
                                <strong>Error:</strong> {run.error}
                            </div>
                        </div>
                    )}

                    {/* Timeline */}
                    <div className="form-group">
                        <label className="form-label">
                            <Clock size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                            Timeline
                        </label>
                        <div style={{
                            padding: 'var(--spacing-md)',
                            backgroundColor: 'var(--color-surface)',
                            borderRadius: 'var(--border-radius-md)',
                            border: '1px solid var(--color-border)',
                            fontSize: 'var(--font-size-sm)'
                        }}>
                            <div style={{ marginBottom: 'var(--spacing-xs)' }}>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Created:</span>{' '}
                                <strong>{formatDate(run.created)}</strong>
                            </div>
                            {run.started && (
                                <div style={{ marginBottom: 'var(--spacing-xs)' }}>
                                    <span style={{ color: 'var(--color-text-secondary)' }}>Started:</span>{' '}
                                    <strong>{formatDate(run.started)}</strong>
                                </div>
                            )}
                            {run.duration_ms && (
                                <div>
                                    <span style={{ color: 'var(--color-text-secondary)' }}>Duration:</span>{' '}
                                    <strong>{formatDuration(run.duration_ms)}</strong>
                                </div>
                            )}
                            {run.pid && (
                                <div style={{ marginTop: 'var(--spacing-xs)' }}>
                                    <span style={{ color: 'var(--color-text-secondary)' }}>Process ID:</span>{' '}
                                    <strong>{run.pid}</strong>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Logs Note */}
                    {run.status === 'running' && (
                        <div className="info-box">
                            <div className="info-box__icon">
                                <Terminal size={20} />
                            </div>
                            <div className="info-box__content">
                                <div className="info-box__title">Training in Progress</div>
                                <div className="info-box__description">
                                    Logs are auto-updating every 3 seconds
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Logs Viewer */}
                    <div className="form-group">
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)' }}>
                            <label className="form-label" style={{ marginBottom: 0 }}>
                                <Terminal size={16} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                                Training Logs
                            </label>
                            <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                                <button
                                    type="button"
                                    onClick={() => setLogStream('stdout')}
                                    style={{
                                        padding: '4px 12px',
                                        fontSize: 'var(--font-size-xs)',
                                        fontWeight: 600,
                                        border: logStream === 'stdout' ? '2px solid #3b82f6' : '1px solid var(--color-border)',
                                        backgroundColor: logStream === 'stdout' ? 'rgba(59, 130, 246, 0.1)' : 'var(--color-surface)',
                                        color: logStream === 'stdout' ? '#3b82f6' : 'var(--color-text-secondary)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        cursor: 'pointer'
                                    }}
                                >
                                    stdout
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setLogStream('stderr')}
                                    style={{
                                        padding: '4px 12px',
                                        fontSize: 'var(--font-size-xs)',
                                        fontWeight: 600,
                                        border: logStream === 'stderr' ? '2px solid #3b82f6' : '1px solid var(--color-border)',
                                        backgroundColor: logStream === 'stderr' ? 'rgba(59, 130, 246, 0.1)' : 'var(--color-surface)',
                                        color: logStream === 'stderr' ? '#3b82f6' : 'var(--color-text-secondary)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        cursor: 'pointer'
                                    }}
                                >
                                    stderr
                                </button>
                                <button
                                    type="button"
                                    onClick={fetchLogs}
                                    disabled={isLoadingLogs}
                                    style={{
                                        padding: '4px 12px',
                                        fontSize: 'var(--font-size-xs)',
                                        fontWeight: 600,
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        color: 'var(--color-text-secondary)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        cursor: isLoadingLogs ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '4px'
                                    }}
                                >
                                    <RefreshCw size={12} className={isLoadingLogs ? 'spinner' : ''} />
                                </button>
                            </div>
                        </div>
                        <div style={{
                            backgroundColor: '#0f172a',
                            border: '1px solid #334155',
                            borderRadius: 'var(--border-radius-md)',
                            padding: 'var(--spacing-md)',
                            maxHeight: '400px',
                            overflowY: 'auto',
                            fontFamily: 'monospace',
                            fontSize: '12px',
                            lineHeight: '1.5',
                            color: '#e2e8f0'
                        }}>
                            {isLoadingLogs && logs.length === 0 ? (
                                <div style={{ color: '#64748b', textAlign: 'center', padding: 'var(--spacing-lg)' }}>
                                    Loading logs...
                                </div>
                            ) : logs.length === 0 ? (
                                <div style={{ color: '#64748b', textAlign: 'center', padding: 'var(--spacing-lg)' }}>
                                    No logs available yet
                                </div>
                            ) : (
                                <LogViewer logs={logs} />
                            )}
                            <div ref={logsEndRef} />
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="modal__footer">
                    {showDeleteConfirm ? (
                        <>
                            <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-error)', marginRight: 'auto' }}>
                                Are you sure?
                            </span>
                            <button
                                className="btn btn--secondary"
                                onClick={() => setShowDeleteConfirm(false)}
                                disabled={isDeleting}
                            >
                                Cancel
                            </button>
                            <button
                                className="btn"
                                onClick={handleDelete}
                                disabled={isDeleting}
                                style={{ backgroundColor: '#ef4444', color: 'white' }}
                            >
                                {isDeleting ? 'Deleting...' : 'Delete'}
                            </button>
                        </>
                    ) : (
                        <>
                            <button
                                className="btn"
                                onClick={() => setShowDeleteConfirm(true)}
                                disabled={run.status === 'running' || isDeleting}
                                style={{
                                    backgroundColor: 'transparent',
                                    color: '#ef4444',
                                    border: '1px solid #ef4444',
                                    marginRight: 'auto'
                                }}
                            >
                                <Trash2 size={16} />
                                Delete
                            </button>

                            {run.status === 'pending' && (
                                <button
                                    className="btn btn--primary"
                                    onClick={handleStart}
                                    disabled={isStarting}
                                >
                                    <Play size={16} />
                                    {isStarting ? 'Starting...' : 'Start Training'}
                                </button>
                            )}

                            {run.status === 'running' && (
                                <button
                                    className="btn btn--secondary"
                                    onClick={handleStop}
                                    disabled={isStopping}
                                >
                                    <Square size={16} />
                                    {isStopping ? 'Stopping...' : 'Stop Training'}
                                </button>
                            )}

                            <button
                                className="btn btn--secondary"
                                onClick={onClose}
                            >
                                Close
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

// Helper components
const ConfigItem: React.FC<{ label: string; value: any }> = ({ label, value }) => (
    <div style={{ fontSize: 'var(--font-size-sm)' }}>
        <div style={{ color: 'var(--color-text-secondary)', marginBottom: '2px' }}>{label}</div>
        <div style={{ fontWeight: 600, fontFamily: 'monospace' }}>{value}</div>
    </div>
);

const MetricItem: React.FC<{ label: string; value?: number | null }> = ({ label, value }) => (
    <div style={{ fontSize: 'var(--font-size-sm)' }}>
        <div style={{ color: '#065f46', marginBottom: '2px' }}>{label}</div>
        <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: '#047857' }}>
            {value !== null && value !== undefined ? (value * 100).toFixed(1) + '%' : 'N/A'}
        </div>
    </div>
);

export default RunDetailsModal;