type ToastType = "success" | "error" | "info" | "warning";

interface ToastOptions {
  duration?: number;
}

export const useToast = () => {
  const showToast = (
    message: string,
    type: ToastType = "info",
    options?: ToastOptions
  ) => {
    const duration = options?.duration || 3000;

    // Dispatch custom event that Toast component will listen to
    const event = new CustomEvent("show-toast", {
      detail: { message, type, duration },
    });
    window.dispatchEvent(event);
  };

  return { showToast };
};
