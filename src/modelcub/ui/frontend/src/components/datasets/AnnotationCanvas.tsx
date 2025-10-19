import { CheckCircle, AlertCircle, Clock } from 'lucide-react';
import type { Task } from '@/lib/api/types';

interface AnnotationCanvasProps {
    currentTask: Task | null;
    imageUrl: string | null;
    isLoading: boolean;
    onImageLoad: () => void;
    onImageError: () => void;
    onComplete: () => void;
}

export const AnnotationCanvas = ({
    currentTask,
    imageUrl,
    isLoading,
    onImageLoad,
    onImageError,
    onComplete,
}: AnnotationCanvasProps) => {
    if (!currentTask || !imageUrl) {
        return (
            <div className="annotation-canvas-full">
                <div className="annotation-canvas__loading">Loading image...</div>
            </div>
        );
    }

    return (
        <div className="annotation-canvas-full">
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

                {/* Image Display */}
                <img
                    src={imageUrl}
                    alt={currentTask.image_id}
                    className="annotation-canvas__image"
                    onLoad={onImageLoad}
                    onError={onImageError}
                    style={{ display: isLoading ? 'none' : 'block' }}
                />

                {isLoading && (
                    <div className="annotation-canvas__loading">Loading image...</div>
                )}

                {/* Overlay - Placeholder for Canvas Tools */}
                <div className="annotation-canvas__overlay">
                    <p>🎨 Canvas annotation tools will be implemented here</p>
                    <button
                        className="btn btn--primary"
                        onClick={onComplete}
                        style={{ marginTop: 'var(--spacing-md)' }}
                    >
                        ✓ Complete Task (Test)
                    </button>
                    <p className="annotation-canvas__overlay-hint">
                        Use ← → or A/D to navigate • ESC to exit
                    </p>
                </div>
            </div>
        </div>
    );
};