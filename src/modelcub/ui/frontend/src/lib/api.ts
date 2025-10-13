/**
 * API client for ModelCub backend
 * Path: frontend/src/lib/api.ts
 */
import { useState, useCallback } from "react";
import type { Project } from "@/types";

// ==================== TYPES ====================

export interface Dataset {
  name: string;
  id: string;
  status: string;
  images: number;
  classes: string[];
  path: string;
  created?: string;
  source?: string;
  size_bytes: number;
  size_formatted: string;
}

export interface DatasetDetail extends Dataset {
  train_images: number;
  valid_images: number;
  unlabeled_images: number;
}

export interface ImportDatasetRequest {
  source: string;
  name?: string;
  recursive?: boolean;
  copy_files?: boolean;
  classes?: string[];
}

export interface CreateProjectRequest {
  name: string;
  path?: string;
  force?: boolean;
}

export interface SetConfigRequest {
  key: string;
  value: string | number | boolean;
}

type LoadingState = "idle" | "loading" | "success" | "error";

interface UseAPIState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  state: LoadingState;
}

interface UseAPIResult<T, TArgs extends any[] = []> extends UseAPIState<T> {
  execute: (...args: TArgs) => Promise<T | null>;
  reset: () => void;
}

// ==================== ERROR CLASS ====================

class ModelCubAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "ModelCubAPIError";
  }
}

// ==================== API CLIENT ====================

class ModelCubAPI {
  private readonly baseURL = "/api/v1";
  private currentProjectPath: string | null = null;

  // Alias for backwards compatibility
  setCurrentProject(projectPath: string | null) {
    this.setProjectPath(projectPath);
  }

  setProjectPath(projectPath: string | null) {
    this.currentProjectPath = projectPath;
    console.log("API: Set current project path to:", projectPath);
  }

  getProjectPath(): string | null {
    return this.currentProjectPath;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (this.currentProjectPath) {
        headers["X-Project-Path"] = this.currentProjectPath;
      }

      if (options?.headers) {
        Object.assign(headers, options.headers);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new ModelCubAPIError(
          "API server not responding. Make sure it is running.",
          response.status
        );
      }

      const data = await response.json();

      if (!response.ok || !data.success) {
        const error = data.error || data;
        throw new ModelCubAPIError(
          error.message || error.error || `HTTP ${response.status}`,
          response.status,
          error.details
        );
      }

      return data.data as T;
    } catch (error) {
      if (error instanceof ModelCubAPIError) {
        throw error;
      }

      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new ModelCubAPIError(
          "Cannot connect to API server. Is it running on port 8000?"
        );
      }

