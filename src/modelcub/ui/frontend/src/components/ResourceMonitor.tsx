import React, { useEffect } from 'react'
import { Cpu, HardDrive, Zap, ChevronDown, ChevronUp, X } from 'lucide-react'
import { useResourceStore } from '@/stores/resourceStore'

interface ResourceMonitorProps {
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ position = 'top-right' }) => {
    const {
        resources,
        isExpanded,
        isVisible,
        isLoading,
        error,
        toggleExpanded,
        toggleVisible,
        fetchResources
    } = useResourceStore()

    useEffect(() => {
        // Initial fetch
        fetchResources()

        // Poll every 2 seconds
        const interval = setInterval(() => {
            fetchResources()
        }, 2000)

        return () => clearInterval(interval)
    }, [fetchResources])

    if (!isVisible) {
        return (
            <button
                className={`resource-monitor-fab resource-monitor-fab--${position}`}
                onClick={toggleVisible}
                title="Show Resource Monitor"
            >
                <Zap size={20} />
            </button>
        )
    }

    const getStatusClass = (percentage: number): string => {
        if (percentage >= 90) return 'critical'
        if (percentage >= 75) return 'warning'
        return 'normal'
    }

    const getStatusColor = (percentage: number): string => {
        if (percentage >= 90) return 'var(--color-error)'
        if (percentage >= 75) return 'var(--color-warning)'
        return 'var(--color-success)'
    }

    return (
        <div className={`resource-monitor resource-monitor--${position}`}>
            {/* Compact Header */}
            <div className="resource-monitor__header" onClick={toggleExpanded}>
                <div className="resource-monitor__header-content">
                    <Zap size={16} className="resource-monitor__icon" />
                    <span className="resource-monitor__title">System</span>
                    {!isExpanded && resources?.cpu && resources?.memory && (
                        <div className="resource-monitor__compact-indicators">
                            <span
                                className="resource-monitor__compact-badge"
                                style={{ color: getStatusColor(resources.cpu.percent) }}
                            >
                                CPU {resources.cpu.percent.toFixed(0)}%
                            </span>
                            <span
                                className="resource-monitor__compact-badge"
                                style={{ color: getStatusColor(resources.memory.percent) }}
                            >
                                RAM {resources.memory.percent.toFixed(0)}%
                            </span>
                        </div>
                    )}
                </div>
                <div className="resource-monitor__header-actions">
                    <button
                        className="resource-monitor__action-btn"
                        onClick={(e) => {
                            e.stopPropagation()
                            toggleExpanded()
                        }}
                        title={isExpanded ? 'Minimize' : 'Expand'}
                    >
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                    <button
                        className="resource-monitor__action-btn"
                        onClick={(e) => {
                            e.stopPropagation()
                            toggleVisible()
                        }}
                        title="Close"
                    >
                        <X size={14} />
                    </button>
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="resource-monitor__body">
                    {isLoading && !resources ? (
                        <div className="resource-monitor__loading">Loading...</div>
                    ) : error ? (
                        <div className="resource-monitor__error">{error}</div>
                    ) : !resources ? (
                        <div className="resource-monitor__loading">No data available</div>
                    ) : resources?.cpu && resources?.memory && resources?.disk ? (
                        <>
                            {/* CPU Section */}
                            <div className="resource-monitor__section">
                                <div className="resource-monitor__section-header">
                                    <Cpu size={14} />
                                    <span>CPU</span>
                                    <span className="resource-monitor__value">
                                        {resources.cpu.percent.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="resource-monitor__progress-bar">
                                    <div
                                        className={`resource-monitor__progress-fill resource-monitor__progress-fill--${getStatusClass(resources.cpu.percent)}`}
                                        style={{ width: `${resources.cpu.percent}%` }}
                                    />
                                </div>
                                <div className="resource-monitor__details">
                                    <span>{resources.cpu.cores} cores</span>
                                    {resources.cpu.frequency && (
                                        <span>{resources.cpu.frequency.toFixed(0)} MHz</span>
                                    )}
                                </div>
                            </div>

                            {/* Memory Section */}
                            <div className="resource-monitor__section">
                                <div className="resource-monitor__section-header">
                                    <HardDrive size={14} />
                                    <span>Memory</span>
                                    <span className="resource-monitor__value">
                                        {resources.memory.percent.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="resource-monitor__progress-bar">
                                    <div
                                        className={`resource-monitor__progress-fill resource-monitor__progress-fill--${getStatusClass(resources.memory.percent)}`}
                                        style={{ width: `${resources.memory.percent}%` }}
                                    />
                                </div>
                                <div className="resource-monitor__details">
                                    <span>{(resources.memory.used / 1024 / 1024 / 1024).toFixed(1)} GB used</span>
                                    <span>{(resources.memory.total / 1024 / 1024 / 1024).toFixed(1)} GB total</span>
                                </div>
                            </div>

                            {/* GPU Section (if available) */}
                            {resources.gpu && resources.gpu.length > 0 && (
                                <div className="resource-monitor__section">
                                    <div className="resource-monitor__section-header">
                                        <Zap size={14} />
                                        <span>GPU {resources.gpu.length > 1 ? `(${resources.gpu.length})` : ''}</span>
                                    </div>
                                    {resources.gpu.map((gpu, index) => (
                                        <div key={index} className="resource-monitor__gpu">
                                            <div className="resource-monitor__gpu-name">{gpu.name}</div>
                                            <div className="resource-monitor__progress-bar">
                                                <div
                                                    className={`resource-monitor__progress-fill resource-monitor__progress-fill--${getStatusClass(gpu.memory_percent)}`}
                                                    style={{ width: `${gpu.memory_percent}%` }}
                                                />
                                            </div>
                                            <div className="resource-monitor__details">
                                                <span>{(gpu.memory_used / 1024).toFixed(1)} GB used</span>
                                                <span>{(gpu.memory_total / 1024).toFixed(1)} GB total</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Disk Section */}
                            <div className="resource-monitor__section">
                                <div className="resource-monitor__section-header">
                                    <HardDrive size={14} />
                                    <span>Disk</span>
                                    <span className="resource-monitor__value">
                                        {resources.disk.percent.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="resource-monitor__progress-bar">
                                    <div
                                        className={`resource-monitor__progress-fill resource-monitor__progress-fill--${getStatusClass(resources.disk.percent)}`}
                                        style={{ width: `${resources.disk.percent}%` }}
                                    />
                                </div>
                                <div className="resource-monitor__details">
                                    <span>{(resources.disk.used / 1024 / 1024 / 1024).toFixed(1)} GB used</span>
                                    <span>{(resources.disk.total / 1024 / 1024 / 1024).toFixed(1)} GB total</span>
                                </div>
                            </div>

                            {/* Top Processes */}
                            {resources.processes && resources.processes.length > 0 && (
                                <div className="resource-monitor__section">
                                    <div className="resource-monitor__section-header">
                                        <span>Top Processes</span>
                                    </div>
                                    <div className="resource-monitor__processes">
                                        {resources.processes.slice(0, 5).map((proc, index) => (
                                            <div key={index} className="resource-monitor__process">
                                                <span className="resource-monitor__process-name" title={proc.name}>
                                                    {proc.name}
                                                </span>
                                                <div className="resource-monitor__process-stats">
                                                    <span className="resource-monitor__process-stat">
                                                        CPU: {proc.cpu_percent.toFixed(1)}%
                                                    </span>
                                                    <span className="resource-monitor__process-stat">
                                                        RAM: {(proc.memory_mb).toFixed(0)} MB
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* ModelCub Tasks */}
                            {resources.modelcub_tasks && resources.modelcub_tasks.length > 0 && (
                                <div className="resource-monitor__section">
                                    <div className="resource-monitor__section-header">
                                        <span>ModelCub Tasks</span>
                                    </div>
                                    <div className="resource-monitor__processes">
                                        {resources.modelcub_tasks.map((task) => (
                                            <div key={task.task_id} className="resource-monitor__modelcub-task">
                                                <div className="resource-monitor__task-header">
                                                    <span className="resource-monitor__task-name" title={task.name}>
                                                        {task.name}
                                                    </span>
                                                    <span className="resource-monitor__task-type">
                                                        {task.task_type}
                                                    </span>
                                                </div>
                                                <div className="resource-monitor__process-stats">
                                                    <span className="resource-monitor__process-stat">
                                                        CPU: {task.cpu_percent.toFixed(1)}%
                                                    </span>
                                                    <span className="resource-monitor__process-stat">
                                                        RAM: {task.memory_mb.toFixed(0)} MB
                                                    </span>
                                                    {task.gpu_memory_mb > 0 && (
                                                        <span className="resource-monitor__process-stat">
                                                            GPU: {task.gpu_memory_mb.toFixed(0)} MB
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="resource-monitor__task-duration">
                                                    {Math.floor(task.duration_seconds / 60)}m {task.duration_seconds % 60}s
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Last Updated */}
                            <div className="resource-monitor__footer">
                                Last updated: {new Date(resources.timestamp).toLocaleTimeString()}
                            </div>
                        </>
                    ) : null}
                </div>
            )}
        </div>
    )
}

export default ResourceMonitor