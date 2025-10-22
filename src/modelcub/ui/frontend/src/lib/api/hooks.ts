/**
 * React hooks for API calls
 */
import { useState, useCallback } from "react";
import { api } from "./index";
import type {
  Project,
  CreateProjectRequest,
  ProjectConfigFull,
  SetConfigRequest,
  Dataset,
  DatasetDetail,
  ImportDatasetRequest,
  ImageInfo,
  Model,
} from "./types";

type LoadingState = "idle" | "loading" | "success" | "error";

interface UseAPIState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  state: LoadingState;
}

export interface UseAPIResult<T, TArgs extends any[] = []>
  extends UseAPIState<T> {
  execute: (...args: TArgs) => Promise<T | null>;
  reset: () => void;
}

function useAPI<T, TArgs extends any[] = []>(
  apiCall: (...args: TArgs) => Promise<T>
): UseAPIResult<T, TArgs> {
  const [state, setState] = useState<UseAPIState<T>>({
    data: null,
    loading: false,
    error: null,
    state: "idle",
  });

  const execute = useCallback(
    async (...args: TArgs): Promise<T | null> => {
      setState({ data: null, loading: true, error: null, state: "loading" });

      try {
        const result = await apiCall(...args);
        setState({
          data: result,
          loading: false,
          error: null,
          state: "success",
        });
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        setState({
          data: null,
          loading: false,
          error: errorMessage,
          state: "error",
        });
        return null;
      }
    },
    [apiCall]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null, state: "idle" });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// ==================== PROJECT HOOKS ====================

export function useListProjects() {
  return useAPI<Project[]>(() => api.listProjects());
}

export function useCreateProject() {
  return useAPI<Project, [CreateProjectRequest]>((data) =>
    api.createProject(data)
  );
}

export function useGetProjectByPath() {
  return useAPI<Project, [string]>((path) => api.getProjectByPath(path));
}

export function useGetProjectConfig() {
  return useAPI<ProjectConfigFull, [string]>((path) =>
    api.getProjectConfig(path)
  );
}

export function useSetProjectConfig() {
  return useAPI<ProjectConfigFull, [string, SetConfigRequest]>((path, data) =>
    api.setProjectConfig(path, data)
  );
}

export function useDeleteProject() {
  return useAPI<void, [string, boolean]>((path, confirm) =>
    api.deleteProject(path, confirm)
  );
}

// ==================== DATASET HOOKS ====================

export function useListDatasets() {
  return useAPI<Dataset[]>(() => api.listDatasets());
}

export function useGetDataset() {
  return useAPI<DatasetDetail, [string, boolean?, string?, number?, number?]>(
    (datasetName, includeImages, split, limit, offset) =>
      api.getDataset(datasetName, includeImages, split, limit, offset)
  );
}

export function useImportDataset() {
  return useAPI<Dataset, [ImportDatasetRequest]>((data) =>
    api.importDataset(data)
  );
}

export function useUploadDataset() {
  return useAPI<Dataset, [File, string?]>((file, datasetName) =>
    api.uploadDataset(file, datasetName)
  );
}

export function useListDatasetImages() {
  return useAPI<
    ImageInfo[],
    [string, { split?: string; limit?: number; offset?: number }?]
  >((datasetId, params) => api.listDatasetImages(datasetId, params));
}

// ==================== MODEL HOOKS ====================

export function useListModels() {
  return useAPI<Model[]>(() => api.listModels());
}

export function useGetModel() {
  return useAPI<Model, [string]>((modelId) => api.getModel(modelId));
}

// ==================== UTILITY HOOKS ====================

export function useHealthCheck() {
  return useAPI<{ status: string; service: string; version: string }>(() =>
    api.healthCheck()
  );
}
