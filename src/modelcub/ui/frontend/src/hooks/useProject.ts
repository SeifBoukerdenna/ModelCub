/**
 * Custom hook for accessing project data
 *
 * Path: frontend/src/hooks/useProject.ts
 */
import {
  useProjectStore,
  selectSelectedProject,
  selectProjects,
  selectLoading,
  selectError,
  selectHasProject,
} from "@/stores/projectStore";
import type { Project } from "@/types";

export interface UseProjectReturn {
  // Current/selected project
  project: Project | null;
  selectedProject: Project | null; // Alias for clarity
  hasProject: boolean;

  // All projects
  projects: Project[];

  // Loading states
  loading: boolean;
  error: string | null;

  // Actions
  setSelectedProject: (project: Project | null) => void;
  setProjects: (projects: Project[]) => void;
}

/**
 * Hook to access current project and project list
 * Uses Zustand selectors for optimized re-renders
 */
export function useProject(): UseProjectReturn {
  const selectedProject = useProjectStore(selectSelectedProject);
  const projects = useProjectStore(selectProjects);
  const loading = useProjectStore(selectLoading);
  const error = useProjectStore(selectError);
  const hasProject = useProjectStore(selectHasProject);

  const setSelectedProject = useProjectStore(
    (state) => state.setSelectedProject
  );
  const setProjects = useProjectStore((state) => state.setProjects);

  return {
    project: selectedProject,
    selectedProject, // Alias for clarity
    hasProject,
    projects,
    loading,
    error,
    setSelectedProject,
    setProjects,
  };
}
