/**
 * React hook for project data
 */
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Project, LoadingState } from "@/types";

interface UseProjectReturn {
  project: Project | null;
  loading: boolean;
  error: string | null;
  state: LoadingState;
  reload: () => Promise<void>;
}

export function useProject(): UseProjectReturn {
  const [project, setProject] = useState<Project | null>(null);
  const [state, setState] = useState<LoadingState>("loading");
  const [error, setError] = useState<string | null>(null);

  const loadProject = async () => {
    try {
      setState("loading");
      setError(null);

      const response = await api.getCurrentProject();
      setProject(response.project);

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

  return {
    project,
    loading: state === "loading",
    error,
    state,
    reload: loadProject,
  };
}
