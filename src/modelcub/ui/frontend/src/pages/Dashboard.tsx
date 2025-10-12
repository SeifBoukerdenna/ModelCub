import React, { useState } from 'react'
import { useProject } from '@/hooks/useProject'
import { Activity, Database, Brain, FolderKanban, Plus, LucideIcon } from 'lucide-react'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'
import CreateProjectModal from '@/components/CreateProjectModal'

interface StatCardData {
    name: string
    value: string
    icon: LucideIcon
    iconColor: string
}

const Dashboard: React.FC = () => {
    const { project, projects, loading, error, reload } = useProject()
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

    const handleCreateSuccess = async () => {
        // Reload projects after creation to sync store
        await reload()
    }

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
                    onSuccess={handleCreateSuccess}
                />
            </>
        )
    }

    // Should never happen, but just in case
    if (!project) {
        return (
            <ErrorMessage message="No project selected. Please select a project from the dropdown above." />
        )
    }

    // Placeholder stats - in real app, these would come from API
    const stats: StatCardData[] = [
        {
            name: 'Datasets',
            value: '0',
            icon: Database,
            iconColor: 'var(--color-primary-500)',
        },
        {
            name: 'Models',
            value: '0',
            icon: Brain,
            iconColor: 'var(--color-success)',
        },
        {
            name: 'Training Runs',
            value: '0',
            icon: Activity,
            iconColor: 'var(--color-info)',
        },
    ]

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    Dashboard
                </h1>
                <p style={{ color: 'var(--color-text-secondary)' }}>
                    Overview of your project: {project.name}
                </p>
            </div>

            {/* Stats Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: 'var(--spacing-lg)',
                marginBottom: 'var(--spacing-xl)'
            }}>
                {stats.map((stat) => (
                    <div key={stat.name} className="card">
                        <div className="card__body">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <div>
                                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                        {stat.name}
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                                        {stat.value}
                                    </div>
                                </div>
                                <stat.icon size={40} style={{ color: stat.iconColor, opacity: 0.8 }} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Project Details */}
            <div className="card">
                <div className="card__header">
                    <h2 className="card__title">Project Details</h2>
                </div>
                <div className="card__body">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-lg)' }}>
                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Project Name
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                {project.name}
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Project Path
                            </div>
                            <div style={{ fontSize: 'var(--font-size-sm)', fontFamily: 'monospace', color: 'var(--color-text-primary)' }}>
                                {project.path}
                            </div>
                        </div>


                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Version
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                {project.version}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Configuration Section */}
            <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card__header">
                    <h2 className="card__title">Configuration</h2>
                </div>
                <div className="card__body">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--spacing-lg)' }}>
                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Device
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontFamily: 'monospace', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                MPS
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Batch Size
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                32
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Image Size
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                640px
                            </div>
                        </div>

                        <div>
                            <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                Format
                            </div>
                            <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                YOLO
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard