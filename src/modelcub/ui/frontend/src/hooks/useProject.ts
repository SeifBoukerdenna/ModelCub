// src/modelcub/ui/frontend/src/hooks/useProject.ts
/**
 * React hook for project data with Zustand global state
 */
import { useEffect } from "react";
import { useProjectStore } from "@/stores/projectStore";
import { api } from "@/lib/api";
import type { Project } from "@/types";

interface UseProjectReturn {
  project: Project | null;
  projects: Project[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  setSelectedProject: (project: Project) => void;
  selectProject: (project: Project) => void;
  clearSelection: () => void;
}

export function useProject(): UseProjectReturn {
  const {
    selectedProject,
    projects,
    loading,
    error,
    setSelectedProject,
    setProjects,
    setLoading,
    setError,
    clearError,
  } = useProjectStore();

  const loadProjects = async () => {
    try {
      setLoading(true);
      clearError();

      // Load all available projects
      const response = await api.listProjects();
      setProjects(response.projects);

      // If no project is selected yet, auto-select the first one
      if (!selectedProject && response.projects.length > 0) {
        // Try to find the "current" project (is_current flag)
        const currentProject = response.projects.find((p) => p.is_current);
        setSelectedProject(currentProject ?? response.projects[0] ?? null);
      }

      setLoading(false);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load projects";
      setError(message);
      setLoading(false);
    }
  };

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Alias for better semantics
  const selectProject = (project: Project) => {
    setSelectedProject(project);
  };

  const clearSelection = () => {
    setSelectedProject(null);
  };

  return {
    project: selectedProject,
    projects,
    loading,
    error,
    reload: loadProjects,
    setSelectedProject: selectProject, // Keep old name for compatibility
    selectProject,
    clearSelection,
  };
}
