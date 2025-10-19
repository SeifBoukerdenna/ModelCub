import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Task } from '@/lib/api/types';

interface AnnotationHeaderProps {
    datasetName: string;
    currentIndex: number;
    totalTasks: number;
    completedCount: number;
    tasks: Task[];
    canGoPrevious: boolean;
    canGoNext: boolean;
    onExit: () => void;
    onPrevious: () => void;
    onNext: () => void;
}

export const AnnotationHeader = ({
    datasetName,
    currentIndex,
    totalTasks,
    completedCount,
    tasks,
    canGoPrevious,
    canGoNext,
    onExit,
    onPrevious,
    onNext,
}: AnnotationHeaderProps) => {
    const completionPercentage = Math.round((completedCount / totalTasks) * 100);

    return (
        <div className="annotation-header-compact">
            {/* Left: Exit button and title */}
            <div className="annotation-header-compact__left">
                <button className="btn btn--sm btn--ghost" onClick={onExit} title="Exit (Esc)">
                    <X size={18} />
                </button>
                <span className="annotation-title">Annotate: {datasetName}</span>
            </div>

            {/* Center: Progress */}
            <div className="annotation-header-compact__center">
                <div className="progress-compact-enhanced">
                    <div className="progress-header-info">
                        <span className="progress-position">
                            Image {currentIndex + 1} of {totalTasks}
                        </span>
                        <span className="progress-percentage">
                            {completionPercentage}% Complete
                        </span>
                    </div>
                    <div className="progress-bar-header">
                        <div
                            className="progress-fill-header"
                            style={{ width: `${completionPercentage}%` }}
                        >
                            <div className="progress-shimmer-header"></div>
                        </div>
                        {/* Task indicators */}
                        <div className="task-indicators">
                            {tasks.map((task, idx) => (
                                <div
                                    key={task.task_id}
                                    className={`task-indicator ${task.status === 'completed' ? 'completed' :
                                        idx === currentIndex ? 'current' : 'pending'
                                        }`}
                                    style={{
                                        left: `${(idx / totalTasks) * 100}%`,
                                        width: `${100 / totalTasks}%`
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Right: Navigation */}
            <div className="annotation-header-compact__right">
                <div className="nav-controls">
                    <button
                        className="btn btn--sm btn--secondary"
                        onClick={onPrevious}
                        disabled={!canGoPrevious}
                        title="Previous (←/A)"
                    >
                        <ChevronLeft size={18} />
                        Previous
                    </button>
                    <button
                        className="btn btn--sm btn--primary"
                        onClick={onNext}
                        title="Next (→/D)"
                    >
                        Next
                        <ChevronRight size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};