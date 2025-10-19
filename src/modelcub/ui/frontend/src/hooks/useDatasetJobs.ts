import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import type { Job } from "@/lib/api/types";

export const useDatasetJobs = (datasetName: string | undefined) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  const loadJobs = useCallback(async () => {
    if (!datasetName) return;
    setLoading(true);
    try {
      const allJobs = await api.listJobs();
      const datasetJobs = allJobs.filter((j) => j.dataset_name === datasetName);
      setJobs(datasetJobs);
    } catch (err) {
      console.error("Failed to load jobs:", err);
    } finally {
      setLoading(false);
    }
  }, [datasetName]);

  useEffect(() => {
    if (datasetName) loadJobs();
  }, [datasetName, loadJobs]);

  const activeJobs = jobs.filter((j) =>
    ["pending", "running", "paused"].includes(j.status)
  );

  const completedJobs = jobs.filter((j) =>
    ["completed", "failed", "cancelled"].includes(j.status)
  );

  return { jobs, activeJobs, completedJobs, loading, reload: loadJobs };
};
