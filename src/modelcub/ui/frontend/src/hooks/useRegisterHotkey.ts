import { useEffect } from "react";
import { Combo, HotkeyOptions, useHotkeys } from "../hotkeys/HotkeysProvider";

export function useRegisterHotkey(
  combo: Combo,
  handler: (e: KeyboardEvent) => void,
  opts?: HotkeyOptions
) {
  const { register } = useHotkeys();

  useEffect(
    () => register(combo, handler, opts),
    [combo, handler, JSON.stringify(opts)]
  );
}
