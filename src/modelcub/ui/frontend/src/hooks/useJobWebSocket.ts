/**
 * React hook for subscribing to job-related WebSocket events
 */
import { useEffect, useRef } from "react";
import { wsManager } from "@/lib/websocket";
import type { Job, Task } from "@/lib/api/types";

interface JobWebSocketCallbacks {
  onTaskCompleted?: (task: Task, job: Job) => void;
  onJobStarted?: (job: Job) => void;
  onJobPaused?: (job: Job) => void;
  onJobCancelled?: (job: Job) => void;
  onJobCompleted?: (job: Job) => void;
}

/**
 * Hook to subscribe to WebSocket events for a specific job
 */
export const useJobWebSocket = (
  jobId: string | null,
  callbacks: JobWebSocketCallbacks
) => {
  // Use refs to avoid recreating handlers on every render
  const callbacksRef = useRef(callbacks);

  // Update ref when callbacks change
  useEffect(() => {
    callbacksRef.current = callbacks;
  }, [callbacks]);

  useEffect(() => {
    if (!jobId) return;

    // Ensure WebSocket is connected (only once per manager instance)
    wsManager.connect();

    const handleTaskCompleted = (data: any) => {
      if (data.job_id === jobId && data.data?.task && data.data?.job) {
        console.log("[WS] Task completed:", data.data.task.task_id);
        callbacksRef.current.onTaskCompleted?.(data.data.task, data.data.job);
      }
    };

    const handleJobStarted = (data: any) => {
      if (data.job_id === jobId && data.data) {
        console.log("[WS] Job started");
        callbacksRef.current.onJobStarted?.(data.data);
      }
    };

    const handleJobPaused = (data: any) => {
      if (data.job_id === jobId && data.data) {
        console.log("[WS] Job paused");
        callbacksRef.current.onJobPaused?.(data.data);
      }
    };

    const handleJobCancelled = (data: any) => {
      if (data.job_id === jobId && data.data) {
        console.log("[WS] Job cancelled");
        callbacksRef.current.onJobCancelled?.(data.data);
      }
    };

    const handleJobCompleted = (data: any) => {
      if (data.job_id === jobId && data.data) {
        console.log("[WS] Job completed");
        callbacksRef.current.onJobCompleted?.(data.data);
      }
    };

    // Subscribe to events
    wsManager.on("task.completed", handleTaskCompleted);
    wsManager.on("job.started", handleJobStarted);
    wsManager.on("job.paused", handleJobPaused);
    wsManager.on("job.cancelled", handleJobCancelled);
    wsManager.on("job.completed", handleJobCompleted);

    // Cleanup
    return () => {
      wsManager.off("task.completed", handleTaskCompleted);
      wsManager.off("job.started", handleJobStarted);
      wsManager.off("job.paused", handleJobPaused);
      wsManager.off("job.cancelled", handleJobCancelled);
      wsManager.off("job.completed", handleJobCompleted);
    };
  }, [jobId]); // Only re-run when jobId changes
};
