import { useState, useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

// Hooks
import { useAnnotationJob } from '@/hooks/useAnnotationJob';
import { useAnnotationNavigation } from '@/hooks/useAnnotationNavigation';
import { useAnnotationKeyboard } from '@/hooks/useAnnotationKeyboard';
import { useDatasetClasses } from '@/hooks/useDatasetClasses';
import { useImageLoader } from '@/hooks/useImageLoader';

// Components
import ClassManagerModal from '@/components/ClassManagerModal';

import './AnnotationViewer.css';
import { AnnotationHeader } from './datasets/AnnotationHeader';
import { AnnotationSidebar } from './datasets/AnnotationSidebar';
import { AnnotationCanvas } from './datasets/AnnotationCanvas';

export const AnnotationView = () => {
    const { name: datasetName } = useParams<{ name: string }>();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const jobId = searchParams.get('job_id');

    const [showClassManager, setShowClassManager] = useState(false);

    // Load job and tasks
    const {
        job,
        tasks,
        error: jobError,
        isLoading: jobLoading,
        completedCount,
        markTaskInProgress,
        completeTask,
    } = useAnnotationJob(jobId);

    // Navigation state
    const {
        currentIndex,
        currentTask,
        canGoPrevious,
        canGoNext,
        goToNext,
        goToPrevious,
    } = useAnnotationNavigation(tasks, () => navigate(`/datasets/${datasetName}`));

    // Dataset classes
    const { classes, reload: reloadClasses } = useDatasetClasses(datasetName);

    // Image loading
    const {
        imageUrl,
        isLoading: imageLoading,
        handleImageLoad,
        handleImageError,
    } = useImageLoader(currentTask, datasetName, api.getProjectPath());

    // Mark task as in_progress when viewing
    useEffect(() => {
        if (currentTask && currentTask.status === 'pending') {
            markTaskInProgress(currentTask.task_id);
        }
    }, [currentTask?.task_id, markTaskInProgress]);

    // Handle task completion
    const handleCompleteTask = async () => {
        if (!currentTask) return;
        try {
            await completeTask(currentTask.task_id);
            goToNext();
        } catch (err) {
            console.error('Failed to complete task:', err);
        }
    };

    // Keyboard shortcuts
    useAnnotationKeyboard({
        onNext: goToNext,
        onPrevious: goToPrevious,
        onExit: () => navigate(`/datasets/${datasetName}`),
        onSave: () => console.log('Save triggered'),
    });

    // Error state
    if (!jobId || jobError) {
        return (
            <div className="annotation-view">
                <div className="annotation-error">
                    <AlertCircle size={24} />
                    <p>{jobError || 'No job ID provided'}</p>
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

    // Loading state
    if (jobLoading) {
        return (
            <div className="annotation-view">
                <div className="annotation-error">
                    <p>Loading annotation job...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="annotation-view">
            {/* Header */}
            <AnnotationHeader
                datasetName={datasetName || 'Unknown'}
                currentIndex={currentIndex}
                totalTasks={tasks.length}
                completedCount={completedCount}
                tasks={tasks}
                canGoPrevious={canGoPrevious}
                canGoNext={canGoNext}
                onExit={() => navigate(`/datasets/${datasetName}`)}
                onPrevious={goToPrevious}
                onNext={goToNext}
            />

            {/* Main Content */}
            <div className="annotation-content-full">
                {/* Canvas */}
                <AnnotationCanvas
                    currentTask={currentTask}
                    imageUrl={imageUrl}
                    isLoading={imageLoading}
                    onImageLoad={handleImageLoad}
                    onImageError={handleImageError}
                    onComplete={handleCompleteTask}
                />

                {/* Sidebar */}
                <AnnotationSidebar
                    classes={classes}
                    currentTask={currentTask}
                    job={job}
                    completedCount={completedCount}
                    onManageClasses={() => setShowClassManager(true)}
                />
            </div>

            {/* Class Manager Modal */}
            {showClassManager && datasetName && (
                <ClassManagerModal
                    isOpen={true}
                    onClose={() => {
                        setShowClassManager(false);
                        reloadClasses();
                    }}
                    datasetId={datasetName}
                    initialClasses={classes}
                    onUpdate={reloadClasses}
                />
            )}
        </div>
    );
};