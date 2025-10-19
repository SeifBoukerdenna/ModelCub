import { useRef, useState, useEffect, useCallback } from 'react';
import { Stage, Layer, Image as KonvaImage, Rect, Transformer } from 'react-konva';
import useImage from 'use-image';
import Konva from 'konva';
import {
    yoloToScreen,
    screenToYolo,
    clampBoxToImage,
    getClassColor,
    type ScreenBox,
    type ImageDimensions,
} from '@/lib/canvas/coordinates';
import { AnnotationBox } from '@/hooks/useAnnotationState';

interface KonvaAnnotationCanvasProps {
    imageUrl: string;
    boxes: AnnotationBox[];
    selectedBoxId: string | null;
    currentClassId: number;
    drawMode: 'draw' | 'edit' | 'view';
    onBoxAdd: (box: { class_id: number; x: number; y: number; w: number; h: number }) => void;
    onBoxUpdate: (id: string, updates: Partial<AnnotationBox>) => void;
    onBoxSelect: (id: string | null) => void;
    classes: Array<{ id: number; name: string }>;
}

export const KonvaAnnotationCanvas = ({
    imageUrl,
    boxes,
    selectedBoxId,
    currentClassId,
    drawMode,
    onBoxAdd,
    onBoxUpdate,
    onBoxSelect,
    classes,
}: KonvaAnnotationCanvasProps) => {
    const [image] = useImage(imageUrl);
    const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
    const [imageDimensions, setImageDimensions] = useState<ImageDimensions | null>(null);
    const stageRef = useRef<Konva.Stage>(null);
    const transformerRef = useRef<Konva.Transformer>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Drawing state
    const [isDrawing, setIsDrawing] = useState(false);
    const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
    const [currentBox, setCurrentBox] = useState<ScreenBox | null>(null);

    // Update canvas size on mount and resize
    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                setCanvasSize({
                    width: containerRef.current.offsetWidth,
                    height: containerRef.current.offsetHeight,
                });
            }
        };

        updateSize();
        window.addEventListener('resize', updateSize);
        return () => window.removeEventListener('resize', updateSize);
    }, []);

    // Set image dimensions
    useEffect(() => {
        if (image) {
            setImageDimensions({ width: image.width, height: image.height });
        }
    }, [image]);

    // Handle transformer attachment
    useEffect(() => {
        if (selectedBoxId && transformerRef.current && drawMode === 'edit') {
            const stage = stageRef.current;
            if (!stage) return;

            const selectedNode = stage.findOne(`#${selectedBoxId}`);
            if (selectedNode) {
                transformerRef.current.nodes([selectedNode]);
                transformerRef.current.getLayer()?.batchDraw();
            }
        } else if (transformerRef.current) {
            transformerRef.current.nodes([]);
            transformerRef.current.getLayer()?.batchDraw();
        }
    }, [selectedBoxId, drawMode]);

    const handleMouseDown = useCallback(
        (e: Konva.KonvaEventObject<MouseEvent>) => {
            if (drawMode !== 'draw') return;

            const stage = e.target.getStage();
            if (!stage) return;

            const point = stage.getPointerPosition();
            if (!point) return;

            setIsDrawing(true);
            setDrawStart(point);
            setCurrentBox({
                x: point.x,
                y: point.y,
                width: 0,
                height: 0,
                class_id: currentClassId,
            });
        },
        [drawMode, currentClassId]
    );

    const handleMouseMove = useCallback(
        (e: Konva.KonvaEventObject<MouseEvent>) => {
            if (!isDrawing || !drawStart || !imageDimensions) return;

            const stage = e.target.getStage();
            if (!stage) return;

            const point = stage.getPointerPosition();
            if (!point) return;

            const width = point.x - drawStart.x;
            const height = point.y - drawStart.y;

            setCurrentBox({
                x: width < 0 ? point.x : drawStart.x,
                y: height < 0 ? point.y : drawStart.y,
                width: Math.abs(width),
                height: Math.abs(height),
                class_id: currentClassId,
            });
        },
        [isDrawing, drawStart, currentClassId, imageDimensions]
    );

    const handleMouseUp = useCallback(() => {
        if (!isDrawing || !currentBox || !imageDimensions) {
            setIsDrawing(false);
            setCurrentBox(null);
            setDrawStart(null);
            return;
        }

        // Minimum box size validation
        if (currentBox.width < 10 || currentBox.height < 10) {
            setIsDrawing(false);
            setCurrentBox(null);
            setDrawStart(null);
            return;
        }

        // Clamp to image bounds
        const clampedBox = clampBoxToImage(currentBox, imageDimensions);

        // Convert to YOLO format
        const yoloBox = screenToYolo(clampedBox, imageDimensions);

        // Add box
        onBoxAdd(yoloBox);

        setIsDrawing(false);
        setCurrentBox(null);
        setDrawStart(null);
    }, [isDrawing, currentBox, imageDimensions, onBoxAdd]);

    const handleBoxClick = useCallback(
        (id: string) => {
            if (drawMode === 'edit') {
                onBoxSelect(id);
            }
        },
        [drawMode, onBoxSelect]
    );

    const handleTransformEnd = useCallback(
        (id: string, node: Konva.Rect) => {
            if (!imageDimensions) return;

            const scaleX = node.scaleX();
            const scaleY = node.scaleY();

            // Reset scale
            node.scaleX(1);
            node.scaleY(1);

            const screenBox: ScreenBox = {
                x: node.x(),
                y: node.y(),
                width: node.width() * scaleX,
                height: node.height() * scaleY,
                class_id: currentClassId, // This should come from the box, but we'll use current for now
            };

            const clampedBox = clampBoxToImage(screenBox, imageDimensions);
            const yoloBox = screenToYolo(clampedBox, imageDimensions);

            onBoxUpdate(id, yoloBox);
        },
        [imageDimensions, onBoxUpdate, currentClassId]
    );

    const handleStageClick = useCallback(
        (e: Konva.KonvaEventObject<MouseEvent>) => {
            // Deselect when clicking on empty space
            if (e.target === e.target.getStage()) {
                onBoxSelect(null);
            }
        },
        [onBoxSelect]
    );

    if (!image || !imageDimensions) {
        return (
            <div ref={containerRef} style={{ width: '100%', height: '100%', background: '#000' }}>
                <div style={{ color: 'white', padding: '20px' }}>Loading image...</div>
            </div>
        );
    }

    return (
        <div ref={containerRef} style={{ width: '100%', height: '100%', background: '#000' }}>
            <Stage
                ref={stageRef}
                width={canvasSize.width}
                height={canvasSize.height}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onClick={handleStageClick}
            >
                {/* Image Layer */}
                <Layer>
                    <KonvaImage
                        image={image}
                        width={imageDimensions.width}
                        height={imageDimensions.height}
                    />
                </Layer>

                {/* Boxes Layer */}
                <Layer>
                    {boxes.map((box) => {
                        const screenBox = yoloToScreen(box, imageDimensions);
                        const isSelected = box.id === selectedBoxId;
                        const color = getClassColor(box.class_id);

                        return (
                            <Rect
                                key={box.id}
                                id={box.id}
                                x={screenBox.x}
                                y={screenBox.y}
                                width={screenBox.width}
                                height={screenBox.height}
                                stroke={color}
                                strokeWidth={isSelected ? 3 : 2}
                                fill="transparent"
                                draggable={drawMode === 'edit' && isSelected}
                                onClick={() => handleBoxClick(box.id)}
                                onTransformEnd={(e) => {
                                    const node = e.target as Konva.Rect;
                                    handleTransformEnd(box.id, node);
                                }}
                                onDragEnd={(e) => {
                                    if (!imageDimensions) return;
                                    const node = e.target as Konva.Rect;
                                    const screenBox: ScreenBox = {
                                        x: node.x(),
                                        y: node.y(),
                                        width: node.width(),
                                        height: node.height(),
                                        class_id: box.class_id,
                                    };
                                    const clampedBox = clampBoxToImage(screenBox, imageDimensions);
                                    const yoloBox = screenToYolo(clampedBox, imageDimensions);
                                    onBoxUpdate(box.id, yoloBox);
                                }}
                            />
                        );
                    })}

                    {/* Current drawing box */}
                    {currentBox && (
                        <Rect
                            x={currentBox.x}
                            y={currentBox.y}
                            width={currentBox.width}
                            height={currentBox.height}
                            stroke={getClassColor(currentClassId)}
                            strokeWidth={2}
                            fill="transparent"
                            dash={[4, 4]}
                        />
                    )}

                    {/* Transformer for editing */}
                    {drawMode === 'edit' && (
                        <Transformer
                            ref={transformerRef}
                            boundBoxFunc={(oldBox, newBox) => {
                                // Minimum size constraint
                                if (newBox.width < 10 || newBox.height < 10) {
                                    return oldBox;
                                }
                                return newBox;
                            }}
                        />
                    )}
                </Layer>
            </Stage>
        </div>
    );
};