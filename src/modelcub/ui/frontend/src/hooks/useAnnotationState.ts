import { useState, useCallback, useEffect } from "react";
import { YOLOBox } from "@/lib/canvas/coordinates";

export type DrawMode = "draw" | "edit" | "view";

export interface AnnotationBox extends YOLOBox {
  id: string;
}

interface AnnotationState {
  boxes: AnnotationBox[];
  selectedBoxId: string | null;
  drawMode: DrawMode;
  currentClassId: number;
  isDirty: boolean;
  history: AnnotationBox[][];
  historyIndex: number;
}

export function useAnnotationState(
  initialBoxes: YOLOBox[] = [],
  initialClassId: number = 0
) {
  const [state, setState] = useState<AnnotationState>({
    boxes: initialBoxes.map((box, i) => ({ ...box, id: `box-${i}` })),
    selectedBoxId: null,
    drawMode: "draw",
    currentClassId: initialClassId,
    isDirty: false,
    history: [initialBoxes.map((box, i) => ({ ...box, id: `box-${i}` }))],
    historyIndex: 0,
  });

  // Update boxes when initial boxes change (e.g., loading new image)
  useEffect(() => {
    setState((prev) => ({
      ...prev,
      boxes: initialBoxes.map((box, i) => ({ ...box, id: `box-${i}` })),
      selectedBoxId: null,
      isDirty: false,
      history: [initialBoxes.map((box, i) => ({ ...box, id: `box-${i}` }))],
      historyIndex: 0,
    }));
  }, [initialBoxes.length]); // Only reset when number of boxes changes

  const addToHistory = useCallback((boxes: AnnotationBox[]) => {
    setState((prev) => {
      const newHistory = prev.history.slice(0, prev.historyIndex + 1);
      newHistory.push([...boxes]);
      return {
        ...prev,
        history: newHistory,
        historyIndex: newHistory.length - 1,
      };
    });
  }, []);

  const addBox = useCallback(
    (box: YOLOBox) => {
      setState((prev) => {
        const newBox: AnnotationBox = {
          ...box,
          id: `box-${Date.now()}-${Math.random()}`,
        };
        const newBoxes = [...prev.boxes, newBox];
        addToHistory(newBoxes);
        return {
          ...prev,
          boxes: newBoxes,
          selectedBoxId: newBox.id,
          isDirty: true,
        };
      });
    },
    [addToHistory]
  );

  const updateBox = useCallback(
    (id: string, updates: Partial<YOLOBox>) => {
      setState((prev) => {
        const newBoxes = prev.boxes.map((box) =>
          box.id === id ? { ...box, ...updates } : box
        );
        addToHistory(newBoxes);
        return {
          ...prev,
          boxes: newBoxes,
          isDirty: true,
        };
      });
    },
    [addToHistory]
  );

  const deleteBox = useCallback(
    (id: string) => {
      setState((prev) => {
        const newBoxes = prev.boxes.filter((box) => box.id !== id);
        addToHistory(newBoxes);
        return {
          ...prev,
          boxes: newBoxes,
          selectedBoxId: prev.selectedBoxId === id ? null : prev.selectedBoxId,
          isDirty: true,
        };
      });
    },
    [addToHistory]
  );

  const selectBox = useCallback((id: string | null) => {
    setState((prev) => ({
      ...prev,
      selectedBoxId: id,
      drawMode: id ? "edit" : prev.drawMode,
    }));
  }, []);

  const setDrawMode = useCallback((mode: DrawMode) => {
    setState((prev) => ({
      ...prev,
      drawMode: mode,
      selectedBoxId: mode === "draw" ? null : prev.selectedBoxId,
    }));
  }, []);

  const setCurrentClassId = useCallback((classId: number) => {
    setState((prev) => ({
      ...prev,
      currentClassId: classId,
    }));
  }, []);

  const clearSelection = useCallback(() => {
    setState((prev) => ({
      ...prev,
      selectedBoxId: null,
    }));
  }, []);

  const undo = useCallback(() => {
    setState((prev) => {
      if (prev.historyIndex > 0) {
        const newIndex = prev.historyIndex - 1;
        return {
          ...prev,
          boxes: [...(prev.history[newIndex] || [])],
          historyIndex: newIndex,
          isDirty: true,
        };
      }
      return prev;
    });
  }, []);

  const redo = useCallback(() => {
    setState((prev) => {
      if (prev.historyIndex < prev.history.length - 1) {
        const newIndex = prev.historyIndex + 1;
        return {
          ...prev,
          boxes: [...(prev.history[newIndex] || [])],
          historyIndex: newIndex,
          isDirty: true,
        };
      }
      return prev;
    });
  }, []);

  const markClean = useCallback(() => {
    setState((prev) => ({ ...prev, isDirty: false }));
  }, []);

  const setBoxes = useCallback((newBoxes: YOLOBox[]) => {
    const boxesWithIds = newBoxes.map((box, i) => ({
      ...box,
      id: `box-${Date.now()}-${i}`,
    }));
    setState((prev) => ({
      ...prev,
      boxes: boxesWithIds,
      selectedBoxId: null,
      isDirty: false,
      history: [boxesWithIds],
      historyIndex: 0,
    }));
  }, []);

  const canUndo = state.historyIndex > 0;
  const canRedo = state.historyIndex < state.history.length - 1;

  return {
    boxes: state.boxes,
    selectedBoxId: state.selectedBoxId,
    drawMode: state.drawMode,
    currentClassId: state.currentClassId,
    isDirty: state.isDirty,
    canUndo,
    canRedo,
    addBox,
    updateBox,
    deleteBox,
    selectBox,
    setDrawMode,
    setCurrentClassId,
    clearSelection,
    undo,
    redo,
    markClean,
    setBoxes,
  };
}
