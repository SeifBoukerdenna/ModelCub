import { useState, useCallback, useEffect } from "react";
import type { Task } from "@/lib/api/types";

export const useAnnotationNavigation = (tasks: Task[], onExit: () => void) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto-select first incomplete task on load
  useEffect(() => {
    if (tasks.length > 0 && currentIndex === 0) {
      const firstIncomplete = tasks.findIndex(
        (t) => t.status === "pending" || t.status === "in_progress"
      );
      if (firstIncomplete >= 0) {
        setCurrentIndex(firstIncomplete);
      }
    }
  }, [tasks.length]);

  const goToNext = useCallback(() => {
    if (currentIndex < tasks.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      onExit();
    }
  }, [currentIndex, tasks.length, onExit]);

  const goToPrevious = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  }, [currentIndex]);

  const goToIndex = useCallback(
    (index: number) => {
      if (index >= 0 && index < tasks.length) {
        setCurrentIndex(index);
      }
    },
    [tasks.length]
  );

  const currentTask = tasks[currentIndex] || null;
  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < tasks.length - 1;

  return {
    currentIndex,
    currentTask,
    canGoPrevious,
    canGoNext,
    goToNext,
    goToPrevious,
    goToIndex,
  };
};
