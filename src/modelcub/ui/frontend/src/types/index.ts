/**
 * Core type definitions for ModelCub UI
 */

export interface Project {
  name: string;
  path: string;
  created: string;
  version?: string;
  config: ProjectConfig;
  is_current?: boolean;
}

export interface ProjectConfig {
  device: string;
  batch_size: number;
  image_size: number;
  format: string;
}

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

export type LoadingState = "idle" | "loading" | "success" | "error";
