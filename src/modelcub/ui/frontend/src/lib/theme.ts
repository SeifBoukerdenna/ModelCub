/**
 * Theme management system
 */

export type Theme = "light" | "dark" | "system";

const STORAGE_KEY = "modelcub-theme";

class ThemeManager {
  private currentTheme: Theme = "system";
  private listeners = new Set<(theme: Theme) => void>();

  constructor() {
    this.initialize();
  }

  private initialize() {
    // Load saved preference
    const saved = localStorage.getItem(STORAGE_KEY) as Theme | null;
    if (saved && ["light", "dark", "system"].includes(saved)) {
      this.currentTheme = saved;
    }

    // Apply theme
    this.applyTheme();

    // Listen for system theme changes
    if (window.matchMedia) {
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .addEventListener("change", () => {
          if (this.currentTheme === "system") {
            this.applyTheme();
          }
        });
    }
  }

  private getEffectiveTheme(): "light" | "dark" {
    if (this.currentTheme === "system") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return this.currentTheme;
  }

  private applyTheme() {
    const effectiveTheme = this.getEffectiveTheme();
    document.documentElement.setAttribute("data-theme", effectiveTheme);
  }

  getTheme(): Theme {
    return this.currentTheme;
  }

  setTheme(theme: Theme) {
    this.currentTheme = theme;
    localStorage.setItem(STORAGE_KEY, theme);
    this.applyTheme();
    this.notify();
  }

  subscribe(listener: (theme: Theme) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((listener) => listener(this.currentTheme));
  }
}

export const themeManager = new ThemeManager();
