import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";

export const useDatasetClasses = (datasetName: string | undefined) => {
  const [classes, setClasses] = useState<Array<{ id: number; name: string }>>(
    []
  );
  const [isLoading, setIsLoading] = useState(true);

  const loadClasses = useCallback(async () => {
    if (!datasetName) return;

    setIsLoading(true);
    try {
      const dataset = await api.getDataset(datasetName, false);
      const classNames = dataset.classes || [];
      // Convert string[] to {id, name}[]
      const classesWithIds = classNames.map((name, index) => ({
        id: index,
        name: name,
      }));
      setClasses(classesWithIds);
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
