import { create } from "zustand";
import type { Project } from "@/types";

interface ProjectState {
  projects: Project[];
  selectedProjectPath: string | null;
  setProjects: (projects: Project[]) => void;
  setSelectedProject: (path: string | null) => void;
}

const STORAGE_KEY = "modelcub_selected_project";

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

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  selectedProjectPath: loadSelectedPath(),
  setProjects: (projects) => set({ projects }),
  setSelectedProject: (path) => {
    saveSelectedPath(path);
    set({ selectedProjectPath: path });
  },
}));

export const selectSelectedProject = (state: ProjectState): Project | null => {
  if (!state.selectedProjectPath) return null;
  return (
    state.projects.find((p) => p.path === state.selectedProjectPath) || null
  );
};

export const selectProjects = (state: ProjectState): Project[] => {
  return state.projects;
};
