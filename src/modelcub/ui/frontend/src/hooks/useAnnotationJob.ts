import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useJobWebSocket } from "@/hooks/useJobWebSocket";
import type { Job, Task } from "@/lib/api/types";

export const useAnnotationJob = (jobId: string | null) => {
  const [job, setJob] = useState<Job | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // WebSocket subscriptions
  useJobWebSocket(jobId, {
    onTaskCompleted: (task, updatedJob) => {
      setJob(updatedJob);
      setTasks((prev) =>
        prev.map((t) => (t.task_id === task.task_id ? task : t))
      );
    },
    onJobStarted: setJob,
    onJobPaused: setJob,
    onJobCancelled: setJob,
    onJobCompleted: setJob,
  });

  const loadJob = useCallback(async () => {
    if (!jobId) return;
    try {
      const jobData = await api.getJob(jobId);
      setJob(jobData);
    } catch (err: any) {
      setError(err?.message || "Failed to load job");
    }
  }, [jobId]);

  const loadTasks = useCallback(async () => {
    if (!jobId) return;
    try {
      const tasksData = await api.getJobTasks(jobId);
      setTasks(tasksData);
    } catch (err: any) {
      console.error("Failed to load tasks:", err);
    } finally {
      setIsLoading(false);
    }
  }, [jobId]);

  const markTaskInProgress = useCallback(
    async (taskId: string) => {
      if (!jobId) return;
      try {
        await api.updateTaskStatus(jobId, taskId, "in_progress");
        setTasks((prev) =>
          prev.map((t) =>
            t.task_id === taskId ? { ...t, status: "in_progress" as any } : t
          )
        );
      } catch (err) {
        console.error("Failed to mark task as in_progress:", err);
      }
    },
    [jobId]
  );

  const completeTask = useCallback(
    async (taskId: string) => {
      if (!jobId) return;
      try {
        await api.completeTask(jobId, taskId);
      } catch (err: any) {
        console.error("Failed to complete task:", err);
        throw err;
      }
    },
    [jobId]
  );

  useEffect(() => {
    if (!jobId) {
      setError("No job ID provided");
      setIsLoading(false);
      return;
    }
    loadJob();
    loadTasks();
  }, [jobId, loadJob, loadTasks]);

  const completedCount = tasks.filter((t) => t.status === "completed").length;

  return {
    job,
    tasks,
    error,
    isLoading,
    completedCount,
    markTaskInProgress,
    completeTask,
  };
};
