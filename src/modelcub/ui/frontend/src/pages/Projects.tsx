import React, { useEffect, useState } from 'react'
import { Plus, Trash2, RefreshCw, FolderKanban, MousePointerClick } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import type { Project } from '@/types'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import CreateProjectModal from '@/components/CreateProjectModal'
import DeleteProjectModal from '@/components/DeleteProjectModal'

const Projects: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const setProjects = useProjectStore(state => state.setProjects)
    const setSelectedProject = useProjectStore(state => state.setSelectedProject)

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
            setLocalProjects(response.projects)
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
        const wasSelected = selectedProject?.path === projectToDelete.path

        try {
            setDeletingProject(projectToDelete.path)
            await api.deleteProject(projectToDelete.path, true)
            toast.success(`Project "${projectToDelete.name}" deleted`)
            setProjectToDelete(null)

            if (wasSelected) {
                setSelectedProject(null)
            }

            await loadProjects()
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete project'
            toast.error(message)
        } finally {
            setDeletingProject(null)
        }
    }

    const handleCreateSuccess = async (newProjectPath: string) => {
        await loadProjects()

        const response = await api.listProjects()
        const newProject = response.projects.find(p => p.path === newProjectPath)
        if (newProject) {
            setSelectedProject(newProject)
            toast.success(`Project "${newProject.name}" selected`)
        }
    }

    const handleProjectClick = (project: Project) => {
        setSelectedProject(project)
        toast.success(`Switched to project: ${project.name}`)
    }

    if (loading) {
        return <Loading text="Loading projects..." />
    }

    if (error) {
        return <ErrorMessage message={error} />
    }

    return (
        <div>
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-xs)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Projects</h1>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button className="btn btn--secondary" onClick={loadProjects} disabled={loading}>
                            <RefreshCw size={20} />
                            Refresh
                        </button>
                        <button className="btn btn--primary" onClick={() => setIsCreateModalOpen(true)}>
                            <Plus size={20} />
                            New Project
                        </button>
                    </div>
                </div>
                <p style={{ color: 'var(--color-text-secondary)' }}>
                    Manage your ModelCub projects
                </p>
                {!selectedProject && projects.length > 0 && (
                    <div style={{
                        marginTop: 'var(--spacing-md)',
                        padding: 'var(--spacing-md)',
                        backgroundColor: 'var(--color-warning-100)',
                        color: 'var(--color-warning-800)',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-sm)',
                        fontSize: 'var(--font-size-sm)'
                    }}>
                        <MousePointerClick size={20} />
                        <span><strong>Click on a project card</strong> to select it and access Datasets, Models, and Settings</span>
                    </div>
                )}
            </div>

            {projects.length === 0 ? (
                <div className="empty-state">
                    <FolderKanban size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No projects yet</h3>
                    <p className="empty-state__description">
                        Create your first project to get started with ModelCub
                    </p>
                    <button className="btn btn--primary" style={{ marginTop: 'var(--spacing-lg)' }} onClick={() => setIsCreateModalOpen(true)}>
                        <Plus size={20} />
                        Create Project
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
                    {projects.map((project) => {
                        const isSelected = selectedProject?.path === project.path

                        return (
                            <div
                                key={project.path}
                                className="card"
                                style={{
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s, box-shadow 0.2s, border-color 0.2s',
                                    border: isSelected ? '2px solid var(--color-primary-500)' : '2px solid transparent',
                                    transform: isSelected ? 'translateY(-2px)' : 'none',
                                    boxShadow: isSelected ? '0 4px 12px rgba(0, 0, 0, 0.15)' : 'none'
                                }}
                                onClick={() => handleProjectClick(project)}
                            >
                                <div className="card__header">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                        <FolderKanban size={20} style={{ color: isSelected ? 'var(--color-primary-500)' : 'var(--color-text-secondary)' }} />
                                        <h3 className="card__title">{project.name}</h3>
                                    </div>
                                    {isSelected && (
                                        <span className="badge" style={{ backgroundColor: 'var(--color-primary-100)', color: 'var(--color-primary-700)' }}>
                                            Selected
                                        </span>
                                    )}
                                </div>

                                <div className="card__body">
                                    <div style={{ marginBottom: 'var(--spacing-md)' }}>
                                        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                            Path
                                        </div>
                                        <div style={{ fontSize: 'var(--font-size-sm)', fontFamily: 'monospace', wordBreak: 'break-all', color: 'var(--color-text-primary)' }}>
                                            {project.path}
                                        </div>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-sm)' }}>
                                        <div>
                                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>Version</div>
                                            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-primary)' }}>{project.version}</div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>Created</div>
                                            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-primary)' }}>
                                                {new Date(project.created).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>

                                    {!isSelected && (
                                        <div style={{
                                            marginTop: 'var(--spacing-md)',
                                            padding: 'var(--spacing-sm)',
                                            backgroundColor: 'var(--color-gray-100)',
                                            borderRadius: 'var(--radius-sm)',
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 'var(--spacing-xs)'
                                        }}>
                                            <MousePointerClick size={14} />
                                            Click to select
                                        </div>
                                    )}
                                </div>

                                <div className="card__footer">
                                    <button
                                        className="btn btn--secondary btn--sm"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            setProjectToDelete(project)
                                        }}
                                        disabled={deletingProject === project.path}
                                    >
                                        <Trash2 size={16} />
                                        Delete
                                    </button>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

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