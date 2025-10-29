/**
 * ModelCub API Client
 */
import { ENDPOINTS } from "@/config/api.config";

import type {
  Project,
  CreateProjectRequest,
  SetConfigRequest,
  ProjectConfigFull,
  Dataset,
  DatasetDetail,
  ImportDatasetRequest,
  ImageInfo,
  Job,
  Task,
  CreateJobRequest,
  Annotation,
  Box,
  PromotedModel,
  TrainingRun,
  LogsResponse,
  PredictionJob,
  PredictionResult,
  CreatePredictionRequest,
} from "./types";
import { ModelCubAPIError } from "./errors";

export class ModelCubAPI {
  private readonly baseURL = "/api/v1";
  private currentProjectPath: string | null = null;

  setCurrentProject(projectPath: string | null): void {
    this.setProjectPath(projectPath);
  }

  setProjectPath(projectPath: string | null): void {
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
    return this.request<void>("/projects", {
      method: "DELETE",
      body: JSON.stringify({ path, confirm }),
    });
  }

  async getProjectConfig(path: string): Promise<ProjectConfigFull> {
    return this.request(`/projects/config?path=${encodeURIComponent(path)}`);
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

  // ==================== DATASET METHODS ====================

  async listDatasets(): Promise<Dataset[]> {
    return this.request<Dataset[]>(ENDPOINTS.datasets);
  }

  async getDataset(
    datasetName: string,
    includeImages: boolean = false,
    split?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<DatasetDetail> {
    const params = new URLSearchParams({
      include_images: String(includeImages),
      limit: String(limit),
      offset: String(offset),
      ...(split && { split }),
    });
    return this.request(`/datasets/${datasetName}?${params}`);
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
    recursive: boolean = true,
    onProgress?: (current: number, total: number, percentage: number) => void
  ): Promise<Dataset> {
    const BATCH_SIZE = 100;
    const fileArray = Array.from(files);
    const batches = Math.ceil(fileArray.length / BATCH_SIZE);

    let datasetName = name;
    let finalDataset: Dataset | null = null;

    for (let i = 0; i < batches; i++) {
      const start = i * BATCH_SIZE;
      const end = Math.min(start + BATCH_SIZE, fileArray.length);
      const batch = fileArray.slice(start, end);

      const formData = new FormData();

      batch.forEach((file) => {
        formData.append("files", file, file.webkitRelativePath || file.name);
      });

      if (datasetName) {
        formData.append("name", datasetName);
      }

      if (i === 0 && classes && classes.length > 0) {
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
          data.error?.message ||
            `HTTP ${response.status} (batch ${i + 1}/${batches})`,
          response.status
        );
      }

      finalDataset = data.data as Dataset;

      if (i === 0 && !datasetName) {
        datasetName = finalDataset.name;
      }

      const percentage = Math.round(((i + 1) / batches) * 100);
      onProgress?.(i + 1, batches, percentage);
    }

    return finalDataset!;
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

  // ==================== JOB METHODS ====================

  async createJob(data: CreateJobRequest): Promise<Job> {
    return this.request<Job>("/jobs/create", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listJobs(status?: string): Promise<Job[]> {
    const params = status ? `?status=${status}` : "";
    return this.request<Job[]>(`/jobs${params}`);
  }

  async getJob(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}`);
  }

  async startJob(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}/start`, {
      method: "POST",
    });
  }

  async pauseJob(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}/pause`, {
      method: "POST",
    });
  }

  async cancelJob(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}/cancel`, {
      method: "POST",
    });
  }

  async completeTask(jobId: string, taskId: string): Promise<Task> {
    return this.request<Task>(`/jobs/${jobId}/tasks/${taskId}/complete`, {
      method: "POST",
    });
  }

  async getJobTasks(jobId: string, status?: string): Promise<Task[]> {
    const params = status ? `?status=${status}` : "";
    return this.request<Task[]>(`/jobs/${jobId}/tasks${params}`);
  }

  async getNextTask(jobId: string): Promise<Task | null> {
    return this.request<Task | null>(`/jobs/${jobId}/next-task`);
  }

  async updateTaskStatus(
    jobId: string,
    taskId: string,
    status: string
  ): Promise<Task> {
    return this.request<Task>(
      `/jobs/${jobId}/tasks/${taskId}/status?status=${status}`,
      {
        method: "POST",
      }
    );
  }

  async getJobReview(jobId: string): Promise<{
    job_id: string;
    dataset_name: string;
    total_completed: number;
    items: Array<{
      image_id: string;
      image_path: string;
      num_boxes: number;
      current_split: string;
    }>;
  }> {
    return this.request(`/jobs/${jobId}/review`);
  }

  async assignSplits(
    jobId: string,
    assignments: Array<{ image_id: string; split: string }>
  ): Promise<{ success: string[]; failed: unknown[] }> {
    return this.request(`/jobs/${jobId}/assign-splits`, {
      method: "POST",
      body: JSON.stringify({ assignments }),
    });
  }

  // ==================== MODEL METHODS ====================

  async listModels(): Promise<PromotedModel[]> {
    return this.request<PromotedModel[]>(ENDPOINTS.models);
  }

