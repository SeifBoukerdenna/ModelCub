/**
 * Main API module exports
 */

// Export API client
export { api, APIError } from "./client";

// Export all types
export type {
  APIResponse,
  ErrorDetail,
  ResponseMeta,
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
