/**
 * Datasets Page Component
 * Displays and manages datasets in the current project
 *
 * Path: frontend/src/pages/Datasets.tsx
 */
import React, { useEffect, useState } from 'react'
import { Plus, Trash2, Database, RefreshCw, Upload, FolderOpen } from 'lucide-react'
import { api, Dataset } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'

const Datasets: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const setProjects = useProjectStore(state => state.setProjects)

    const [datasets, setDatasets] = useState<Dataset[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [message, setMessage] = useState<string>('')

    // Initialize projects if not loaded
    useEffect(() => {
        const initProjects = async () => {
            try {
                const response = await api.listProjects()
                if (response.success && response.projects.length > 0) {
                    setProjects(response.projects)
                }
            } catch (err) {
                console.error('Failed to load projects:', err)
            }
        }

        // Only init if we don't have a selected project
        if (!selectedProject) {
            initProjects()
        }
    }, [])

    const loadDatasets = async () => {
        try {
            setLoading(true)
            setError(null)

            const response = await api.listDatasets()

            console.log('Datasets API Response:', JSON.stringify(response, null, 2))

            if (response.success) {
                setDatasets(response.datasets)
                setMessage(response.message || '')
            } else {
                throw new Error(response.message || 'Failed to load datasets')
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load datasets'
            setError(errorMessage)
            toast.error(errorMessage)
            setDatasets([])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (selectedProject) {
            console.log('Selected project:', selectedProject.name, 'at', selectedProject.path)
            api.setCurrentProject(selectedProject.path)
            loadDatasets()
        } else {
            api.setCurrentProject(null)
            setLoading(false)
            setError('No project selected. Please create or select a project first.')
        }
    }, [selectedProject])

    const handleDeleteDataset = async (datasetName: string) => {
        if (!window.confirm(`Are you sure you want to delete dataset "${datasetName}"?`)) {
            return
        }

        try {
            const response = await api.deleteDataset(datasetName, true)

            if (response.success) {
                toast.success(response.message || `Dataset "${datasetName}" deleted`)
                await loadDatasets()
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to delete dataset'
            toast.error(errorMessage)
        }
    }

    const formatBytes = (bytes: number): string => {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    if (loading) {
        return <Loading text="Loading datasets..." />
    }

    if (!selectedProject) {
        return (
            <div className="empty-state">
                <Database size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">No Project Selected</h3>
                <p className="empty-state__description">
                    Please create or select a project before managing datasets
                </p>
            </div>
        )
    }

    if (error) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Datasets
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: {selectedProject.name} ({selectedProject.path})
                    </p>
                </div>
                <ErrorMessage message={error} />
                <button
                    className="btn btn--primary"
                    style={{ marginTop: 'var(--spacing-lg)' }}
                    onClick={loadDatasets}
                >
                    <RefreshCw size={20} />
                    Retry
                </button>
            </div>
        )
    }

    return (
        <div>
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-xs)'
                }}>
                    <div>
                        <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                            Datasets
                        </h1>
                        <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Project: <strong>{selectedProject.name}</strong>
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            className="btn btn--secondary"
                            onClick={loadDatasets}
                            disabled={loading}
                        >
                            <RefreshCw size={20} />
                            Refresh
                        </button>
                        <button
                            className="btn btn--primary"
                            onClick={() => toast.info('Import feature coming soon')}
                        >
                            <Upload size={20} />
                            Import Dataset
                        </button>
                    </div>
                </div>
                {message && (
                    <p style={{
                        color: 'var(--color-text-secondary)',
                        fontSize: 'var(--font-size-sm)',
                        marginTop: 'var(--spacing-xs)'
                    }}>
                        {message}
                    </p>
                )}
            </div>

            {datasets.length === 0 ? (
                <div className="empty-state">
                    <Database size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No datasets yet</h3>
                    <p className="empty-state__description">
                        Import images to create your first dataset for training
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => toast.info('Import feature coming soon')}
                    >
                        <Upload size={20} />
                        Import Dataset
                    </button>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {datasets.map((dataset) => (
                        <div key={dataset.id} className="card">
                            <div className="card__header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                    <Database size={20} style={{ color: 'var(--color-primary-500)' }} />
                                    <h3 className="card__title">{dataset.name}</h3>
                                </div>
                                <span
                                    className="badge"
                                    style={{
                                        backgroundColor: dataset.status === 'ready'
                                            ? 'var(--color-success-100)'
                                            : 'var(--color-warning-100)',
                                        color: dataset.status === 'ready'
                                            ? 'var(--color-success-700)'
                                            : 'var(--color-warning-700)'
                                    }}
                                >
                                    {dataset.status}
                                </span>
                            </div>

                            <div className="card__body">
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(2, 1fr)',
                                    gap: 'var(--spacing-md)',
                                    marginBottom: 'var(--spacing-md)'
                                }}>
                                    <div>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)'
                                        }}>
                                            Images
                                        </div>
                                        <div style={{
                                            fontSize: 'var(--font-size-lg)',
                                            fontWeight: 600,
                                            color: 'var(--color-text-primary)'
                                        }}>
                                            {dataset.images.toLocaleString()}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)'
                                        }}>
                                            Classes
                                        </div>
                                        <div style={{
                                            fontSize: 'var(--font-size-lg)',
                                            fontWeight: 600,
                                            color: 'var(--color-text-primary)'
                                        }}>
                                            {dataset.classes.length}
                                        </div>
                                    </div>
                                </div>

                                {dataset.classes.length > 0 && (
                                    <div style={{ marginBottom: 'var(--spacing-md)' }}>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)',
                                            marginBottom: 'var(--spacing-xs)'
                                        }}>
                                            Class Names
                                        </div>
                                        <div style={{
                                            display: 'flex',
                                            flexWrap: 'wrap',
                                            gap: 'var(--spacing-xs)'
                                        }}>
                                            {dataset.classes.slice(0, 5).map((className) => (
                                                <span
                                                    key={className}
                                                    className="badge"
                                                    style={{
                                                        backgroundColor: 'var(--color-gray-100)',
                                                        color: 'var(--color-gray-700)',
                                                        fontSize: 'var(--font-size-xs)'
                                                    }}
                                                >
                                                    {className}
                                                </span>
                                            ))}
                                            {dataset.classes.length > 5 && (
                                                <span
                                                    className="badge"
                                                    style={{
                                                        backgroundColor: 'var(--color-gray-100)',
                                                        color: 'var(--color-gray-700)',
                                                        fontSize: 'var(--font-size-xs)'
                                                    }}
                                                >
                                                    +{dataset.classes.length - 5} more
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(2, 1fr)',
                                    gap: 'var(--spacing-sm)'
                                }}>
                                    <div>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)'
                                        }}>
                                            Size
                                        </div>
                                        <div style={{
                                            fontSize: 'var(--font-size-sm)',
                                            color: 'var(--color-text-primary)'
                                        }}>
                                            {dataset.size_formatted || formatBytes(dataset.size_bytes)}
                                        </div>
                                    </div>
                                    {dataset.created && (
                                        <div>
                                            <div style={{
                                                fontSize: 'var(--font-size-xs)',
                                                color: 'var(--color-text-secondary)'
                                            }}>
                                                Created
                                            </div>
                                            <div style={{
                                                fontSize: 'var(--font-size-sm)',
                                                color: 'var(--color-text-primary)'
                                            }}>
                                                {new Date(dataset.created).toLocaleDateString()}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {dataset.path && (
                                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)',
                                            marginBottom: 'var(--spacing-xs)'
                                        }}>
                                            Path
                                        </div>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            fontFamily: 'monospace',
                                            wordBreak: 'break-all',
                                            color: 'var(--color-text-secondary)',
                                            padding: 'var(--spacing-xs)',
                                            backgroundColor: 'var(--color-gray-50)',
                                            borderRadius: 'var(--radius-sm)'
                                        }}>
                                            {dataset.path}
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="card__footer">
                                <button
                                    className="btn btn--secondary btn--sm"
                                    onClick={() => toast.info('View feature coming soon')}
                                >
                                    <FolderOpen size={16} />
                                    View
                                </button>
                                <button
                                    className="btn btn--secondary btn--sm"
                                    onClick={() => handleDeleteDataset(dataset.name)}
                                >
                                    <Trash2 size={16} />
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default Datasets