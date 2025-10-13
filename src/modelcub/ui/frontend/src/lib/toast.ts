/**
 * Toast notification utility
 * Simple toast notifications for user feedback
 *
 * Path: frontend/src/lib/toast.ts
 */

type ToastType = "success" | "error" | "info" | "warning";

interface ToastOptions {
  duration?: number;
  position?: "top-right" | "top-center" | "bottom-right" | "bottom-center";
}

class Toast {
  private container: HTMLDivElement | null = null;

  private getContainer(): HTMLDivElement {
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = "toast-container";
      this.container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
        pointer-events: none;
      `;
      document.body.appendChild(this.container);
    }
    return this.container;
  }

  private show(message: string, type: ToastType, options: ToastOptions = {}) {
    const { duration = 3000 } = options;
    const container = this.getContainer();

    const toast = document.createElement("div");
    toast.style.cssText = `
      background: ${this.getBackgroundColor(type)};
      color: white;
      padding: 12px 20px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      font-size: 14px;
      font-weight: 500;
      max-width: 400px;
      word-wrap: break-word;
      pointer-events: auto;
      animation: slideIn 0.3s ease-out;
      transition: opacity 0.3s ease-out;
    `;
    toast.textContent = message;

    // Add animation keyframes if not already added
    if (!document.getElementById("toast-styles")) {
      const style = document.createElement("style");
      style.id = "toast-styles";
      style.textContent = `
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
    }

    container.appendChild(toast);

    // Auto remove
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => {
        if (toast.parentNode) {
          container.removeChild(toast);
        }
      }, 300);
    }, duration);
  }

  private getBackgroundColor(type: ToastType): string {
    switch (type) {
      case "success":
        return "#10b981";
      case "error":
        return "#ef4444";
      case "warning":
        return "#f59e0b";
      case "info":
      default:
        return "#3b82f6";
    }
  }

  success(message: string, options?: ToastOptions) {
    this.show(message, "success", options);
  }

  error(message: string, options?: ToastOptions) {
    this.show(message, "error", options);
  }

  info(message: string, options?: ToastOptions) {
    this.show(message, "info", options);
  }

  warning(message: string, options?: ToastOptions) {
    this.show(message, "warning", options);
  }
}

export const toast = new Toast();