  async getModel(name: string): Promise<PromotedModel> {
    return this.request<PromotedModel>(ENDPOINTS.modelDetail(name));
  }

  async deleteModel(name: string): Promise<void> {
    return this.request<void>(ENDPOINTS.modelDetail(name), {
      method: "DELETE",
    });
  }

  // ==================== TRAINING RUN METHODS ====================

  async listRuns(status?: string): Promise<TrainingRun[]> {
    const params = status ? `?status=${status}` : "";
    return this.request<TrainingRun[]>(`${ENDPOINTS.runs}${params}`);
  }

  async getRun(runId: string): Promise<TrainingRun> {
    return this.request<TrainingRun>(`${ENDPOINTS.runs}/${runId}`);
  }

  async createRun(data: {
    dataset_name: string;
    model?: string;
    epochs?: number;
    task?: string;
    imgsz?: number;
    batch?: number;
    device?: string;
    patience?: number;
    save_period?: number;
    workers?: number;
    seed?: number | null;
  }): Promise<TrainingRun> {
    return this.request<TrainingRun>(ENDPOINTS.runs, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async startRun(runId: string): Promise<TrainingRun> {
    return this.request<TrainingRun>(`${ENDPOINTS.runs}/${runId}/start`, {
      method: "POST",
    });
  }

  async stopRun(runId: string, timeout: number = 10.0): Promise<TrainingRun> {
    return this.request<TrainingRun>(
      `${ENDPOINTS.runs}/${runId}/stop?timeout=${timeout}`,
      { method: "POST" }
    );
  }

  async deleteRun(
    runId: string,
    keepArtifacts: boolean = false
  ): Promise<void> {
    return this.request<void>(
      `${ENDPOINTS.runs}/${runId}?keep_artifacts=${keepArtifacts}`,
      { method: "DELETE" }
    );
  }

  async getLogs(
    runId: string,
    stream: "stdout" | "stderr" = "stdout",
    lines: number = 100
  ): Promise<LogsResponse> {
    return this.request<LogsResponse>(
      `${ENDPOINTS.runs}/${runId}/logs?stream=${stream}&lines=${lines}`
    );
  }

  async promoteModel(
    runId: string,
    name: string,
    description?: string,
    tags?: string[]
  ): Promise<{
    name: string;
    version: string;
    run_id: string;
    metrics: Record<string, number>;
  }> {
    return this.request(`${ENDPOINTS.runs}/${runId}/promote`, {
      method: "POST",
      body: JSON.stringify({ name, description, tags }),
    });
  }

  // ==================== ANNOTATION METHODS ====================

  async getAnnotation(
    datasetName: string,
    imageId: string
  ): Promise<Annotation> {
    return this.request<Annotation>(
      `/datasets/${datasetName}/annotations/${imageId}`
    );
  }

  async saveAnnotation(
    datasetName: string,
    imageId: string,
    boxes: Box[],
    isNull: boolean = false
  ): Promise<{
    image_id: string;
    num_boxes: number;
    label_path: string;
    is_null: boolean;
  }> {
    return this.request(`/datasets/${datasetName}/annotations/${imageId}`, {
      method: "POST",
      body: JSON.stringify({ boxes, is_null: isNull }),
    });
  }

  async deleteBox(
    datasetName: string,
    imageId: string,
    boxIndex: number
  ): Promise<{
    image_id: string;
    deleted_index: number;
    remaining_boxes: number;
  }> {
    return this.request(
      `/datasets/${datasetName}/annotations/${imageId}/boxes/${boxIndex}`,
      {
        method: "DELETE",
      }
    );
  }

  // ==================== PREDICTION METHODS ====================

  async listPredictions(status?: string): Promise<PredictionJob[]> {
    const params = status ? `?status=${status}` : "";
    return this.request<PredictionJob[]>(`/predictions${params}`);
  }

  async getPrediction(inferenceId: string): Promise<PredictionResult> {
    return this.request<PredictionResult>(`/predictions/${inferenceId}`);
  }

  async createPrediction(
    data: CreatePredictionRequest
  ): Promise<PredictionResult> {
    const params = new URLSearchParams();
    params.append("model_name", data.model_name);
    params.append("input_type", data.input_type);
    params.append("input_path", data.input_path);

    if (data.conf !== undefined) params.append("conf", data.conf.toString());
    if (data.iou !== undefined) params.append("iou", data.iou.toString());
    if (data.device) params.append("device", data.device);
    if (data.batch_size !== undefined)
      params.append("batch_size", data.batch_size.toString());
    if (data.save_txt !== undefined)
      params.append("save_txt", data.save_txt.toString());
    if (data.save_img !== undefined)
      params.append("save_img", data.save_img.toString());
    if (data.classes) params.append("classes", data.classes);
    if (data.split) params.append("split", data.split);

    return this.request<PredictionResult>(`/predictions?${params.toString()}`, {
      method: "POST",
    });
  }

  async deletePrediction(inferenceId: string): Promise<void> {
    return this.request<void>(`/predictions/${inferenceId}`, {
      method: "DELETE",
    });
  }
}
