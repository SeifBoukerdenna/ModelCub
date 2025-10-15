/**
 * Core type definitions for ModelCub UI
 *
 * Path: frontend/src/types/index.ts
 */

// Project Types
export interface Project {
  name: string;
  path: string;
  created: string;
  version: string;
  config: ProjectConfig;
  is_current?: boolean;
}

export interface ProjectConfig {
  device: string;
  batch_size: number;
  image_size: number;
  workers: number;
  format: string;
}

// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface ApiError {
  success: false;
  error: string;
  status_code?: number;
  details?: unknown;
}

// UI State Types
export type LoadingState = "idle" | "loading" | "success" | "error";

// Model Types (placeholder for future use)
export interface Model {
  id: string;
  name: string;
  type: string;
  created: string;
}

// Training Types (placeholder for future use)
export interface TrainingRun {
  id: string;
  model_id: string;
  dataset_id: string;
  status: string;
  created: string;
  metrics?: Record<string, number>;
}
