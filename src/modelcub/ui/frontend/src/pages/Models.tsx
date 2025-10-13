import React from 'react'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { Brain } from 'lucide-react'

const Models: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)

    return (
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
                <Brain size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">No models yet</h3>
                <p className="empty-state__description">
                    Train models from your datasets using: <code>modelcub train dataset-name</code>
                </p>
            </div>
        </div>
    )
}

export default Models