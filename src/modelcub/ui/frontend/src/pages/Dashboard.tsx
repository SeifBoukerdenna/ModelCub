import React, { useState } from 'react'
import { useProject } from '@/hooks/useProject'
import { Activity, Database, Brain, FolderKanban, Plus, LucideIcon } from 'lucide-react'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import CreateProjectModal from '@/components/CreateProjectModal'
import ProjectSwitcher from '@/components/ProjectSwitcher'

interface StatCardData {
    name: string
    value: string
    icon: LucideIcon
    iconColor: string
}

const Dashboard: React.FC = () => {
    const { project, projects, loading, error, reload, setActiveProject } = useProject()
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

    if (loading) {
        return <Loading text="Loading projects..." />
    }

    if (error) {
        return <ErrorMessage message={error} />
    }

    // No projects at all - show empty state
    if (!project && projects.length === 0) {
        return (
            <>
                <div className="empty-state">
                    <FolderKanban className="empty-state__icon" size={48} />
                    <h3 className="empty-state__title">No projects found</h3>
                    <p className="empty-state__description">
                        Create your first project to get started with ModelCub
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => setIsCreateModalOpen(true)}
                    >
                        <Plus size={20} />
                        Create Your First Project
                    </button>
                </div>

                <CreateProjectModal
                    isOpen={isCreateModalOpen}
                    onClose={() => setIsCreateModalOpen(false)}
                    onSuccess={reload}
                />
            </>
        )
    }

    // Should never happen, but just in case
    if (!project) {
        return <ErrorMessage message="Unable to load project data" />
    }

    const stats: StatCardData[] = [
        {
            name: 'Datasets',
            value: '0',
            icon: Database,
            iconColor: 'stat-card__icon--blue',
        },
        {
            name: 'Models',
            value: '0',
            icon: Brain,
            iconColor: 'stat-card__icon--purple',
        },
        {
            name: 'Training Runs',
            value: '0',
            icon: Activity,
            iconColor: 'stat-card__icon--green',
        },
    ]

    return (
        <div>
            {/* Header with Project Switcher */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: 'var(--spacing-xl)',
                }}
            >
                <div style={{ flex: 1 }}>
                    {projects.length > 1 ? (
                        <ProjectSwitcher
                            currentProject={project}
                            projects={projects}
                            onProjectChange={setActiveProject}
                        />
                    ) : (
                        <div>
                            <h1>{project.name}</h1>
                            <p className="u-text-gray-500 u-mt-1">
                                Created {new Date(project.created).toLocaleDateString()}
                            </p>
                        </div>
                    )}
                </div>
                <button
                    className="btn btn--primary"
                    onClick={() => setIsCreateModalOpen(true)}
                >
                    <Plus size={20} />
                    New Project
                </button>
            </div>

            {/* Stats Grid */}
            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: 'var(--spacing-lg)',
                    marginBottom: 'var(--spacing-2xl)',
                }}
            >
                {stats.map((stat) => {
                    const Icon = stat.icon
                    return (
                        <div key={stat.name} className="stat-card">
                            <div className="stat-card__content">
                                <div className="stat-card__label">{stat.name}</div>
                                <div className="stat-card__value">{stat.value}</div>
                            </div>
                            <Icon size={32} className={`stat-card__icon ${stat.iconColor}`} />
                        </div>
                    )
                })}
            </div>

            {/* Project Details Card */}
            <div className="card">
                <div className="card__header">
                    <h2 className="card__title">Project Details</h2>
                </div>
                <div className="card__body">
                    <dl
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                            gap: 'var(--spacing-lg)',
                        }}
                    >
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Project Name
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.name}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Project Path
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-gray-600)',
                                    fontFamily: 'monospace',
                                    wordBreak: 'break-all',
                                }}
                            >
                                {project.path}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Created
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {new Date(project.created).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                })}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Version
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.version}
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>

            {/* Configuration Card */}
            <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card__header">
                    <h2 className="card__title">Configuration</h2>
                </div>
                <div className="card__body">
                    <dl
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                            gap: 'var(--spacing-lg)',
                        }}
                    >
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Device
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                    textTransform: 'uppercase',
                                    fontWeight: 600,
                                }}
                            >
                                {project.config?.device}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Batch Size
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config?.batch_size}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Image Size
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config?.image_size}px
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500 }}>
                                Format
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-base)',
                                    color: 'var(--color-gray-900)',
                                    textTransform: 'uppercase',
                                }}
                            >
                                {project.config?.format}
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>

            <CreateProjectModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSuccess={reload}
            />
        </div>
    )
}

export default Dashboard