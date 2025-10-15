import React, { createContext, useContext, useEffect, useMemo, useRef } from "react";

type ModKey = "ctrl" | "meta" | "shift" | "alt";
export type Combo = string; // e.g. "mod+b", "shift+mod+k"
export type Scope = "global" | string;

export interface HotkeyOptions {
    scope?: Scope;                   // default "global"
    preventDefault?: boolean;        // default true
    stopPropagation?: boolean;       // default false
    enabled?: boolean;               // default true
    enableOnForm?: boolean;          // default false (ignore inputs/textareas by default)
    description?: string;            // optional, for future command palette/help
    priority?: number;               // higher wins if duplicates exist
}

type Handler = (e: KeyboardEvent) => void;

interface Registered {
    comboSig: string;
    scope: Scope;
    handler: Handler;
    opts: Required<Omit<HotkeyOptions, "description">> & Pick<HotkeyOptions, "description">;
}

interface HotkeysAPI {
    register: (combo: Combo, handler: Handler, opts?: HotkeyOptions) => () => void;
}

const HotkeysCtx = createContext<HotkeysAPI | null>(null);

const isMac = typeof navigator !== "undefined" && /Mac|iPhone|iPad|iPod/.test(navigator.platform || "");

function keySigFromEvent(e: KeyboardEvent) {
    // we use event.key lowercased; normalize modifiers -> ctrl, meta, shift, alt
    const parts: string[] = [];
    if (e.ctrlKey) parts.push("ctrl");
    if (e.metaKey) parts.push("meta");
    if (e.shiftKey) parts.push("shift");
    if (e.altKey) parts.push("alt");
    // `key` can be e.g. "b", "B", "ArrowLeft"
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key.toLowerCase();
    parts.push(k);
    return parts.join("+");
}

function normalizeCombo(combo: Combo) {
    // supports "mod" which maps to meta on mac, ctrl on others
    const parts = combo.toLowerCase().split("+").map(s => s.trim()).filter(Boolean);
    const mapped: string[] = [];
    for (const p of parts) {
        if (p === "mod") mapped.push(isMac ? "meta" : "ctrl");
        else mapped.push(p);
    }
    // sort modifiers to stable order: alt, ctrl, meta, shift, then key
    const mods: ModKey[] = [];
    let key = "";
    for (const t of mapped) {
        if (["ctrl", "meta", "shift", "alt"].includes(t)) mods.push(t as ModKey);
        else key = t;
    }
    const ordered = ["alt", "ctrl", "meta", "shift"].filter(m => mods.includes(m as ModKey));
    if (!key) throw new Error(`Invalid combo "${combo}" (no key)`);
    return [...ordered, key].join("+");
}

function isEditableTarget(el: EventTarget | null) {
    if (!(el instanceof HTMLElement)) return false;
    const tag = el.tagName.toLowerCase();
    const editable = el.isContentEditable;
    return editable || tag === "input" || tag === "textarea" || tag === "select";
}

export const HotkeysProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // Keep a list; if you need insane perf, bucket by comboSig
    const regs = useRef<Registered[]>([]);

    const api = useMemo<HotkeysAPI>(() => ({
        register: (combo, handler, opts) => {
            const comboSig = normalizeCombo(combo);
            const reg: Registered = {
                comboSig,
                scope: opts?.scope ?? "global",
                handler,
                opts: {
                    scope: opts?.scope ?? "global",
                    preventDefault: opts?.preventDefault ?? true,
                    stopPropagation: opts?.stopPropagation ?? false,
                    enabled: opts?.enabled ?? true,
                    enableOnForm: opts?.enableOnForm ?? false,
                    description: opts?.description,
                    priority: opts?.priority ?? 0,
                },
            };
            regs.current.push(reg);
            // sort by priority descending so highest priority wins
            regs.current.sort((a, b) => b.opts.priority - a.opts.priority);
            return () => {
                regs.current = regs.current.filter(r => r !== reg);
            };
        }
    }), []);

    useEffect(() => {
        const onKeyDown = (e: KeyboardEvent) => {
            if (e.repeat) {
                // You can allow repeats by removing this. Keeping off avoids rapid toggles.
                return;
            }
            const sig = keySigFromEvent(e);

            // Filter eligible regs
            let candidates = regs.current.filter(r => r.opts.enabled && r.comboSig === sig);

            if (!candidates.length) return;

            // Respect form fields unless enableOnForm
            const inForm = isEditableTarget(e.target);
            if (inForm) {
                candidates = candidates.filter(r => r.opts.enableOnForm);
                if (!candidates.length) return;
            }

            // Pick first match (highest priority already sorted)
            const chosen = candidates[0];

            if (chosen?.opts.preventDefault) e.preventDefault();
            if (chosen?.opts.stopPropagation) e.stopPropagation();

            chosen?.handler(e);
        };

        window.addEventListener("keydown", onKeyDown, { capture: true });
        return () => window.removeEventListener("keydown", onKeyDown, { capture: true } as any);
    }, []);

    return <HotkeysCtx.Provider value={api}>{children}</HotkeysCtx.Provider>;
};

export function useHotkeys() {
    const ctx = useContext(HotkeysCtx);
    if (!ctx) throw new Error("useHotkeys must be used inside <HotkeysProvider>");
    return ctx;
}
