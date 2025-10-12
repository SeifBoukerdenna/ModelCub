/**
 * API client for ModelCub backend
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

class ModelCubAPI {
  private readonly baseURL = "/api";

  /**
   * Make HTTP request to API
   */
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        ...options,
      });

      // Handle non-JSON responses (like when API is down)
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

      // Network errors
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

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request("/health");
  }

  /**
   * List all projects
   */
  async listProjects(): Promise<{
    success: boolean;
    projects: Project[];
    count: number;
  }> {
    return this.request("/projects/"); // Added trailing slash
  }

  /**
   * Get current project
   */
  async getCurrentProject(): Promise<{
    exists: boolean;
    project: Project | null;
  }> {
    return this.request("/projects/current");
  }

  /**
   * Create new project
   */
  async createProject(
    name: string,
    path?: string,
    force = false
  ): Promise<ApiResponse<Project>> {
    return this.request("/projects/", {
      // Added trailing slash
      method: "POST",
      body: JSON.stringify({ name, path, force }),
    });
  }

  /**
   * Delete project
   */
  async deleteProject(path: string, confirm = false): Promise<ApiResponse> {
    return this.request(`/projects/${encodeURIComponent(path)}`, {
      method: "DELETE",
      body: JSON.stringify({ confirm }),
    });
  }

  /**
   * List datasets
   */
  async listDatasets(): Promise<{ datasets: unknown[] }> {
    return this.request("/datasets/");
  }

  /**
   * List models
   */
  async listModels(): Promise<{ models: unknown[] }> {
    return this.request("/models/");
  }
}

export const api = new ModelCubAPI();
export { ModelCubAPIError };
