/**
 * Simple toast notification system
 */

export type ToastType = "success" | "error" | "info" | "warning";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

type ToastListener = (toasts: Toast[]) => void;

class ToastManager {
  private toasts: Toast[] = [];
  private listeners: Set<ToastListener> = new Set();
  private nextId = 0;

  subscribe(listener: ToastListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((listener) => listener([...this.toasts]));
  }

  show(type: ToastType, message: string, duration = 5000) {
    const id = `toast-${this.nextId++}`;
    const toast: Toast = { id, type, message, duration };

    this.toasts.push(toast);
    this.notify();

    if (duration > 0) {
      setTimeout(() => this.dismiss(id), duration);
    }
  }

  success(message: string, duration?: number) {
    this.show("success", message, duration);
  }

  error(message: string, duration?: number) {
    this.show("error", message, duration);
  }

  info(message: string, duration?: number) {
    this.show("info", message, duration);
  }

  warning(message: string, duration?: number) {
    this.show("warning", message, duration);
  }

  dismiss(id: string) {
    this.toasts = this.toasts.filter((t) => t.id !== id);
    this.notify();
  }

  clear() {
    this.toasts = [];
    this.notify();
  }
}

export const toast = new ToastManager();
