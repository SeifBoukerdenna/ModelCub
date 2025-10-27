// ADD TO src/modelcub/ui/frontend/src/lib/api/hooks.ts

import { useCallback, useState } from "react";
import { UseAPIResult } from "./hooks";
import { TrainingRun } from "./types";
import { api } from ".";

// ==================== TRAINING RUN HOOKS ====================
export function useListRuns(status?: string): UseAPIResult<TrainingRun[]> {
  const [data, setData] = useState<TrainingRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const runs = await api.listRuns(status);
      setData(runs);
      return runs;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [status]);

  const reset = useCallback(() => {
    setData([]);
    setError(null);
    setLoading(false);
  }, []);

  const state = loading ? "loading" : error ? "error" : "success";

  return { data, loading, error, execute, reset, state };
}

export function useGetRun(runId: string): UseAPIResult<TrainingRun | null> {
  const [data, setData] = useState<TrainingRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    if (!runId) return null;
    setLoading(true);
    setError(null);
    try {
      const run = await api.getRun(runId);
      setData(run);
      return run;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, [runId]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  const state = loading ? "loading" : error ? "error" : "success";

  return { data, loading, error, execute, reset, state };
}
