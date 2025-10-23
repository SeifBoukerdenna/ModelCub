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
  isNull?: boolean;
}

export function useBoxOperations({
  datasetName,
  imageId,
  boxes,
  isDirty,
  onSaveComplete,
  isNull = false,
}: UseBoxOperationsProps) {
  const { showToast } = useToast();
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isSavingRef = useRef(false);

  // Auto-save with debounce
  useEffect(() => {
    if (!isDirty || !datasetName || !imageId) {
      return;
    }

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

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
  }, [boxes, isDirty, datasetName, imageId, isNull]);

  const saveBoxes = useCallback(async () => {
    if (!datasetName || !imageId) {
      throw new Error("Dataset name or image ID missing");
    }

    const boxesToSave: Box[] = boxes.map(({ id, ...box }) => box);
    await api.saveAnnotation(datasetName, imageId, boxesToSave, isNull);
  }, [datasetName, imageId, boxes, isNull]);

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

  const markAsNull = useCallback(async () => {
    if (!datasetName || !imageId) {
      showToast("Cannot mark as null: missing dataset or image", "error");
      return;
    }

    try {
      await api.saveAnnotation(datasetName, imageId, [], true);
      onSaveComplete();
      showToast("Marked as null (negative example)", "success");
    } catch (error: any) {
      showToast(error.message || "Failed to mark as null", "error");
    }
  }, [datasetName, imageId, onSaveComplete, showToast]);

  return {
    manualSave,
    markAsNull,
  };
}
