import React, { useEffect, useState } from 'react'
import { Plus, Trash2, FolderOpen, RefreshCw } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'
import type { Project } from '@/types'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import CreateProjectModal from '@/components/CreateProjectModal'
import DeleteProjectModal from '@/components/DeleteProjectModal'

const Projects: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([])
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
            setProjects(response.projects)
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
            loadProjects()
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete project'
            toast.error(message)
        } finally {
            setDeletingProject(null)
        }
    }

    const handleCreateSuccess = () => {
        toast.success('Project created successfully!')
        loadProjects()
    }

    if (loading) {
        return <Loading text="Loading projects..." />
    }

    if (error) {
        return (
            <div>
                <ErrorMessage message={error} />
                <button
                    className="btn btn--primary"
                    style={{ marginTop: 'var(--spacing-md)' }}
                    onClick={loadProjects}
                >
                    <RefreshCw size={20} />
                    Retry
                </button>
            </div>
        )
    }

    return (
        <div>
            {/* Header */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-xl)',
                }}
            >
                <div>
                    <h1>Projects</h1>
                    <p className="u-text-gray-600 u-mt-1">
                        {projects.length} project{projects.length !== 1 ? 's' : ''} found
                    </p>
                </div>
                <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                    <button className="btn btn--secondary" onClick={loadProjects}>
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

            {/* Projects Grid */}
            {projects.length === 0 ? (
                <div className="empty-state">
                    <FolderOpen className="empty-state__icon" size={48} />
                    <h3 className="empty-state__title">No projects found</h3>
                    <p className="empty-state__description">
                        Create your first project to get started
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
                <div
                    style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                        gap: 'var(--spacing-lg)',
                    }}
                >
                    {projects.map((project) => (
                        <div key={project.path} className="card">
                            <div
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'flex-start',
                                    marginBottom: 'var(--spacing-md)',
                                }}
                            >
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <h3
                                        style={{
                                            fontSize: 'var(--font-size-lg)',
                                            fontWeight: 'var(--font-weight-semibold)',
                                            marginBottom: 'var(--spacing-xs)',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap',
                                        }}
                                    >
                                        {project.name}
                                    </h3>
                                    {project.is_current && (
                                        <span
                                            style={{
                                                display: 'inline-block',
                                                padding: '2px 8px',
                                                fontSize: 'var(--font-size-xs)',
                                                fontWeight: 'var(--font-weight-medium)',
                                                color: 'var(--color-primary-700)',
                                                backgroundColor: 'var(--color-primary-50)',
                                                borderRadius: 'var(--border-radius-sm)',
                                            }}
                                        >
                                            Current
                                        </span>
                                    )}
                                </div>
                                <button
                                    className="btn btn--danger"
                                    style={{ padding: 'var(--spacing-xs)' }}
                                    onClick={() => setProjectToDelete(project)}
                                    disabled={deletingProject === project.path}
                                    title="Delete project"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>

                            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                                <div style={{ marginBottom: 'var(--spacing-xs)' }}>
                                    <strong>Path:</strong>{' '}
                                    <code
                                        style={{
                                            fontSize: 'var(--font-size-xs)',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            display: 'block',
                                        }}
                                    >
                                        {project.path}
                                    </code>
                                </div>
                                <div>
                                    <strong>Created:</strong>{' '}
                                    {new Date(project.created).toLocaleDateString()}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <CreateProjectModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={handleCreateSuccess}
            />

            <DeleteProjectModal
                isOpen={!!projectToDelete}
                projectName={projectToDelete?.name || ''}
                projectPath={projectToDelete?.path || ''}
                onClose={() => setProjectToDelete(null)}
                onConfirm={handleDeleteProject}
                isDeleting={!!deletingProject}
            />
        </div>
    )
}

export default Projects