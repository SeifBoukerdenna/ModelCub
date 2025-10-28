"""
System resource monitoring endpoint for ModelCub UI.
Provides real-time CPU, RAM, GPU, disk, and process information.
"""

import psutil
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/system", tags=["system"])


class CPUInfo(BaseModel):
    percent: float
    cores: int
    frequency: Optional[float] = None


class MemoryInfo(BaseModel):
    total: int
    used: int
    available: int
    percent: float


class GPUInfo(BaseModel):
    id: int
    name: str
    memory_total: int
    memory_used: int
    memory_percent: float
    temperature: Optional[float] = None
    utilization: Optional[float] = None


class DiskInfo(BaseModel):
    total: int
    used: int
    free: int
    percent: float


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float


class ModelCubTaskInfo(BaseModel):
    """ModelCub-specific task information"""
    task_id: str
    task_type: str  # 'training', 'annotation', 'data_processing', 'inference'
    name: str
    cpu_percent: float
    memory_mb: float
    gpu_memory_mb: float
    duration_seconds: int


class SystemResources(BaseModel):
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    gpu: Optional[list[GPUInfo]] = None
    processes: Optional[list[ProcessInfo]] = None
    modelcub_tasks: Optional[list[ModelCubTaskInfo]] = None
    timestamp: str


def get_gpu_info() -> Optional[list[GPUInfo]]:
    """Get GPU information using pynvml (NVIDIA) or fallback methods."""
    gpu_list = []

    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

            try:
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temperature = None

            try:
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = utilization.gpu
            except:
                gpu_util = None

            gpu_list.append(GPUInfo(
                id=i,
                name=name if isinstance(name, str) else name.decode('utf-8'),
                memory_total=memory_info.total,
                memory_used=memory_info.used,
                memory_percent=(memory_info.used / memory_info.total * 100) if memory_info.total > 0 else 0,
                temperature=temperature,
                utilization=gpu_util
            ))

        pynvml.nvmlShutdown()
        return gpu_list if gpu_list else None

    except ImportError:
        # pynvml not installed
        return None
    except Exception as e:
        # GPU not available or other error
        print(f"GPU info error: {e}")
        return None


def get_top_processes(limit: int = 5) -> list[ProcessInfo]:
    """Get top processes by CPU and memory usage."""
    processes = []

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu_percent': info['cpu_percent'] or 0,
                    'memory_mb': info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU first, then memory
        processes.sort(key=lambda x: (x['cpu_percent'], x['memory_mb']), reverse=True)

        return [
            ProcessInfo(**proc) for proc in processes[:limit]
        ]

    except Exception as e:
        print(f"Process info error: {e}")
        return []


@router.get("/resources", response_model=SystemResources)
async def get_system_resources():
    """
    Get current system resource usage including CPU, memory, disk, GPU, and top processes.

    Returns:
        SystemResources: Complete system resource information
    """
    try:
        # CPU Info
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()

        cpu_info = CPUInfo(
            percent=cpu_percent,
            cores=psutil.cpu_count(logical=True),
            frequency=cpu_freq.current if cpu_freq else None
        )

        # Memory Info
        memory = psutil.virtual_memory()
        memory_info = MemoryInfo(
            total=memory.total,
            used=memory.used,
            available=memory.available,
            percent=memory.percent
        )

        # Disk Info
        disk = psutil.disk_usage('/')
        disk_info = DiskInfo(
            total=disk.total,
            used=disk.used,
            free=disk.free,
            percent=disk.percent
        )

        # GPU Info (if available)
        gpu_info = get_gpu_info()

        # Top Processes
        processes = get_top_processes(limit=5)

        return SystemResources(
            cpu=cpu_info,
            memory=memory_info,
            disk=disk_info,
            gpu=gpu_info,
            processes=processes,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system resources: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}