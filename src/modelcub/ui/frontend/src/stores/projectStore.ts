/**
 * Zustand store for project state management
 *
 * Path: frontend/src/stores/projectStore.ts
 */
import { create } from "zustand";
import type { Project } from "@/types";

interface ProjectStore {
  // State
  projects: Project[];
  selectedProject: Project | null; // Renamed from currentProject
  loading: boolean;
  error: string | null;

  // Actions
  setProjects: (projects: Project[]) => void;
  setSelectedProject: (project: Project | null) => void; // Renamed from setCurrentProject
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed getters (kept for backward compatibility)
  getCurrentProject: () => Project | null;
  hasCurrentProject: () => boolean;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  // Initial state
  projects: [],
  selectedProject: null,
  loading: false,
  error: null,

  // Actions
  setProjects: (projects) => {
    set({ projects });

    // Auto-set selected project to the first one marked as current
    const currentProj = projects.find((p) => p.is_current);
    if (currentProj) {
      set({ selectedProject: currentProj });
    }
  },

  setSelectedProject: (project) => set({ selectedProject: project }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  // Computed getters (backward compatibility)
  getCurrentProject: () => get().selectedProject,

  hasCurrentProject: () => get().selectedProject !== null,
}));

// Selector functions for optimized re-renders
export const selectSelectedProject = (state: ProjectStore) =>
  state.selectedProject;
export const selectProjects = (state: ProjectStore) => state.projects;
export const selectLoading = (state: ProjectStore) => state.loading;
export const selectError = (state: ProjectStore) => state.error;
export const selectHasProject = (state: ProjectStore) =>
  state.selectedProject !== null;

// Backward compatibility aliases
export const selectCurrentProject = selectSelectedProject;
