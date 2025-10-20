import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Stage, Layer, Image as KonvaImage, Rect, Transformer, Text } from 'react-konva';
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
    showLabels: boolean;
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
    showLabels,
    onBoxAdd,
    onBoxUpdate,
    onBoxSelect,
    classes,
}: KonvaAnnotationCanvasProps) => {
    const [image] = useImage(imageUrl);
    const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 });
    const [imageDimensions, setImageDimensions] = useState<ImageDimensions | null>(null);
    const [imageOffset, setImageOffset] = useState({ x: 0, y: 0 });
    const stageRef = useRef<Konva.Stage>(null);
    const transformerRef = useRef<Konva.Transformer>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Drawing state
    const [isDrawing, setIsDrawing] = useState(false);
    const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
    const [currentBox, setCurrentBox] = useState<ScreenBox | null>(null);

    // Update canvas size
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

    // Calculate scaled image dimensions and offset to center
    useEffect(() => {
        if (image && containerRef.current) {
            const containerWidth = containerRef.current.offsetWidth;
            const containerHeight = containerRef.current.offsetHeight;

            const imageAspect = image.width / image.height;
            const containerAspect = containerWidth / containerHeight;

            let displayWidth, displayHeight;

            if (imageAspect > containerAspect) {
                displayWidth = containerWidth * 0.9;
                displayHeight = displayWidth / imageAspect;
            } else {
                displayHeight = containerHeight * 0.9;
                displayWidth = displayHeight * imageAspect;
            }

            // Calculate offset to center the image
            const offsetX = (containerWidth - displayWidth) / 2;
            const offsetY = (containerHeight - displayHeight) / 2;

            setImageDimensions({ width: displayWidth, height: displayHeight });
            setImageOffset({ x: offsetX, y: offsetY });
        }
    }, [image, canvasSize]);

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

            // Adjust for image offset
            const adjustedX = point.x - imageOffset.x;
            const adjustedY = point.y - imageOffset.y;

            setIsDrawing(true);
            setDrawStart({ x: adjustedX, y: adjustedY });
            setCurrentBox({
                x: adjustedX,
                y: adjustedY,
                width: 0,
                height: 0,
                class_id: currentClassId,
            });
        },
        [drawMode, currentClassId, imageOffset]
    );

    const handleMouseMove = useCallback(
        (e: Konva.KonvaEventObject<MouseEvent>) => {
            if (!isDrawing || !drawStart || !imageDimensions) return;

            const stage = e.target.getStage();
            if (!stage) return;

            const point = stage.getPointerPosition();
            if (!point) return;

            // Adjust for image offset
            const adjustedX = point.x - imageOffset.x;
            const adjustedY = point.y - imageOffset.y;

            const width = adjustedX - drawStart.x;
            const height = adjustedY - drawStart.y;

            setCurrentBox({
                x: width < 0 ? adjustedX : drawStart.x,
                y: height < 0 ? adjustedY : drawStart.y,
                width: Math.abs(width),
                height: Math.abs(height),
                class_id: currentClassId,
            });
        },
        [isDrawing, drawStart, currentClassId, imageDimensions, imageOffset]
    );

    const handleMouseUp = useCallback(() => {
        if (!isDrawing || !currentBox || !imageDimensions) {
            setIsDrawing(false);
            setCurrentBox(null);
            setDrawStart(null);
            return;
        }

        if (currentBox.width < 10 || currentBox.height < 10) {
            setIsDrawing(false);
            setCurrentBox(null);
            setDrawStart(null);
            return;
        }

        const clampedBox = clampBoxToImage(currentBox, imageDimensions);
        const yoloBox = screenToYolo(clampedBox, imageDimensions);
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
            node.scaleX(1);
            node.scaleY(1);

            const screenBox: ScreenBox = {
                x: node.x() - imageOffset.x,
                y: node.y() - imageOffset.y,
                width: node.width() * scaleX,
                height: node.height() * scaleY,
                class_id: currentClassId,
            };

            const clampedBox = clampBoxToImage(screenBox, imageDimensions);
            const yoloBox = screenToYolo(clampedBox, imageDimensions);
            onBoxUpdate(id, yoloBox);
        },
        [imageDimensions, onBoxUpdate, currentClassId, imageOffset]
    );

    const handleStageClick = useCallback(
        (e: Konva.KonvaEventObject<MouseEvent>) => {
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
                <Layer>
                    <KonvaImage
                        image={image}
                        x={imageOffset.x}
                        y={imageOffset.y}
                        width={imageDimensions.width}
                        height={imageDimensions.height}
                    />
                </Layer>

                <Layer>
                    {boxes.map((box) => {
                        const screenBox = yoloToScreen(box, imageDimensions);
                        const isSelected = box.id === selectedBoxId;
                        const color = getClassColor(box.class_id);
                        const className = classes.find(c => c.id === box.class_id)?.name || `Class ${box.class_id}`;

                        return (
                            <React.Fragment key={box.id}>
                                <Rect
                                    id={box.id}
                                    x={screenBox.x + imageOffset.x}
                                    y={screenBox.y + imageOffset.y}
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
                                            x: node.x() - imageOffset.x,
                                            y: node.y() - imageOffset.y,
                                            width: node.width(),
                                            height: node.height(),
                                            class_id: box.class_id,
                                        };
                                        const clampedBox = clampBoxToImage(screenBox, imageDimensions);
                                        const yoloBox = screenToYolo(clampedBox, imageDimensions);
                                        onBoxUpdate(box.id, yoloBox);
                                    }}
                                />
                                {showLabels && (
                                    <Text
                                        x={screenBox.x + imageOffset.x}
                                        y={screenBox.y + imageOffset.y - 20}
                                        text={className}
                                        fontSize={14}
                                        fontFamily="sans-serif"
                                        fill={color}
                                        padding={4}
                                        shadowColor="black"
                                        shadowBlur={4}
                                        shadowOpacity={0.8}
                                    />
                                )}
                            </React.Fragment>
                        );
                    })}

                    {currentBox && (
                        <Rect
                            x={currentBox.x + imageOffset.x}
                            y={currentBox.y + imageOffset.y}
                            width={currentBox.width}
                            height={currentBox.height}
                            stroke={getClassColor(currentClassId)}
                            strokeWidth={2}
                            fill="transparent"
                            dash={[4, 4]}
                        />
                    )}

                    {drawMode === 'edit' && (
                        <Transformer
                            ref={transformerRef}
                            boundBoxFunc={(oldBox, newBox) => {
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