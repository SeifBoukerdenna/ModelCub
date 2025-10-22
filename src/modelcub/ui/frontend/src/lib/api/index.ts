/**
 * ModelCub API Module
 * Main entry point for API interactions
 */

// Export the API client instance
export { ModelCubAPI } from "./client";
export { ModelCubAPIError } from "./errors";

// Export all types
export type {
  Project,
  ProjectConfig,
  ProjectInfo,
  ProjectPaths,
  ProjectConfigFull,
  CreateProjectRequest,
  SetConfigRequest,
  DeleteProjectRequest,
  Dataset,
  DatasetDetail,
  ImportDatasetRequest,
  ImageInfo,
  Model,
  TrainingRun,
  Job,
  Task,
  CreateJobRequest,
  Annotation,
  Box,
  ErrorCodeType,
} from "./types";

export { ErrorCode } from "./types";

// Export all hooks
export {
  useListProjects,
  useCreateProject,
  useGetProjectByPath,
  useGetProjectConfig,
  useSetProjectConfig,
  useDeleteProject,
  useListDatasets,
  useGetDataset,
  useImportDataset,
  useUploadDataset,
  useListDatasetImages,
  useListModels,
  useGetModel,
  useHealthCheck,
} from "./hooks";

export type { UseAPIResult } from "./hooks";

// Create and export singleton instance
import { ModelCubAPI } from "./client";
export const api = new ModelCubAPI();
