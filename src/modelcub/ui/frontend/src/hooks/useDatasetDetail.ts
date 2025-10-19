import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import type { Dataset } from "@/lib/api/types";

export const useDatasetDetails = (name: string | undefined) => {
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDataset = useCallback(async () => {
    if (!name) return;
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDataset(name);
      setDataset(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dataset");
    } finally {
      setLoading(false);
    }
  }, [name]);

  useEffect(() => {
    loadDataset();
  }, [loadDataset]);

  return { dataset, loading, error, reload: loadDataset };
};
