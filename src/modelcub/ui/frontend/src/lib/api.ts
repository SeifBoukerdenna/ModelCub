/**
 * API client for ModelCub backend
 * Path: frontend/src/lib/api.ts
 */
import type { Project, ApiResponse, ApiError } from "@/types";

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
  copy?: boolean;
}

class ModelCubAPI {
  private readonly baseURL = "/api";
  private currentProjectPath: string | null = null;

  setCurrentProject(projectPath: string | null) {
    this.currentProjectPath = projectPath;
    console.log("API: Set current project path to:", projectPath);
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      // Build headers
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      // Add project path if set
      if (this.currentProjectPath) {
        headers["X-Project-Path"] = this.currentProjectPath;
        console.log(
          "API: Including X-Project-Path header:",
          this.currentProjectPath
        );
      }

      // Merge with any provided headers
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

      if (!response.ok) {
        const error = data as ApiError;
        throw new ModelCubAPIError(
          error.error || `HTTP ${response.status}`,
          response.status,
          error.details
        );
      }

      return data;
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

  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request("/health");
  }

  async listProjects(): Promise<{
    success: boolean;
    projects: Project[];
    count: number;
  }> {
    return this.request("/projects/");
  }

  async getCurrentProject(): Promise<{
    exists: boolean;
    project: Project | null;
  }> {
    return this.request("/projects/current");
  }

  async createProject(
    name: string,
    path?: string,
    force = false
  ): Promise<ApiResponse<Project>> {
    return this.request("/projects/", {
      method: "POST",
      body: JSON.stringify({ name, path, force }),
    });
  }

  async deleteProject(path: string, confirm = false): Promise<ApiResponse> {
    return this.request(`/projects/${encodeURIComponent(path)}`, {
      method: "DELETE",
      body: JSON.stringify({ confirm }),
    });
  }

  async setProjectConfig(
    projectPath: string,
    key: string,
    value: string | number | boolean
  ): Promise<ApiResponse> {
    return this.request(`/projects/${encodeURIComponent(projectPath)}/config`, {
      method: "POST",
      body: JSON.stringify({ key, value }),
    });
  }

  async listDatasets(): Promise<{
    success: boolean;
    datasets: Dataset[];
    count: number;
    message?: string;
  }> {
    return this.request("/datasets/");
  }

  async getDataset(name: string): Promise<{
    success: boolean;
    dataset: DatasetDetail;
  }> {
    return this.request(`/datasets/${encodeURIComponent(name)}`);
  }

  async importDatasetFiles(
    files: FileList,
    name?: string,
    recursive: boolean = true,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<{ dataset: Dataset }>> {
    const formData = new FormData();

    // Add all files
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file) {
        formData.append("files", file, file.webkitRelativePath || file.name);
      }
    }

    // Add metadata
    if (name) {
      formData.append("name", name);
    }
    formData.append("recursive", String(recursive));

    // Build headers (without Content-Type - browser sets it for FormData)
    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener("progress", (e) => {
          if (e.lengthComputable) {
            const progress = Math.round((e.loaded / e.total) * 100);
            onProgress(progress);
          }
        });
      }

      xhr.addEventListener("load", () => {
        try {
          const response = JSON.parse(xhr.responseText);
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(response);
          } else {
            reject(
              new ModelCubAPIError(
                response.detail || response.error || `HTTP ${xhr.status}`,
                xhr.status
              )
            );
          }
        } catch (e) {
          reject(new ModelCubAPIError("Failed to parse response"));
        }
      });

      xhr.addEventListener("error", () => {
        reject(new ModelCubAPIError("Network error"));
      });

      xhr.open("POST", `${this.baseURL}/datasets/import`);

      // Set headers
      Object.entries(headers).forEach(([key, value]) => {
        xhr.setRequestHeader(key, value);
      });

      xhr.send(formData);
    });
  }

  async deleteDataset(
    name: string,
    confirm = false
  ): Promise<{
    success: boolean;
    message: string;
  }> {
    return this.request(
      `/datasets/${encodeURIComponent(name)}?confirm=${confirm}`,
      {
        method: "DELETE",
      }
    );
  }

  async listModels(): Promise<{ models: unknown[] }> {
    return this.request("/models/");
  }
}

export const api = new ModelCubAPI();
export { ModelCubAPIError };
