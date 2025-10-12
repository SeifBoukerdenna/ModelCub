import { useEffect, useState } from "react";
import { themeManager, Theme } from "@/lib/theme";

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(themeManager.getTheme());

  useEffect(() => {
    const unsubscribe = themeManager.subscribe(setTheme);
    return unsubscribe;
  }, []);

  const toggleTheme = () => {
    const current = themeManager.getTheme();
    const next: Theme =
      current === "light" ? "dark" : current === "dark" ? "system" : "light";
    themeManager.setTheme(next);
  };

  const setThemeMode = (mode: Theme) => {
    themeManager.setTheme(mode);
  };

  return {
    theme,
    setTheme: setThemeMode,
    toggleTheme,
  };
}
