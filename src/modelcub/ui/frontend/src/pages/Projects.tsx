import React, { useEffect, useState } from 'react'
import { Plus, Trash2, FolderKanban, RefreshCw } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'
import { useProjectStore } from '@/stores/projectStore'
import Loading from '@/components/Loading'
import CreateProjectModal from '@/components/CreateProjectModal'
import DeleteProjectModal from '@/components/DeleteProjectModal'
import type { Project } from '@/types'

const Projects: React.FC = () => {
    const { projects, setProjects, selectedProjectPath, setSelectedProject } = useProjectStore()
    const [loading, setLoading] = useState(true)
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
    const [isDeleting, setIsDeleting] = useState(false)

    const loadProjects = async () => {
        try {
            setLoading(true)
            const response = await api.listProjects()

            if (response.success) {
                setProjects(response.projects)

                // Auto-select logic
                if (response.projects.length > 0) {
                    const savedPath = selectedProjectPath
                    const savedExists = savedPath && response.projects.some(p => p.path === savedPath)

                    if (savedExists) {
                        // Saved project still exists, keep it selected
                        console.log('Restored selected project:', savedPath)
                    } else {
                        // No saved project or it doesn't exist, select first
                        if (response.projects[0]) {
                            setSelectedProject(response.projects[0].path)
                            console.log('Auto-selected first project:', response.projects[0].path)
                        }
                    }
                }
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load projects'
            toast.error(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadProjects()
    }, [])

    const handleCreateSuccess = (projectPath: string) => {
        loadProjects()
        setSelectedProject(projectPath)
    }

    const handleDeleteClick = (project: Project) => {
        setProjectToDelete(project)
        setShowDeleteModal(true)
    }

    const handleDeleteConfirm = async () => {
        if (!projectToDelete) return

        try {
            setIsDeleting(true)
            const response = await api.deleteProject(projectToDelete.path, true)

            if (response.success) {
                toast.success(`Project "${projectToDelete.name}" deleted`)

                // If we deleted the selected project, clear selection
                if (projectToDelete.path === selectedProjectPath) {
                    setSelectedProject(null)
                }

                setShowDeleteModal(false)
                setProjectToDelete(null)
                await loadProjects()
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete project'
            toast.error(message)
        } finally {
            setIsDeleting(false)
        }
    }

    if (loading) {
        return <Loading message="Loading projects..." />
    }

    return (
        <div>
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-md)'
                }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Projects
                    </h1>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button className="btn btn--secondary" onClick={loadProjects}>
                            <RefreshCw size={20} />
                            Refresh
                        </button>
                        <button className="btn btn--primary" onClick={() => setShowCreateModal(true)}>
                            <Plus size={20} />
                            New Project
                        </button>
                    </div>
                </div>
            </div>

            {projects.length === 0 ? (
                <div className="empty-state">
                    <FolderKanban size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No projects yet</h3>
                    <p className="empty-state__description">
                        Create your first project to get started with ModelCub
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => setShowCreateModal(true)}
                    >
                        <Plus size={20} />
                        Create Project
                    </button>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {projects.map((project) => {
                        const isSelected = project.path === selectedProjectPath

                        return (
                            <div
                                key={project.path}
                                className="card"
                                style={{
                                    cursor: 'pointer',
                                    border: isSelected ? '2px solid var(--color-primary-500)' : undefined,
                                    boxShadow: isSelected ? '0 0 0 3px var(--color-primary-100)' : undefined
                                }}
                                onClick={() => setSelectedProject(project.path)}
                            >
                                <div className="card__header">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                        <FolderKanban size={20} style={{ color: 'var(--color-primary-500)' }} />
                                        <h3 className="card__title">{project.name}</h3>
                                    </div>
                                    {isSelected && (
                                        <span className="badge" style={{
                                            backgroundColor: 'var(--color-primary-100)',
                                            color: 'var(--color-primary-700)'
                                        }}>
                                            Active
                                        </span>
                                    )}
                                </div>

                                <div className="card__body">
                                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                                        <div style={{ marginBottom: 'var(--spacing-xs)' }}>
                                            <strong>Path:</strong>
                                        </div>
                                        <code style={{
                                            display: 'block',
                                            padding: 'var(--spacing-xs)',
                                            backgroundColor: 'var(--color-surface)',
                                            borderRadius: 'var(--border-radius-sm)',
                                            wordBreak: 'break-all',
                                            fontSize: 'var(--font-size-xs)'
                                        }}>
                                            {project.path}
                                        </code>
                                    </div>
                                </div>

                                <div className="card__footer">
                                    <button
                                        className="btn btn--text btn--sm"
                                        style={{ color: 'var(--color-error-500)' }}
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            handleDeleteClick(project)
                                        }}
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
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSuccess={handleCreateSuccess}
            />

            {projectToDelete && (
                <DeleteProjectModal
                    isOpen={showDeleteModal}
                    project={projectToDelete}
                    onClose={() => {
                        setShowDeleteModal(false)
                        setProjectToDelete(null)
                    }}
                    onConfirm={handleDeleteConfirm}
                    isDeleting={isDeleting}
                />
            )}
        </div>
    )
}

export default Projects