/**
 * Type-safe API client for ModelCub backend
 */
import { API_CONFIG, ENDPOINTS } from "@/config/api.config";
import type {
  APIResponse,
  Project,
  ProjectConfigFull,
  CreateProjectRequest,
  SetConfigRequest,
  Dataset,
  DatasetDetail,
  ImportDatasetRequest,
  ImageInfo,
  Model,
} from "./types";

class APIError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = "APIError";
  }
}

class APIClient {
  private baseURL: string;
  private currentProjectPath: string | null = null;

  constructor() {
    this.baseURL = API_CONFIG.baseURL;
  }

  /**
   * Set current project path for subsequent requests
   */
  setProjectPath(path: string | null) {
    this.currentProjectPath = path;
    console.log("API: Set project path to:", path);
  }

  /**
   * Get current project path
   */
  getProjectPath(): string | null {
    return this.currentProjectPath;
  }

  /**
   * Make HTTP request with standardized error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...((options.headers as Record<string, string>) || {}),
      };

      // Add project path header if set
      if (this.currentProjectPath) {
        headers["X-Project-Path"] = this.currentProjectPath;
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      const contentType = response.headers.get("content-type");
      if (!contentType?.includes("application/json")) {
        throw new APIError(
          "API server not responding. Make sure it is running.",
          "CONNECTION_ERROR",
          response.status
        );
      }

      const data: APIResponse<T> = await response.json();

      if (!response.ok || !data.success) {
        const error = data.error;
        throw new APIError(
          error?.message || `HTTP ${response.status}`,
          error?.code,
          response.status,
          error?.details
        );
      }

      return data.data as T;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }

      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new APIError(
          "Cannot connect to API server. Is it running on port 8000?",
          "CONNECTION_ERROR"
        );
      }

      throw new APIError(
        error instanceof Error ? error.message : "Unknown error",
        "UNKNOWN_ERROR"
      );
    }
  }

  // ==================== PROJECT METHODS ====================

  async listProjects(): Promise<Project[]> {
    return this.request<Project[]>(ENDPOINTS.projects);
  }

  async createProject(data: CreateProjectRequest): Promise<Project> {
    return this.request<Project>(ENDPOINTS.projects, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProjectByPath(path: string): Promise<Project> {
    return this.request<Project>(
      `${ENDPOINTS.projectByPath}?path=${encodeURIComponent(path)}`
    );
  }

  async getProjectConfig(path: string): Promise<ProjectConfigFull> {
    return this.request<ProjectConfigFull>(
      `${ENDPOINTS.projectConfig}?path=${encodeURIComponent(path)}`
    );
  }

  async setProjectConfig(
    path: string,
    data: SetConfigRequest
  ): Promise<ProjectConfigFull> {
    return this.request<ProjectConfigFull>(
      `${ENDPOINTS.projectConfig}?path=${encodeURIComponent(path)}`,
      {
        method: "POST",
        body: JSON.stringify(data),
      }
    );
  }

  async deleteProject(path: string, confirm: boolean = false): Promise<void> {
    return this.request<void>(
      `${ENDPOINTS.projectDelete}?path=${encodeURIComponent(path)}`,
      {
        method: "DELETE",
        body: JSON.stringify({ confirm }),
      }
    );
  }

  // ==================== DATASET METHODS ====================

  async listDatasets(): Promise<Dataset[]> {
    return this.request<Dataset[]>(ENDPOINTS.datasets);
  }

  async getDataset(datasetId: string): Promise<DatasetDetail> {
    return this.request<DatasetDetail>(ENDPOINTS.datasetDetail(datasetId));
  }

  async importDataset(data: ImportDatasetRequest): Promise<Dataset> {
    return this.request<Dataset>(ENDPOINTS.datasetImport, {
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

    // Special handling for file upload
    const headers: Record<string, string> = {};
    if (this.currentProjectPath) {
      headers["X-Project-Path"] = this.currentProjectPath;
    }

    const response = await fetch(`${this.baseURL}${ENDPOINTS.datasetUpload}`, {
      method: "POST",
      headers,
      body: formData,
    });

    const data: APIResponse<Dataset> = await response.json();

    if (!response.ok || !data.success) {
      const error = data.error;
      throw new APIError(
        error?.message || `HTTP ${response.status}`,
        error?.code,
        response.status,
        error?.details
      );
    }

    return data.data as Dataset;
  }

  async listDatasetImages(
    datasetId: string,
    params?: { split?: string; limit?: number; offset?: number }
  ): Promise<ImageInfo[]> {
    const queryParams = new URLSearchParams();
    if (params?.split) queryParams.set("split", params.split);
    if (params?.limit) queryParams.set("limit", params.limit.toString());
    if (params?.offset) queryParams.set("offset", params.offset.toString());

    const query = queryParams.toString();
    const endpoint = `${ENDPOINTS.datasetImages(datasetId)}${
      query ? `?${query}` : ""
    }`;

    return this.request<ImageInfo[]>(endpoint);
  }

  // ==================== MODEL METHODS ====================

  async listModels(): Promise<Model[]> {
    return this.request<Model[]>(ENDPOINTS.models);
  }

  async getModel(modelId: string): Promise<Model> {
    return this.request<Model>(ENDPOINTS.modelDetail(modelId));
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
  }> {
    return this.request<{ status: string; service: string; version: string }>(
      ENDPOINTS.health
    );
  }
}

// Export singleton instance
export const api = new APIClient();
export { APIError };
