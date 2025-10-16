/**
 * API types - mirrors backend schemas
 * Generated/synced from backend Pydantic models
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
  image_list?: ImageInfo[]; // Add this
  total_images?: number; // Add this
}

export interface ImportDatasetRequest {
  source: string;
  name?: string;
  recursive?: boolean;
  copy?: boolean;
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

export interface TrainingRun {
  id: string;
  model_id: string;
  dataset_id: string;
  status: string;
  created: string;
  metrics?: Record<string, number>;
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
