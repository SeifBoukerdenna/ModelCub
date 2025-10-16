import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Play, Pause, Square, ChevronRight, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { Job, Task } from '@/lib/api/types';

export const AnnotationView = () => {
    const { name: datasetName } = useParams<{ name: string }>();
    const [searchParams] = useSearchParams();
    const projectPath = api.getProjectPath();

    const navigate = useNavigate();

    const jobId = searchParams.get('job_id');

    const [job, setJob] = useState<Job | null>(null);
    const [currentTask, setCurrentTask] = useState<Task | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string | null>(null);

    // Load job details
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

    // Load next task
    const loadNextTask = useCallback(async () => {
        if (!jobId) return;

        try {
            setLoading(true);
            setError(null);

            const task = await api.getNextTask(jobId);

            if (!task) {
                // Job complete!
                console.log('Job complete, no more tasks');
                navigate(`/datasets/${datasetName}`);
                return;
            }

            setCurrentTask(task);

            // Build image URL
            const imgUrl = `/api/v1/datasets/${datasetName}/image/${task.image_path}?project_path=${encodeURIComponent(projectPath || '')}`;
            setImageUrl(imgUrl);

            // Refresh job status
            await loadJob();
        } catch (err: any) {
            console.error('Failed to load next task:', err);
            setError(err?.message || 'Failed to load next task');
        } finally {
            setLoading(false);
        }
    }, [jobId, datasetName, navigate, loadJob]);

    // Pause job
    const handlePause = useCallback(async () => {
        if (!jobId) return;

        try {
            await api.pauseJob(jobId);
            await loadJob();
        } catch (err: any) {
            console.error('Failed to pause job:', err);
            setError(err?.message || 'Failed to pause job');
        }
    }, [jobId, loadJob]);

    // Resume job
    const handleResume = useCallback(async () => {
        if (!jobId) return;

        try {
            await api.startJob(jobId);
            await loadJob();
            await loadNextTask();
        } catch (err: any) {
            console.error('Failed to resume job:', err);
            setError(err?.message || 'Failed to resume job');
        }
    }, [jobId, loadJob, loadNextTask]);

    // Cancel job
    const handleCancel = useCallback(async () => {
        if (!jobId) return;

        const confirmed = window.confirm('Are you sure you want to cancel this job?');
        if (!confirmed) return;

        try {
            await api.cancelJob(jobId);
            navigate(`/datasets/${datasetName}`);
        } catch (err: any) {
            console.error('Failed to cancel job:', err);
            setError(err?.message || 'Failed to cancel job');
        }
    }, [jobId, datasetName, navigate]);

    // Skip current task (for now, just loads next)
    const handleSkip = useCallback(async () => {
        await loadNextTask();
    }, [loadNextTask]);

    // Initialize
    useEffect(() => {
        if (!jobId) {
            setError('No job ID provided');
            return;
        }

        loadJob();
        loadNextTask();
    }, [jobId, loadJob, loadNextTask]);

    if (!jobId) {
        return (
            <div className="annotation-view">
                <div className="annotation-error">
                    <AlertCircle size={24} />
                    <p>No job ID provided</p>
                    <button
                        className="btn btn--secondary"
                        onClick={() => navigate(`/datasets/${datasetName}`)}
                    >
                        Back to Dataset
                    </button>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="annotation-view">
                <div className="annotation-error">
                    <AlertCircle size={24} />
                    <p>{error}</p>
                    <button
                        className="btn btn--secondary"
                        onClick={() => navigate(`/datasets/${datasetName}`)}
                    >
                        Back to Dataset
                    </button>
                </div>
            </div>
        );
    }

    const progressPercent = job
        ? Math.round((job.completed_tasks / job.total_tasks) * 100)
        : 0;

    return (
        <div className="annotation-view">
            {/* Header */}
            <div className="annotation-header">
                <div className="annotation-header__left">
                    <button
                        className="btn btn--sm btn--ghost"
                        onClick={() => navigate(`/datasets/${datasetName}`)}
                    >
                        <ArrowLeft size={16} />
                        Back
                    </button>
                    <h1>Annotate: {datasetName}</h1>
                </div>

                <div className="annotation-header__center">
                    {job && (
                        <div className="job-progress">
                            <div className="job-progress__bar">
                                <div
                                    className="job-progress__fill"
                                    style={{ width: `${progressPercent}%` }}
                                />
                            </div>
                            <span className="job-progress__text">
                                {job.completed_tasks} / {job.total_tasks} ({progressPercent}%)
                            </span>
                        </div>
                    )}
                </div>

                <div className="annotation-header__right">
                    <div className="job-controls">
                        {job?.status === 'running' && (
                            <button
                                className="btn btn--sm btn--secondary"
                                onClick={handlePause}
                                title="Pause job"
                            >
                                <Pause size={16} />
                                Pause
                            </button>
                        )}

                        {job?.status === 'paused' && (
                            <button
                                className="btn btn--sm btn--primary"
                                onClick={handleResume}
                                title="Resume job"
                            >
                                <Play size={16} />
                                Resume
                            </button>
                        )}

                        <button
                            className="btn btn--sm btn--danger"
                            onClick={handleCancel}
                            title="Cancel job"
                        >
                            <Square size={16} />
                            Cancel
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="annotation-content">
                {loading && !currentTask ? (
                    <div className="annotation-loading">
                        <p>Loading task...</p>
                    </div>
                ) : currentTask ? (
                    <>
                        {/* Canvas Area */}
                        <div className="annotation-canvas">
                            {imageUrl ? (
                                <div className="annotation-canvas__wrapper">
                                    <img
                                        src={imageUrl}
                                        alt={currentTask.image_id}
                                        className="annotation-canvas__image"
                                    />
                                    {/* TODO: Add annotation tools here later */}
                                    <div className="annotation-canvas__placeholder">
                                        <p>Annotation tools will go here</p>
                                        <p className="annotation-canvas__placeholder-hint">
                                            For now, you can navigate through images using the controls below
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="annotation-canvas__loading">
                                    Loading image...
                                </div>
                            )}
                        </div>

                        {/* Sidebar */}
                        <div className="annotation-sidebar">
                            <div className="annotation-task-info">
                                <h3>Current Task</h3>
                                <div className="annotation-task-info__item">
                                    <span className="label">Image ID:</span>
                                    <span className="value">{currentTask.image_id}</span>
                                </div>
                                <div className="annotation-task-info__item">
                                    <span className="label">Task ID:</span>
                                    <span className="value">{currentTask.task_id}</span>
                                </div>
                                <div className="annotation-task-info__item">
                                    <span className="label">Status:</span>
                                    <span className={`value status-${currentTask.status}`}>
                                        {currentTask.status}
                                    </span>
                                </div>
                            </div>

                            <div className="annotation-job-info">
                                <h3>Job Status</h3>
                                {job && (
                                    <>
                                        <div className="annotation-job-info__item">
                                            <span className="label">Job ID:</span>
                                            <span className="value">{job.job_id}</span>
                                        </div>
                                        <div className="annotation-job-info__item">
                                            <span className="label">Status:</span>
                                            <span className={`value status-${job.status}`}>
                                                {job.status}
                                            </span>
                                        </div>
                                        <div className="annotation-job-info__item">
                                            <span className="label">Completed:</span>
                                            <span className="value">
                                                {job.completed_tasks} / {job.total_tasks}
                                            </span>
                                        </div>
                                        {job.failed_tasks > 0 && (
                                            <div className="annotation-job-info__item">
                                                <span className="label">Failed:</span>
                                                <span className="value error">
                                                    {job.failed_tasks}
                                                </span>
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="annotation-empty">
                        <p>No task loaded</p>
                    </div>
                )}
            </div>

            {/* Footer Controls */}
            <div className="annotation-footer">
                <div className="annotation-footer__left">
                    <span className="annotation-footer__hint">
                        Annotation tools coming soon
                    </span>
                </div>

                <div className="annotation-footer__center">
                    {currentTask && (
                        <button
                            className="btn btn--lg btn--primary"
                            onClick={handleSkip}
                            disabled={loading}
                        >
                            {loading ? 'Loading...' : 'Next Image'}
                            <ChevronRight size={20} />
                        </button>
                    )}
                </div>

                <div className="annotation-footer__right">
                    {/* Placeholder for future controls */}
                </div>
            </div>
        </div>
    );
};