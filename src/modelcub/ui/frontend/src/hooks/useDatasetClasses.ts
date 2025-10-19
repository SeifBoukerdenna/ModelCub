import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";

export const useDatasetClasses = (datasetName: string | undefined) => {
  const [classes, setClasses] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadClasses = useCallback(async () => {
    if (!datasetName) return;

    setIsLoading(true);
    try {
      const dataset = await api.getDataset(datasetName);
      setClasses(dataset.classes || []);
    } catch (err) {
      console.error("Failed to load classes:", err);
      setClasses([]);
    } finally {
      setIsLoading(false);
    }
  }, [datasetName]);

  useEffect(() => {
    loadClasses();
  }, [loadClasses]);

  return {
    classes,
    isLoading,
    reload: loadClasses,
  };
};
