import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { X, ChevronLeft, ChevronRight, AlertCircle, Settings, CheckCircle, Clock } from 'lucide-react';
import { api } from '@/lib/api';
import { useJobWebSocket } from '@/hooks/useJobWebSocket';
import type { Job, Task } from '@/lib/api/types';

import './AnnotationViewer.css';
import ClassManagerModal from './ClassManagerModal';

export const AnnotationView = () => {
    const { name: datasetName } = useParams<{ name: string }>();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const jobId = searchParams.get('job_id');

    const [job, setJob] = useState<Job | null>(null);
    const [allTasks, setAllTasks] = useState<Task[]>([]);
    const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [classes, setClasses] = useState<string[]>([]);
    const [showClassManager, setShowClassManager] = useState(false);
    const [isLoadingImage, setIsLoadingImage] = useState(true);

    const projectPath = api.getProjectPath();
    const currentTask = allTasks[currentTaskIndex] || null;
    const imageUrl = currentTask
        ? `/api/v1/datasets/${datasetName}/image/${currentTask.image_path}?project_path=${encodeURIComponent(projectPath || '')}`
        : null;

    // WebSocket subscriptions
    useJobWebSocket(jobId, {
        onTaskCompleted: (task, updatedJob) => {
            console.log('Task completed via WebSocket');
            setJob(updatedJob);
            setAllTasks(prev => prev.map(t =>
                t.task_id === task.task_id ? task : t
            ));
        },
        onJobStarted: (updatedJob) => {
            console.log('Job started via WebSocket');
            setJob(updatedJob);
        },
        onJobPaused: (updatedJob) => {
            console.log('Job paused via WebSocket');
            setJob(updatedJob);
        },
        onJobCancelled: (updatedJob) => {
            console.log('Job cancelled via WebSocket');
            setJob(updatedJob);
        },
        onJobCompleted: (updatedJob) => {
            console.log('Job completed via WebSocket');
            setJob(updatedJob);
        }
    });

    const loadClasses = useCallback(async () => {
        if (!datasetName) return;
        try {
            const dataset = await api.getDataset(datasetName);
            setClasses(dataset.classes || []);
        } catch (err) {
            console.error('Failed to load classes:', err);
        }
    }, [datasetName]);

    const loadAllTasks = useCallback(async () => {
        if (!jobId) return;
        try {
            const tasks = await api.getJobTasks(jobId);
            setAllTasks(tasks);

            // Auto-select first incomplete task
            if (currentTaskIndex === 0 && tasks.length > 0) {
                const firstIncomplete = tasks.findIndex(t =>
                    t.status === 'pending' || t.status === 'in_progress'
                );
                if (firstIncomplete >= 0) {
                    setCurrentTaskIndex(firstIncomplete);
                }
            }
        } catch (err: any) {
            console.error('Failed to load tasks:', err);
        }
    }, [jobId]);

    const loadJob = useCallback(async () => {
        if (!jobId) return;
        try {
            const jobData = await api.getJob(jobId);
            setJob(jobData);
        } catch (err: any) {
            console.error('Failed to load job:', err);
            setError(err?.message || 'Failed to load job');
        }
    }, [jobId]);

    // Mark task as in_progress when viewing
    useEffect(() => {
        if (!currentTask || !jobId) return;

        const markInProgress = async () => {
            if (currentTask.status === 'pending') {
                try {
                    await api.updateTaskStatus(jobId, currentTask.task_id, 'in_progress');
                    // Update local state
                    setAllTasks(prev => prev.map(t =>
                        t.task_id === currentTask.task_id
                            ? { ...t, status: 'in_progress' as any }
                            : t
                    ));
                } catch (err) {
                    console.error('Failed to mark task as in_progress:', err);
                }
            }
        };

        markInProgress();
    }, [currentTask?.task_id, jobId]);

    const goToNext = useCallback(() => {
        if (currentTaskIndex < allTasks.length - 1) {
            setCurrentTaskIndex(prev => prev + 1);
        } else {
            navigate(`/datasets/${datasetName}`);
        }
    }, [currentTaskIndex, allTasks.length, datasetName, navigate]);

    const goToPrevious = useCallback(() => {
        if (currentTaskIndex > 0) {
            setCurrentTaskIndex(prev => prev - 1);
        }
    }, [currentTaskIndex]);

    const handleExit = useCallback(() => {
        navigate(`/datasets/${datasetName}`);
    }, [datasetName, navigate]);

    const handleCompleteTask = async () => {
        if (!currentTask || !jobId) return;
        try {
            await api.completeTask(jobId, currentTask.task_id);
            // WebSocket handles state updates
            goToNext();
        } catch (err: any) {
            console.error('Failed to complete task:', err);
        }
    };

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;

            switch (e.key) {
                case 'ArrowRight':
                case 'd':
                case 'D':
                    goToNext();
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    goToPrevious();
                    break;
                case 'Escape':
                    handleExit();
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [goToNext, goToPrevious, handleExit]);

    // Initialize
    useEffect(() => {
        if (!jobId) {
            setError('No job ID provided');
            return;
        }

        loadJob();
        loadAllTasks();
        loadClasses();
    }, [jobId, loadJob, loadAllTasks, loadClasses]);

    // Handle image loading
    useEffect(() => {
        if (imageUrl) {
            setIsLoadingImage(true);
        }
    }, [imageUrl]);

    const handleImageLoad = () => setIsLoadingImage(false);
    const handleImageError = () => {
        setIsLoadingImage(false);
        console.error('Failed to load image');
    };

    if (!jobId || error) {
        return (
            <div className="annotation-view">
                <div className="annotation-error">
                    <AlertCircle size={24} />
                    <p>{error || 'No job ID provided'}</p>
                    <button className="btn btn--secondary" onClick={() => navigate(`/datasets/${datasetName}`)}>
                        Back to Dataset
                    </button>
                </div>
            </div>
        );
    }

    const completedCount = allTasks.filter(t => t.status === 'completed').length;

    return (
        <div className="annotation-view">
            {/* Header */}
            <div className="annotation-header-compact">
                <div className="annotation-header-compact__left">
                    <button className="btn btn--sm btn--ghost" onClick={handleExit} title="Exit (Esc)">
                        <X size={18} />
                    </button>
                    <span className="annotation-title">Annotate: {datasetName}</span>
                </div>

                <div className="annotation-header-compact__center">
                    <div className="progress-compact-enhanced">
                        <div className="progress-header-info">
                            <span className="progress-position">
                                Image {currentTaskIndex + 1} of {allTasks.length}
                            </span>
                            <span className="progress-percentage">
                                {Math.round((completedCount / allTasks.length) * 100)}% Complete
                            </span>
                        </div>
                        <div className="progress-bar-header">
                            <div
                                className="progress-fill-header"
                                style={{ width: `${(completedCount / allTasks.length) * 100}%` }}
                            >
                                <div className="progress-shimmer-header"></div>
                            </div>
                            {/* Task indicators */}
                            <div className="task-indicators">
                                {allTasks.map((task, idx) => (
                                    <div
                                        key={task.task_id}
                                        className={`task-indicator ${task.status === 'completed' ? 'completed' :
                                            idx === currentTaskIndex ? 'current' : 'pending'
                                            }`}
                                        style={{
                                            left: `${(idx / allTasks.length) * 100}%`,
                                            width: `${100 / allTasks.length}%`
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="annotation-header-compact__right">
                    <div className="nav-controls">
                        <button
                            className="btn btn--sm btn--secondary"
                            onClick={goToPrevious}
                            disabled={currentTaskIndex === 0}
                            title="Previous (←/A)"
                        >
                            <ChevronLeft size={18} />
                            Previous
                        </button>
                        <button className="btn btn--sm btn--primary" onClick={goToNext} title="Next (→/D)">
                            Next
                            <ChevronRight size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="annotation-content-full">
                {/* Canvas */}
                <div className="annotation-canvas-full">
                    {currentTask && imageUrl ? (
                        <div className="annotation-canvas__wrapper">
                            {/* Status Indicator */}
                            <div className={`annotation-canvas__status-overlay status-${currentTask.status}`}>
                                {currentTask.status === 'completed' && (
                                    <>
                                        <CheckCircle size={18} />
                                        <span>COMPLETED</span>
                                    </>
                                )}
                                {currentTask.status === 'pending' && (
                                    <>
                                        <AlertCircle size={18} />
                                        <span>PENDING</span>
                                    </>
                                )}
                                {currentTask.status === 'in_progress' && (
                                    <>
                                        <Clock size={18} />
                                        <span>IN PROGRESS</span>
                                    </>
                                )}
                            </div>

                            <img
                                src={imageUrl}
                                alt={currentTask.image_id}
                                className="annotation-canvas__image"
                                onLoad={handleImageLoad}
                                onError={handleImageError}
                                style={{ display: isLoadingImage ? 'none' : 'block' }}
                            />
                            {isLoadingImage && (
                                <div className="annotation-canvas__loading">Loading image...</div>
                            )}
                            <div className="annotation-canvas__overlay">
                                <p>Annotation tools will go here</p>
                                <button
                                    className="btn btn--primary"
                                    onClick={handleCompleteTask}
                                    style={{ marginTop: 'var(--spacing-md)' }}
                                >
                                    ✓ Complete Task (Test)
                                </button>
                                <p className="annotation-canvas__overlay-hint">
                                    Use ← → or A/D to navigate • ESC to exit
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="annotation-canvas__loading">Loading image...</div>
                    )}
                </div>

                {/* Sidebar */}
                <div className="annotation-sidebar-compact">
                    {/* Dataset Classes */}
                    <div className="sidebar-section">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-sm)' }}>
                            <h3>Classes ({classes.length})</h3>
                            <button
                                className="btn btn--xs btn--secondary"
                                onClick={() => setShowClassManager(true)}
                                title="Manage classes"
                                style={{ padding: '4px 8px', fontSize: 'var(--font-size-xs)' }}
                            >
                                <Settings size={12} />
                                Edit
                            </button>
                        </div>
                        {classes.length > 0 ? (
                            <div className="classes-list" style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-xs)' }}>
                                {classes.map((className, idx) => (
                                    <span
                                        key={idx}
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
                                        {className}
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
                        </div>
                    </div>
                </div>
            </div>

            {/* Class Manager Modal */}
            {showClassManager && datasetName && (
                <ClassManagerModal
                    isOpen={true}
                    onClose={() => {
                        setShowClassManager(false);
                        loadClasses();
                    }}
                    datasetId={datasetName}
                    initialClasses={classes}
                    onUpdate={loadClasses}
                />
            )}
        </div>
    );
};