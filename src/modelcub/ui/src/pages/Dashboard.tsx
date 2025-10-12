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
    const { project, loading, error, reload } = useProject()
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

    if (loading) {
        return <Loading text="Loading project..." />
    }

    if (error) {
        return <ErrorMessage message={error} />
    }

    if (!project) {
        return (
            <>
                <div className="empty-state">
                    <FolderKanban className="empty-state__icon" size={48} />
                    <h3 className="empty-state__title">No project found</h3>
                    <p className="empty-state__description">
                        Create a new project to get started
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

                <CreateProjectModal
                    isOpen={isCreateModalOpen}
                    onClose={() => setIsCreateModalOpen(false)}
                    onSuccess={reload}
                />
            </>
        )
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
            {/* Header */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-md)',
                }}
            >
                <div>
                    <h1>{project.name}</h1>
                    <p className="u-text-gray-500 u-mt-1">
                        Created {new Date(project.created).toLocaleDateString()}
                    </p>
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

            {/* Project Config */}
            <div className="card">
                <div className="card__header">
                    <h2 className="card__title">Configuration</h2>
                </div>
                <div className="card__body">
                    <dl
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: 'var(--spacing-md)',
                        }}
                    >
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)' }}>
                                Device
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config.device}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)' }}>
                                Batch Size
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config.batch_size}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)' }}>
                                Image Size
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config.image_size}
                            </dd>
                        </div>
                        <div>
                            <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)' }}>
                                Format
                            </dt>
                            <dd
                                style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-gray-900)',
                                }}
                            >
                                {project.config.format}
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