import { useEffect } from "react";

interface KeyboardHandlers {
  onNext: () => void;
  onPrevious: () => void;
  onExit: () => void;
  onSave?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
}

export const useAnnotationKeyboard = (handlers: KeyboardHandlers) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;

      // Don't trigger shortcuts when typing in inputs
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
        return;
      }

      switch (e.key) {
        case "ArrowRight":
        case "d":
        case "D":
          e.preventDefault();
          handlers.onNext();
          break;

        case "ArrowLeft":
        case "a":
        case "A":
          e.preventDefault();
          handlers.onPrevious();
          break;

        case "Escape":
          e.preventDefault();
          handlers.onExit();
          break;

        case "s":
        case "S":
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handlers.onSave?.();
          }
          break;

        case "z":
        case "Z":
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            if (e.shiftKey) {
              handlers.onRedo?.();
            } else {
              handlers.onUndo?.();
            }
          }
          break;

        case "y":
        case "Y":
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handlers.onRedo?.();
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handlers]);
};
