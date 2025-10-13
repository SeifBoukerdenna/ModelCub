import React from 'react'
import ProjectGuard from '@/guards/ProjectGuard'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { BarChart3, Database, Cpu, TrendingUp } from 'lucide-react'

const Dashboard: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)

    return (
        <ProjectGuard>
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Dashboard
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: <strong>{selectedProject?.name}</strong>
                    </p>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: 'var(--spacing-lg)',
                    marginBottom: 'var(--spacing-xl)'
                }}>
                    <div className="card">
                        <div className="card__body">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                                <Database size={32} style={{ color: 'var(--color-primary-500)' }} />
                                <div>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                        Datasets
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 600 }}>
                                        0
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="card__body">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                                <Cpu size={32} style={{ color: 'var(--color-success-500)' }} />
                                <div>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                        Models
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 600 }}>
                                        0
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="card__body">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                                <TrendingUp size={32} style={{ color: 'var(--color-warning-500)' }} />
                                <div>
                                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                        Training Runs
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 600 }}>
                                        0
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="empty-state">
                    <BarChart3 size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">Dashboard Coming Soon</h3>
                    <p className="empty-state__description">
                        Project overview and statistics will be displayed here
                    </p>
                </div>
            </div>
        </ProjectGuard>
    )
}

export default Dashboard