      throw new ModelCubAPIError(
        error instanceof Error ? error.message : "Network error"
      );
    }
  }

  // ==================== PROJECT METHODS ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
  }> {
    return this.request("/health");
  }

  async listProjects(): Promise<Project[]> {
    return this.request("/projects");
  }

  async createProject(data: CreateProjectRequest): Promise<Project> {
    return this.request("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProjectByPath(path: string): Promise<Project> {
    return this.request(`/projects/by-path?path=${encodeURIComponent(path)}`);
  }

  async deleteProject(path: string, confirm: boolean = false): Promise<void> {
    return this.request(`/projects/delete?path=${encodeURIComponent(path)}`, {
      method: "DELETE",
      body: JSON.stringify({ confirm }),
    });
  }

  async getProjectConfig(path: string): Promise<any> {
    return this.request(`/projects/config?path=${encodeURIComponent(path)}`);
  }

  async setProjectConfig(path: string, data: SetConfigRequest): Promise<any> {
    return this.request(`/projects/config?path=${encodeURIComponent(path)}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ==================== DATASET METHODS ====================

  async listDatasets(): Promise<Dataset[]> {
    return this.request("/datasets");
  }

  async getDataset(datasetId: string): Promise<DatasetDetail> {
    return this.request(`/datasets/${datasetId}`);
  }

  async importDataset(data: ImportDatasetRequest): Promise<Dataset> {
    return this.request("/datasets/import", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async uploadDataset(file: File, datasetName?: string): Promise<Dataset> {
    const formData = new FormData();
    formData.append("file", file);
    if (datasetName) {
      formData.append("dataset_name", datasetName);
    }

    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    const response = await fetch(`${this.baseURL}/datasets/upload`, {
      method: "POST",
      headers,
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      const error = data.error;
      throw new ModelCubAPIError(
        error?.message || `HTTP ${response.status}`,
        response.status,
        error?.details
      );
    }

    return data.data as Dataset;
  }

  async importDatasetFiles(
    files: FileList,
    name?: string,
    classes?: string[],
    recursive: boolean = true
  ): Promise<Dataset> {
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file) {
        formData.append("files", file, file.webkitRelativePath || file.name);
      }
    }

    if (name) formData.append("name", name);
    if (classes && classes.length > 0) {
      // Send as comma-separated string
      formData.append("classes", classes.join(","));
    }
    formData.append("recursive", String(recursive));

    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    const response = await fetch(`${this.baseURL}/datasets/import-files`, {
      method: "POST",
      headers,
      body: formData,
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new ModelCubAPIError(
        data.error?.message || `HTTP ${response.status}`,
        response.status
      );
    }

    return data.data as Dataset;
  }

  async addClassToDataset(
    datasetId: string,
    className: string
  ): Promise<string[]> {
    const formData = new FormData();
    formData.append("class_name", className);

    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    const response = await fetch(
      `${this.baseURL}/datasets/${encodeURIComponent(datasetId)}/classes`,
      {
        method: "POST",
        headers,
        body: formData,
      }
    );

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new ModelCubAPIError(
        data.error?.message || `HTTP ${response.status}`,
        response.status
      );
    }

    return data.data as string[];
  }

  async removeClassFromDataset(
    datasetId: string,
    className: string
  ): Promise<string[]> {
    return this.request(
      `/datasets/${encodeURIComponent(datasetId)}/classes/${encodeURIComponent(
        className
      )}`,
      {
        method: "DELETE",
      }
    );
  }

  async renameClassInDataset(
    datasetId: string,
    oldName: string,
    newName: string
  ): Promise<string[]> {
    const formData = new FormData();
    formData.append("new_name", newName);

    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    const response = await fetch(
      `${this.baseURL}/datasets/${encodeURIComponent(
        datasetId
      )}/classes/${encodeURIComponent(oldName)}`,
      {
        method: "PUT",
        headers,
        body: formData,
      }
    );

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new ModelCubAPIError(
        data.error?.message || `HTTP ${response.status}`,
        response.status
      );
    }

    return data.data as string[];
  }

  async deleteDataset(datasetName: string): Promise<void> {
    return this.request(`/datasets/${encodeURIComponent(datasetName)}`, {
      method: "DELETE",
    });
  }

  // ==================== MODEL METHODS ====================

  async listModels(): Promise<any[]> {
    return this.request("/models");
  }
}

// ==================== HOOKS ====================

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

// Project Hooks
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
  return useAPI<any, [string]>((path) => api.getProjectConfig(path));
}

export function useSetProjectConfig() {
  return useAPI<any, [string, SetConfigRequest]>((path, data) =>
    api.setProjectConfig(path, data)
  );
}

export function useDeleteProject() {
  return useAPI<void, [string, boolean]>((path, confirm) =>
    api.deleteProject(path, confirm)
  );
}

// Dataset Hooks
export function useListDatasets() {
  return useAPI<Dataset[]>(() => api.listDatasets());
}

export function useGetDataset() {
  return useAPI<DatasetDetail, [string]>((datasetId) =>
    api.getDataset(datasetId)
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

// Model Hooks
export function useListModels() {
  return useAPI<any[]>(() => api.listModels());
}

// ==================== EXPORTS ====================

export const api = new ModelCubAPI();
export { ModelCubAPIError };
export type { UseAPIResult, LoadingState, Project };
