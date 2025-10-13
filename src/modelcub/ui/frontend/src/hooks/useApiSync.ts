/**
 * Hook to sync API client with Zustand store
 * Automatically sets project path in API client when selected project changes
 */
import { useEffect } from "react";
import { api } from "@/lib/api";
import { useProjectStore, selectSelectedProject } from "@/stores/projectStore";

export function useApiSync() {
  const selectedProject = useProjectStore(selectSelectedProject);

  useEffect(() => {
    if (selectedProject) {
      api.setProjectPath(selectedProject.path);
    } else {
      api.setProjectPath(null);
    }
  }, [selectedProject?.path]);
}
