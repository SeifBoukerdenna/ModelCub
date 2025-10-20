import { useEffect, useState } from 'react';
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
            const target = e.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                return;
            }

            if ((e.key === 'Delete' || e.key === 'Backspace') && selectedBoxId) {
                e.preventDefault();
                deleteBox(selectedBoxId);
            }

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

            if (e.key === 'r' || e.key === 'R') {
                e.preventDefault();
                setDrawMode('draw');
            }
            if (e.key === 'e' || e.key === 'E') {
                e.preventDefault();
                setDrawMode('edit');
            }

            if (e.key >= '1' && e.key <= '9') {
                e.preventDefault();
                const classIndex = parseInt(e.key) - 1;
                if (classIndex < classes.length && classes[classIndex]) {
                    const newClassId = classes[classIndex].id;
                    setCurrentClassId(newClassId);
                    onClassChange(newClassId);
                }
            }

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
            {/* Minimal Toolbar - OUTSIDE wrapper */}
            <div style={{
                position: 'absolute',
                top: '16px',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: '6px',
                background: 'rgba(0,0,0,0.85)',
                padding: '6px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                zIndex: 1000,
            }}>
                <button
                    className={`btn btn--sm ${drawMode === 'draw' ? 'btn--primary' : 'btn--secondary'}`}
                    onClick={() => setDrawMode('draw')}
                    title="Draw (R)"
                    style={{ minWidth: '70px' }}
                >
                    Draw
                </button>
                <button
                    className={`btn btn--sm ${drawMode === 'edit' ? 'btn--primary' : 'btn--secondary'}`}
                    onClick={() => setDrawMode('edit')}
                    title="Edit (E)"
                    style={{ minWidth: '70px' }}
                >
                    Edit
                </button>

                {selectedBoxId && (
                    <button
                        className="btn btn--sm btn--danger"
                        onClick={() => deleteBox(selectedBoxId)}
                        title="Delete (Del)"
                    >
                        🗑️
                    </button>
                )}

                <div style={{ width: '1px', background: 'rgba(255,255,255,0.3)', margin: '0 4px' }} />

                <button
                    className="btn btn--sm btn--secondary"
                    onClick={undo}
                    disabled={!canUndo}
                    title="Undo (Ctrl+Z)"
                    style={{ opacity: canUndo ? 1 : 0.5 }}
                >
                    ↶
                </button>
                <button
                    className="btn btn--sm btn--secondary"
                    onClick={redo}
                    disabled={!canRedo}
                    title="Redo (Ctrl+Y)"
                    style={{ opacity: canRedo ? 1 : 0.5 }}
                >
                    ↷
                </button>

                <div style={{ width: '1px', background: 'rgba(255,255,255,0.3)', margin: '0 4px' }} />

                <button
                    className={`btn btn--sm ${showLabels ? 'btn--primary' : 'btn--secondary'}`}
                    onClick={() => setShowLabels(!showLabels)}
                    title="Toggle Labels"
                >
                    🏷️
                </button>
            </div>

            {/* Box count indicator */}
            <div style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                background: 'rgba(0,0,0,0.7)',
                padding: '6px 12px',
                borderRadius: '6px',
                color: 'white',
                fontSize: '12px',
                fontFamily: 'monospace',
                zIndex: 1000,
            }}>
                {boxes.length} box{boxes.length !== 1 ? 'es' : ''}
            </div>

            {/* Save indicator */}
            {isDirty && (
                <div style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    background: 'rgba(255, 165, 0, 0.9)',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    color: 'white',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    zIndex: 1000,
                }}>
                    <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'white',
                        animation: 'pulse 1.5s ease-in-out infinite',
                    }} />
                    Saving...
                </div>
            )}

            <div className="annotation-canvas__wrapper" style={{
                width: '100%',
                height: '100%',
                position: 'relative',
                overflow: 'hidden'
            }}>
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
            </div>
        </div>
    );
};