import React, { useEffect, useState } from 'react'
import { Trash2, Database, RefreshCw, Upload } from 'lucide-react'
import { api, Dataset } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import ImportDatasetModal from '@/components/ImportDatasetModal'

const Datasets: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const setProjects = useProjectStore(state => state.setProjects)
    const [datasets, setDatasets] = useState<Dataset[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [showImportModal, setShowImportModal] = useState(false)

    useEffect(() => {
        const init = async () => {
            if (!selectedProject) {
                try {
                    const response = await api.listProjects()
                    if (response.success && response.projects.length > 0) {
                        setProjects(response.projects)
                    }
                } catch (err) {
                    console.error('Failed to load projects:', err)
                }
            }
        }
        init()
    }, [])

    const loadDatasets = async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await api.listDatasets()
            if (response.success) {
                setDatasets(response.datasets)
            } else {
                throw new Error(response.message || 'Failed to load datasets')
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : 'Failed to load datasets'
            setError(msg)
            toast.error(msg)
            setDatasets([])
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (selectedProject) {
            api.setCurrentProject(selectedProject.path)
            loadDatasets()
        } else {
            api.setCurrentProject(null)
            setLoading(false)
            setError('No project selected')
        }
    }, [selectedProject])

    if (loading) return <Loading message="Loading datasets..." />

    if (!selectedProject) {
        return (
            <div className="empty-state">
                <Database size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">No Project Selected</h3>
                <p className="empty-state__description">Select a project to manage datasets</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="empty-state">
                <ErrorMessage message={error} />
                <button className="btn btn--primary" style={{ marginTop: 'var(--spacing-lg)' }} onClick={loadDatasets}>
                    <RefreshCw size={20} /> Retry
                </button>
            </div>
        )
    }

    return (
        <div>
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-xs)' }}>
                    <div>
                        <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Datasets</h1>
                        <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Project: <strong>{selectedProject.name}</strong>
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button className="btn btn--secondary" onClick={loadDatasets} disabled={loading}>
                            <RefreshCw size={20} /> Refresh
                        </button>
                        <button className="btn btn--primary" onClick={() => setShowImportModal(true)}>
                            <Upload size={20} /> Import Dataset
                        </button>
                    </div>
                </div>
            </div>

            {datasets.length === 0 ? (
                <div className="empty-state">
                    <Database size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No datasets yet</h3>
                    <p className="empty-state__description">Import images to create your first dataset</p>
                    <button className="btn btn--primary" style={{ marginTop: 'var(--spacing-lg)' }} onClick={() => setShowImportModal(true)}>
                        <Upload size={20} /> Import Dataset
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 'var(--spacing-lg)' }}>
                    {datasets.map((dataset) => (
                        <div key={dataset.id} className="card">
                            <div className="card__header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                    <Database size={20} style={{ color: 'var(--color-primary-500)' }} />
                                    <h3 className="card__title">{dataset.name}</h3>
                                </div>
                                <span className="badge" style={{
                                    backgroundColor: dataset.status === 'ready' ? 'var(--color-success-100)' : 'var(--color-warning-100)',
                                    color: dataset.status === 'ready' ? 'var(--color-success-700)' : 'var(--color-warning-700)'
                                }}>
                                    {dataset.status}
                                </span>
                            </div>

                            <div className="card__body">
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-sm)' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>Images:</span>
                                        <span style={{ fontWeight: 500 }}>{dataset.images}</span>
                                    </div>
                                    {dataset.classes && dataset.classes.length > 0 && (
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-sm)' }}>
                                            <span style={{ color: 'var(--color-text-secondary)' }}>Classes:</span>
                                            <span style={{ fontWeight: 500 }}>{dataset.classes.length}</span>
                                        </div>
                                    )}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--font-size-sm)' }}>
                                        <span style={{ color: 'var(--color-text-secondary)' }}>Size:</span>
                                        <span style={{ fontWeight: 500 }}>{dataset.size_formatted}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <button className="btn btn--text btn--sm" onClick={() => toast.info('Coming soon')}>
                                    View Details
                                </button>
                                <button className="btn btn--text btn--sm" onClick={() => toast.info('Coming soon')}>
                                    <Trash2 size={16} /> Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <ImportDatasetModal isOpen={showImportModal} onClose={() => setShowImportModal(false)} onSuccess={loadDatasets} />
        </div>
    )
}

export default Datasets