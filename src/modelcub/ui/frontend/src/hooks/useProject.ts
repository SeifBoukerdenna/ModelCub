/**
 * React hook for project data with multi-project support
 */
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Project, LoadingState } from "@/types";

interface UseProjectReturn {
  project: Project | null;
  projects: Project[]; // All available projects
  loading: boolean;
  error: string | null;
  state: LoadingState;
  reload: () => Promise<void>;
  setActiveProject: (project: Project) => void;
}

export function useProject(): UseProjectReturn {
  const [project, setProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [state, setState] = useState<LoadingState>("loading");
  const [error, setError] = useState<string | null>(null);

  const loadProject = async () => {
    try {
      setState("loading");
      setError(null);

      // Step 1: Try to get current project (in working directory)
      const currentResponse = await api.getCurrentProject();

      // Step 2: Always load all available projects
      const projectsResponse = await api.listProjects();
      setProjects(projectsResponse.projects);

      // Step 3: Determine which project to show
      if (currentResponse.project) {
        // Current project exists in working dir
        setProject(currentResponse.project);
      } else if (projectsResponse.projects.length > 0) {
        // No current project, use first available or one marked as current
        const activeProject =
          projectsResponse.projects.find((p) => p.is_current) ||
          projectsResponse.projects[0];
        setProject(activeProject ?? null);
      } else {
        // No projects at all
        setProject(null);
      }

      setState("success");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load project";
      setError(message);
      setState("error");
    }
  };

  useEffect(() => {
    loadProject();
  }, []);

  const setActiveProject = (newProject: Project) => {
    setProject(newProject);
  };

  return {
    project,
    projects,
    loading: state === "loading",
    error,
    state,
    reload: loadProject,
    setActiveProject,
  };
}
