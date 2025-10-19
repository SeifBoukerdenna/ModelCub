import { useEffect, useState } from 'react';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';
import type { Task } from '@/lib/api/types';
import { useAnnotationState } from '@/hooks/useAnnotationState';
import { useBoxOperations } from '@/hooks/useBoxOperations';
import { api } from '@/lib/api';
import { KonvaAnnotationCanvas } from '../canvas/KonvaAnnotationCanvas';

interface AnnotationCanvasProps {
    currentTask: Task | null;
    imageUrl: string | null;
    isLoading: boolean;
    onImageLoad: () => void;
    onImageError: () => void;
    onComplete: () => void;
    datasetName: string | undefined;
    classes: Array<{ id: number; name: string }>;
    currentClassId: number;
    onClassChange: (classId: number) => void;
}

export const AnnotationCanvas = ({
    currentTask,
    imageUrl,
    isLoading,
    onComplete,
    datasetName,
    classes,
    currentClassId,
    onClassChange,
}: AnnotationCanvasProps) => {
    const [showLabels, setShowLabels] = useState(true);

    const {
        boxes,
        selectedBoxId,
        drawMode,
        isDirty,
        canUndo,
        canRedo,
        addBox,
        updateBox,
        deleteBox,
        selectBox,
        setDrawMode,
        setCurrentClassId,
        undo,
        redo,
        markClean,
        setBoxes,
    } = useAnnotationState([], currentClassId);

    // Sync current class ID from parent
    useEffect(() => {
        setCurrentClassId(currentClassId);
    }, [currentClassId, setCurrentClassId]);

    // Load existing annotations when task changes
    useEffect(() => {
        if (!currentTask || !datasetName) return;

        const loadAnnotations = async () => {
            try {
                const annotation = await api.getAnnotation(datasetName, currentTask.image_id);
                setBoxes(annotation.boxes);
            } catch (error) {
                console.error('Failed to load annotations:', error);
                setBoxes([]);
            }
        };

        loadAnnotations();
    }, [currentTask?.image_id, datasetName, setBoxes]);

    // Auto-save
    const { manualSave } = useBoxOperations({
        datasetName,
        imageId: currentTask?.image_id,
        boxes,
        isDirty,
        onSaveComplete: markClean,
    });

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ignore if typing in input/textarea
            const target = e.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                return;
            }

            // Delete selected box
            if ((e.key === 'Delete' || e.key === 'Backspace') && selectedBoxId) {
                e.preventDefault();
                deleteBox(selectedBoxId);
            }

            // Undo/Redo
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z' && !e.shiftKey && canUndo) {
                    e.preventDefault();
                    undo();
                } else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
                    if (canRedo) {
                        e.preventDefault();
                        redo();
                    }
                }
            }

            // Tool shortcuts
            if (e.key === 'r' || e.key === 'R') {
                e.preventDefault();
                setDrawMode('draw');
            }
            if (e.key === 'e' || e.key === 'E') {
                e.preventDefault();
                setDrawMode('edit');
            }

            // Number keys for class selection
            if (e.key >= '1' && e.key <= '9') {
                e.preventDefault();
                const classIndex = parseInt(e.key) - 1;
                if (classIndex < classes.length && classes[classIndex]) {
                    const newClassId = classes[classIndex].id;
                    setCurrentClassId(newClassId);
                    onClassChange(newClassId);
                }
            }

            // Manual save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                manualSave();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [
        selectedBoxId,
        deleteBox,
        canUndo,
        canRedo,
        undo,
        redo,
        setDrawMode,
        classes,
        setCurrentClassId,
        onClassChange,
        manualSave,
    ]);

    if (!currentTask || !imageUrl) {
        return (
            <div className="annotation-canvas-full">
                <div className="annotation-canvas__loading">Loading image...</div>
            </div>
        );
    }

    return (
        <div className="annotation-canvas-full">
            <div className="annotation-canvas__wrapper" style={{
                width: '100%',
                height: '100%',
                position: 'relative',
                overflow: 'hidden'
            }}>
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
                            <Clock size={18} />
                            <span>IN PROGRESS</span>
                        </>
                    )}
                    {currentTask.status === 'failed' && (
                        <>
                            <AlertCircle size={18} />
                            <span>FAILED</span>
                        </>
                    )}
                </div>

                {/* Canvas */}
                {!isLoading && (
                    <KonvaAnnotationCanvas
                        imageUrl={imageUrl}
                        boxes={boxes}
                        selectedBoxId={selectedBoxId}
                        currentClassId={currentClassId}
                        drawMode={drawMode}
                        showLabels={showLabels}
                        onBoxAdd={addBox}
                        onBoxUpdate={updateBox}
                        onBoxSelect={selectBox}
                        classes={classes}
                    />
                )}

                {isLoading && (
                    <div className="annotation-canvas__loading">Loading image...</div>
                )}

                {/* Tool Toolbar */}
                <div style={{
                    position: 'absolute',
                    top: '20px',
                    left: '20px',
                    display: 'flex',
                    gap: '8px',
                    background: 'rgba(0,0,0,0.7)',
                    padding: '8px',
                    borderRadius: '8px',
                }}>
                    <button
                        className={`btn btn--sm ${drawMode === 'draw' ? 'btn--primary' : 'btn--secondary'}`}
                        onClick={() => setDrawMode('draw')}
                        title="Rectangle Tool (R)"
                    >
                        🔲 Draw
                    </button>
                    <button
                        className={`btn btn--sm ${drawMode === 'edit' ? 'btn--primary' : 'btn--secondary'}`}
                        onClick={() => setDrawMode('edit')}
                        title="Edit Tool (E)"
                    >
                        ✏️ Edit
                    </button>
                    {selectedBoxId && (
                        <button
                            className="btn btn--sm btn--danger"
                            onClick={() => deleteBox(selectedBoxId)}
                            title="Delete Selected (Del)"
                        >
                            🗑️ Delete
                        </button>
                    )}
                    <button
                        className="btn btn--sm btn--secondary"
                        onClick={undo}
                        disabled={!canUndo}
                        title="Undo (Ctrl+Z)"
                    >
                        ↶
                    </button>
                    <button
                        className="btn btn--sm btn--secondary"
                        onClick={redo}
                        disabled={!canRedo}
                        title="Redo (Ctrl+Y)"
                    >
                        ↷
                    </button>
                    <div style={{ width: '1px', background: 'rgba(255,255,255,0.3)', margin: '0 4px' }} />
                    <button
                        className={`btn btn--sm ${showLabels ? 'btn--primary' : 'btn--secondary'}`}
                        onClick={() => setShowLabels(!showLabels)}
                        title="Toggle Labels"
                    >
                        🏷️ Labels
                    </button>
                </div>

                {/* Complete Button */}
                <div style={{
                    position: 'absolute',
                    bottom: '20px',
                    right: '20px',
                }}>
                    <button
                        className="btn btn--primary"
                        onClick={onComplete}
                    >
                        ✓ Complete Task (Space)
                    </button>
                </div>

                {/* Info Display */}
                <div style={{
                    position: 'absolute',
                    bottom: '20px',
                    left: '20px',
                    background: 'rgba(0,0,0,0.7)',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '12px',
                }}>
                    <div>Boxes: {boxes.length}</div>
                    {isDirty && <div style={{ color: '#ffa500' }}>● Saving...</div>}
                </div>
            </div>
        </div>
    );
};