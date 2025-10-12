import React, { useEffect, useState } from 'react'
import { Plus, Trash2, FolderOpen, RefreshCw, FolderKanban } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useProjectStore } from '@/stores/projectStore'  // ADD THIS
import type { Project } from '@/types'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import CreateProjectModal from '@/components/CreateProjectModal'
import DeleteProjectModal from '@/components/DeleteProjectModal'

const Projects: React.FC = () => {
    // Get store actions
    const setProjects = useProjectStore(state => state.setProjects)

    const [projects, setLocalProjects] = useState<Project[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
    const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
    const [deletingProject, setDeletingProject] = useState<string | null>(null)

    const loadProjects = async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await api.listProjects()

            // Update BOTH local state and global store
            setLocalProjects(response.projects)
            setProjects(response.projects)  // SYNC WITH STORE
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load projects'
            setError(message)
            toast.error(message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadProjects()
    }, [])

    const handleDeleteProject = async () => {
        if (!projectToDelete) return

        try {
            setDeletingProject(projectToDelete.path)
            await api.deleteProject(projectToDelete.path, true)
            toast.success(`Project "${projectToDelete.name}" deleted`)
            setProjectToDelete(null)

            // Reload projects to sync with store
            await loadProjects()
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete project'
            toast.error(message)
        } finally {
            setDeletingProject(null)
        }
    }

    const handleCreateSuccess = async () => {
        // Reload projects to sync with store
        await loadProjects()
    }

    if (loading) {
        return <Loading text="Loading projects..." />
    }

    if (error) {
        return <ErrorMessage message={error} />
    }

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-xs)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Projects
                    </h1>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            className="btn btn--secondary"
                            onClick={loadProjects}
                            disabled={loading}
                        >
                            <RefreshCw size={20} />
                            Refresh
                        </button>
                        <button
                            className="btn btn--primary"
                            onClick={() => setIsCreateModalOpen(true)}
                        >
                            <Plus size={20} />
                            New Project
                        </button>
                    </div>
                </div>
                <p style={{ color: 'var(--color-text-secondary)' }}>
                    Manage your ModelCub projects
                </p>
            </div>

            {/* Empty State */}
            {projects.length === 0 ? (
                <div className="empty-state">
                    <FolderOpen size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No projects yet</h3>
                    <p className="empty-state__description">
                        Create your first project to get started with ModelCub
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => setIsCreateModalOpen(true)}
                    >
                        <Plus size={20} />
                        Create Project
                    </button>
                </div>
            ) : (
                /* Projects Grid */
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {projects.map((project) => (
                        <div key={project.path} className="card">
                            <div className="card__header">
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                    <FolderKanban size={20} style={{ color: 'var(--color-primary-500)' }} />
                                    <h3 className="card__title">{project.name}</h3>
                                </div>
                            </div>

                            <div className="card__body">
                                <div style={{ marginBottom: 'var(--spacing-md)' }}>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                        Path
                                    </div>
                                    <div style={{
                                        fontSize: 'var(--font-size-sm)',
                                        fontFamily: 'monospace',
                                        wordBreak: 'break-all',
                                        color: 'var(--color-text-primary)'
                                    }}>
                                        {project.path}
                                    </div>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-sm)' }}>
                                    <div>
                                        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                            Version
                                        </div>
                                        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-primary)' }}>
                                            {project.version}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="card__footer">
                                <button
                                    className="btn btn--secondary btn--sm"
                                    onClick={() => setProjectToDelete(project)}
                                    disabled={deletingProject === project.path}
                                >
                                    <Trash2 size={16} />
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modals */}
            <CreateProjectModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={handleCreateSuccess}
            />

            {projectToDelete && (
                <DeleteProjectModal
                    project={projectToDelete}
                    isOpen={true}
                    onClose={() => setProjectToDelete(null)}
                    onConfirm={handleDeleteProject}
                    isDeleting={false}

                />
            )}
        </div>
    )
}

export default Projects