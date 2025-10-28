import { create } from "zustand";

export interface CPUInfo {
  percent: number;
  cores: number;
  frequency?: number;
}

export interface MemoryInfo {
  total: number;
  used: number;
  available: number;
  percent: number;
}

export interface GPUInfo {
  id: number;
  name: string;
  memory_total: number;
  memory_used: number;
  memory_percent: number;
  temperature?: number;
  utilization?: number;
}

export interface DiskInfo {
  total: number;
  used: number;
  free: number;
  percent: number;
}

export interface ProcessInfo {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_mb: number;
}

export interface ModelCubTaskInfo {
  task_id: string;
  task_type: "training" | "annotation" | "data_processing" | "inference";
  name: string;
  cpu_percent: number;
  memory_mb: number;
  gpu_memory_mb: number;
  duration_seconds: number;
}

export interface SystemResources {
  cpu: CPUInfo;
  memory: MemoryInfo;
  disk: DiskInfo;
  gpu?: GPUInfo[];
  processes?: ProcessInfo[];
  modelcub_tasks?: ModelCubTaskInfo[];
  timestamp: string;
}

interface ResourceStore {
  resources: SystemResources | null;
  isExpanded: boolean;
  isVisible: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setResources: (resources: SystemResources) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  toggleExpanded: () => void;
  toggleVisible: () => void;
  fetchResources: () => Promise<void>;
}

export const useResourceStore = create<ResourceStore>((set) => ({
  resources: null,
  isExpanded: false,
  isVisible: true,
  isLoading: false,
  error: null,

  setResources: (resources) => set({ resources, error: null }),

  setError: (error) => set({ error, isLoading: false }),

  setLoading: (isLoading) => set({ isLoading }),

  toggleExpanded: () => set((state) => ({ isExpanded: !state.isExpanded })),

  toggleVisible: () => set((state) => ({ isVisible: !state.isVisible })),

  fetchResources: async () => {
    try {
      set({ isLoading: true });
      const response = await fetch("/api/v1/system/resources");

      if (!response.ok) {
        throw new Error(`Failed to fetch resources: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Fetched resources:", data);
      set({ resources: data, error: null, isLoading: false });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      console.error("Resource fetch error:", errorMessage);
      set({ error: errorMessage, isLoading: false });
    }
  },
}));
