import React from 'react'
import ProjectGuard from '@/guards/ProjectGuard'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { Cpu } from 'lucide-react'

const Models: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)

    return (
        <ProjectGuard>
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Models
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: <strong>{selectedProject?.name}</strong>
                    </p>
                </div>

                <div className="empty-state">
                    <Cpu size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No models yet</h3>
                    <p className="empty-state__description">
                        Train models from your datasets to get started
                    </p>
                </div>
            </div>
        </ProjectGuard>
    )
}

export default Models