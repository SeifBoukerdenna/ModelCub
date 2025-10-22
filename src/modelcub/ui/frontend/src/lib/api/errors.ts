/**
 * API Error classes
 */

export class ModelCubAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "ModelCubAPIError";
  }
}
