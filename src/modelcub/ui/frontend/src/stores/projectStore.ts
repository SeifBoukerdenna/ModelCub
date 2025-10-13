import { create } from "zustand";
import type { Project } from "@/lib/api";

interface ProjectState {
  // State
  projects: Project[];
  selectedProjectPath: string | null;
  loading: boolean;
  error: string | null;

  // Actions
  setProjects: (projects: Project[]) => void;
  setSelectedProject: (path: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  hasProject: () => boolean;
}

const STORAGE_KEY = "modelcub_selected_project";

// Persistence helpers
const loadSelectedPath = (): string | null => {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
};

const saveSelectedPath = (path: string | null) => {
  try {
    if (path) {
      localStorage.setItem(STORAGE_KEY, path);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch (e) {
    console.error("Failed to save selected project:", e);
  }
};

// Create store
export const useProjectStore = create<ProjectState>((set, get) => ({
  // Initial state
  projects: [],
  selectedProjectPath: loadSelectedPath(),
  loading: false,
  error: null,

  // Actions
  setProjects: (projects) => set({ projects }),

  setSelectedProject: (path) => {
    saveSelectedPath(path);
    set({ selectedProjectPath: path });
  },

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  // Computed
  hasProject: () => {
    const state = get();
    return state.selectedProjectPath !== null;
  },
}));

// Selectors (optimized for re-renders)
export const selectSelectedProject = (state: ProjectState): Project | null => {
  if (!state.selectedProjectPath) return null;
  return (
    state.projects.find((p) => p.path === state.selectedProjectPath) || null
  );
};

export const selectProjects = (state: ProjectState): Project[] => {
  return state.projects;
};

export const selectLoading = (state: ProjectState): boolean => {
  return state.loading;
};

export const selectError = (state: ProjectState): string | null => {
  return state.error;
};

export const selectHasProject = (state: ProjectState): boolean => {
  return state.selectedProjectPath !== null;
};
