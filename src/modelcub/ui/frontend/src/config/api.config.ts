/**
 * API configuration for frontend
 */

export const API_CONFIG = {
  baseURL: "/api/v1",
  timeout: 30000,
  withCredentials: true,
} as const;

export const ENDPOINTS = {
  // Health
  health: "/health",

  // Projects
  projects: "/projects",
  projectByPath: "/projects/by-path",
  projectConfig: "/projects/config",
  projectDelete: "/projects/delete",

  // Datasets
  datasets: "/datasets",
  datasetDetail: (id: string) => `/datasets/${id}`,
  datasetImport: "/datasets/import",
  datasetUpload: "/datasets/upload",
  datasetImages: (id: string) => `/datasets/${id}/images`,

  // Models
  models: "/models",
  modelDetail: (id: string) => `/models/${id}`,

  runs: "/runs",
  runDetail: (id: string) => `/runs/${id}`,
  runStart: (id: string) => `/runs/${id}/start`,
  runStop: (id: string) => `/runs/${id}/stop`,

  // WebSocket
  ws: "/ws",
} as const;
