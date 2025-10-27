/**
 * API types - mirrors backend schemas
 */

// ==================== BASE API TYPES ====================

export interface ResponseMeta {
  timestamp: string;
  request_id?: string;
}

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ErrorDetail;
  message?: string;
  meta?: ResponseMeta;
}

// ==================== PROJECT TYPES ====================

export interface ProjectConfig {
  device: string;
  batch_size: number;
  image_size: number;
  workers: number;
  format: string;
}

export interface ProjectInfo {
  name: string;
  created: string;
  version: string;
}

export interface ProjectPaths {
  data: string;
  runs: string;
  reports: string;
}

export interface ProjectConfigFull {
  project: ProjectInfo;
  defaults: ProjectConfig;
  paths: ProjectPaths;
}

export interface Project {
  name: string;
  path: string;
  created: string;
  version: string;
  config: ProjectConfig;
  is_current?: boolean;
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

export interface DeleteProjectRequest {
  confirm: boolean;
}

// ==================== DATASET TYPES ====================

export interface Dataset {
  name: string;
  id: string;
  status: string;
  classes: string[];
  path: string;
  created?: string;
  source?: string;
  size_bytes: number;
  size_formatted: string;
  images?: number;
}

export interface DatasetDetail extends Dataset {
  train_images: number;
  valid_images: number;
  unlabeled_images: number;
  image_list?: ImageInfo[];
  total_images?: number;
}

export interface ImportDatasetRequest {
  source: string;
  name?: string;
  recursive?: boolean;
  copy_files?: boolean;
  classes?: string[];
}

export interface ImageInfo {
  filename: string;
  path: string;
  width: number;
  height: number;
  size_bytes: number;
  has_labels: boolean;
  split: string;
}

// ==================== MODEL TYPES ====================

export interface Model {
  id: string;
  name: string;
  type: string;
  created: string;
  path?: string;
}

// ==================== JOB TYPES ====================

export interface Job {
  job_id: string;
  dataset_name: string;
  status:
    | "pending"
    | "running"
    | "paused"
    | "completed"
    | "failed"
    | "cancelled";
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  paused_at: string | null;
  can_resume: boolean;
  is_terminal: boolean;
}

export interface Task {
  task_id: string;
  job_id: string;
  image_id: string;
  image_path: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped";
  attempts: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface CreateJobRequest {
  dataset_name: string;
  image_ids?: string[];
  auto_start?: boolean;
  config?: Record<string, any>;
}

// ==================== ANNOTATION TYPES ====================

export interface Box {
  class_id: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Annotation {
  image_id: string;
  image_path: string;
  split: string;
  boxes: Box[];
  num_boxes: number;
  is_null: boolean; // NEW: Whether marked as null (intentionally empty)
  is_annotated: boolean; // NEW: Whether has any annotation (boxes or null marker)
}

// ==================== ERROR CODES ====================

export const ErrorCode = {
  INTERNAL_ERROR: "INTERNAL_ERROR",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  NOT_FOUND: "NOT_FOUND",
  BAD_REQUEST: "BAD_REQUEST",
  PROJECT_NOT_FOUND: "PROJECT_NOT_FOUND",
  PROJECT_ALREADY_EXISTS: "PROJECT_ALREADY_EXISTS",
  PROJECT_INVALID: "PROJECT_INVALID",
  PROJECT_LOAD_FAILED: "PROJECT_LOAD_FAILED",
  DATASET_NOT_FOUND: "DATASET_NOT_FOUND",
  DATASET_ALREADY_EXISTS: "DATASET_ALREADY_EXISTS",
  DATASET_IMPORT_FAILED: "DATASET_IMPORT_FAILED",
  DATASET_INVALID: "DATASET_INVALID",
  MODEL_NOT_FOUND: "MODEL_NOT_FOUND",
  TRAINING_FAILED: "TRAINING_FAILED",
  FILE_NOT_FOUND: "FILE_NOT_FOUND",
  FILE_UPLOAD_FAILED: "FILE_UPLOAD_FAILED",
  INVALID_FILE_TYPE: "INVALID_FILE_TYPE",
} as const;

export type ErrorCodeType = (typeof ErrorCode)[keyof typeof ErrorCode];

export interface ModelMetrics {
  map50?: number;
  map50_95?: number;
  precision?: number;
  recall?: number;
  best_epoch?: number;
}

export interface ModelConfig {
  model?: string;
  epochs?: number;
  batch?: number;
  imgsz?: number;
  device?: string;
  patience?: number;
  [key: string]: any;
}

export interface PromotedModel {
  name: string;
  version: string;
  created: string;
  run_id: string;
  path: string;
  description?: string;
  tags?: string[];
  metrics?: ModelMetrics;
  dataset_name?: string;
  config?: ModelConfig;
}

export interface TrainingRunMetrics {
  map50?: number;
  map50_95?: number;
  precision?: number;
  recall?: number;
  best_epoch?: number;
}

export interface TrainingRunConfig {
  model: string;
  epochs: number;
  batch: number;
  imgsz: number;
  device: string;
  patience: number;
  save_period?: number;
  workers?: number;
  seed?: number;
  [key: string]: any;
}

export interface TrainingRun {
  id: string;
  created: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  dataset_name: string;
  dataset_snapshot_id: string;
  task: string;
  config: TrainingRunConfig;
  artifacts_path: string;
  metrics?: TrainingRunMetrics;
  pid?: number | null;
  duration_ms?: number | null;
  exit_code?: number | null;
  error?: string | null;
  started?: string;
}
