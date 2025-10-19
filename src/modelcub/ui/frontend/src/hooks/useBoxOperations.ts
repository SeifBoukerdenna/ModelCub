import { useEffect, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";
import { AnnotationBox } from "@/hooks/useAnnotationState";
import { Box } from "@/lib/api/types";

interface UseBoxOperationsProps {
  datasetName: string | undefined;
  imageId: string | undefined;
  boxes: AnnotationBox[];
  isDirty: boolean;
  onSaveComplete: () => void;
}

export function useBoxOperations({
  datasetName,
  imageId,
  boxes,
  isDirty,
  onSaveComplete,
}: UseBoxOperationsProps) {
  const { showToast } = useToast();
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isSavingRef = useRef(false);

  // Auto-save with debounce
  useEffect(() => {
    if (!isDirty || !datasetName || !imageId) {
      return;
    }

    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Set new timeout for auto-save (300ms debounce)
    saveTimeoutRef.current = setTimeout(async () => {
      if (isSavingRef.current) return;

      try {
        isSavingRef.current = true;
        await saveBoxes();
        onSaveComplete();
      } catch (error) {
        console.error("Auto-save failed:", error);
      } finally {
        isSavingRef.current = false;
      }
    }, 300);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [boxes, isDirty, datasetName, imageId]);

  const saveBoxes = useCallback(async () => {
    if (!datasetName || !imageId) {
      throw new Error("Dataset name or image ID missing");
    }

    // Convert AnnotationBox to Box (remove id field)
    const boxesToSave: Box[] = boxes.map(({ id, ...box }) => box);

    await api.saveAnnotation(datasetName, imageId, boxesToSave);
  }, [datasetName, imageId, boxes]);

  const manualSave = useCallback(async () => {
    if (!datasetName || !imageId) {
      showToast("Cannot save: missing dataset or image", "error");
      return;
    }

    try {
      await saveBoxes();
      onSaveComplete();
      showToast("Annotations saved", "success");
    } catch (error: any) {
      showToast(error.message || "Failed to save annotations", "error");
    }
  }, [saveBoxes, onSaveComplete, showToast, datasetName, imageId]);

  return {
    manualSave,
  };
}
