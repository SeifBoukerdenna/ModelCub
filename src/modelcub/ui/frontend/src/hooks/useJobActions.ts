import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";

export const useJobActions = (
  datasetName: string | undefined,
  onJobUpdate: () => void
) => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const startAnnotation = useCallback(async () => {
    if (!datasetName) return;
    try {
      const job = await api.createJob({
        dataset_name: datasetName,
        auto_start: true,
      });
      showToast("Annotation job started", "success");
      navigate(`/datasets/${datasetName}/annotate?job_id=${job.job_id}`);
    } catch (err: any) {
      showToast(err.message || "Failed to start annotation", "error");
    }
  }, [datasetName, navigate, showToast]);

  const continueJob = useCallback(
    (jobId: string) => {
      if (!datasetName) return;
      navigate(`/datasets/${datasetName}/annotate?job_id=${jobId}`);
    },
    [datasetName, navigate]
  );

  const pauseJob = useCallback(
    async (jobId: string) => {
      try {
        await api.pauseJob(jobId);
        showToast("Job paused", "success");
        onJobUpdate();
      } catch (err: any) {
        showToast(err.message || "Failed to pause job", "error");
      }
    },
    [showToast, onJobUpdate]
  );

  const resumeJob = useCallback(
    async (jobId: string) => {
      try {
        await api.startJob(jobId);
        showToast("Job resumed", "success");
        onJobUpdate();
      } catch (err: any) {
        showToast(err.message || "Failed to resume job", "error");
      }
    },
    [showToast, onJobUpdate]
  );

  return { startAnnotation, continueJob, pauseJob, resumeJob };
};
