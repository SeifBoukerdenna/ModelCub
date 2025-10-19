/**
 * Coordinate transformation utilities for annotation canvas.
 *
 * YOLO format: normalized center coordinates (0-1 range)
 * - x, y: center point
 * - w, h: width and height
 *
 * Screen format: pixel coordinates
 * - x, y: top-left corner
 * - width, height: dimensions in pixels
 */

export interface YOLOBox {
  class_id: number;
  x: number; // center x (0-1)
  y: number; // center y (0-1)
  w: number; // width (0-1)
  h: number; // height (0-1)
}

export interface ScreenBox {
  x: number; // top-left x (pixels)
  y: number; // top-left y (pixels)
  width: number; // width (pixels)
  height: number; // height (pixels)
  class_id: number;
}

export interface ImageDimensions {
  width: number;
  height: number;
}

/**
 * Convert YOLO normalized coordinates to screen pixel coordinates.
 */
export function yoloToScreen(
  box: YOLOBox,
  imageDimensions: ImageDimensions
): ScreenBox {
  const { width: imgWidth, height: imgHeight } = imageDimensions;

  // Convert center coordinates to top-left
  const screenWidth = box.w * imgWidth;
  const screenHeight = box.h * imgHeight;
  const screenX = box.x * imgWidth - screenWidth / 2;
  const screenY = box.y * imgHeight - screenHeight / 2;

  return {
    x: screenX,
    y: screenY,
    width: screenWidth,
    height: screenHeight,
    class_id: box.class_id,
  };
}

/**
 * Convert screen pixel coordinates to YOLO normalized coordinates.
 */
export function screenToYolo(
  box: ScreenBox,
  imageDimensions: ImageDimensions
): YOLOBox {
  const { width: imgWidth, height: imgHeight } = imageDimensions;

  // Normalize dimensions
  const normalizedWidth = box.width / imgWidth;
  const normalizedHeight = box.height / imgHeight;

  // Convert top-left to center coordinates
  const centerX = (box.x + box.width / 2) / imgWidth;
  const centerY = (box.y + box.height / 2) / imgHeight;

  return {
    class_id: box.class_id,
    x: clamp(centerX, 0, 1),
    y: clamp(centerY, 0, 1),
    w: clamp(normalizedWidth, 0, 1),
    h: clamp(normalizedHeight, 0, 1),
  };
}

/**
 * Clamp a value between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * Validate if box coordinates are within bounds.
 */
export function isValidBox(box: YOLOBox): boolean {
  return (
    box.x >= 0 &&
    box.x <= 1 &&
    box.y >= 0 &&
    box.y <= 1 &&
    box.w > 0 &&
    box.w <= 1 &&
    box.h > 0 &&
    box.h <= 1
  );
}

/**
 * Clamp box to image bounds.
 */
export function clampBoxToImage(
  box: ScreenBox,
  imageDimensions: ImageDimensions
): ScreenBox {
  const { width: imgWidth, height: imgHeight } = imageDimensions;

  const x = clamp(box.x, 0, imgWidth);
  const y = clamp(box.y, 0, imgHeight);
  const width = clamp(box.width, 0, imgWidth - x);
  const height = clamp(box.height, 0, imgHeight - y);

  return { ...box, x, y, width, height };
}

/**
 * Get class color with consistent hashing.
 */
export function getClassColor(classId: number): string {
  const colors = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#FFA07A",
    "#98D8C8",
    "#F7DC6F",
    "#BB8FCE",
    "#85C1E2",
    "#F8B739",
    "#52B788",
    "#FF6F91",
    "#C9ADA7",
    "#9D84B7",
    "#FFB4A2",
    "#B5E7E7",
  ];
  return colors[classId % colors.length] ?? "";
}

/**
 * Check if point is inside box (for hit detection).
 */
export function pointInBox(
  pointX: number,
  pointY: number,
  box: ScreenBox
): boolean {
  return (
    pointX >= box.x &&
    pointX <= box.x + box.width &&
    pointY >= box.y &&
    pointY <= box.y + box.height
  );
}
