// src/modelcub/ui/frontend/src/stores/projectStore.ts
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { Project } from "@/types";

interface ProjectState {
  // State
  selectedProject: Project | null;
  projects: Project[];
  loading: boolean;
  error: string | null;

  // Actions
  setSelectedProject: (project: Project | null) => void;
  setProjects: (projects: Project[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;

  findProjectByPath: (path: string) => Project | undefined;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      // Initial state
      selectedProject: null,
      projects: [],
      loading: false,
      error: null,

      // Actions
      setSelectedProject: (project) => {
        set({ selectedProject: project, error: null });
        console.log("📌 Selected project:", project?.name || "None");
      },

      setProjects: (projects) => {
        set({ projects });

        // If there's a selected project, make sure it's still in the list
        const { selectedProject } = get();
        if (selectedProject) {
          const stillExists = projects.some(
            (p) => p.path === selectedProject.path
          );
          if (!stillExists) {
            // Selected project was deleted, clear selection
            set({ selectedProject: null });
            console.log(
              "⚠️  Selected project no longer exists, clearing selection"
            );
          } else {
            // Update selected project with fresh data
            const updated = projects.find(
              (p) => p.path === selectedProject.path
            );
            if (updated) {
              set({ selectedProject: updated });
            }
          }
        }
      },

      setLoading: (loading) => set({ loading }),

      setError: (error) => set({ error }),

      clearError: () => set({ error: null }),

      findProjectByPath: (path) => {
        return get().projects.find((p) => p.path === path);
      },
    }),
    {
      name: "modelcub-project-store", // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist selected project (not loading/error states)
        selectedProject: state.selectedProject,
      }),
    }
  )
);

// Selectors for better performance
export const selectSelectedProject = (state: ProjectState) =>
  state.selectedProject;
export const selectProjects = (state: ProjectState) => state.projects;
export const selectLoading = (state: ProjectState) => state.loading;
export const selectError = (state: ProjectState) => state.error;
