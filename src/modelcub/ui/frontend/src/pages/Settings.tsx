import React from 'react'
import ProjectGuard from '@/guards/ProjectGuard'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { Settings as SettingsIcon } from 'lucide-react'

const Settings: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)

    return (
        <ProjectGuard>
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>
                        Settings
                    </h1>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Project: <strong>{selectedProject?.name}</strong>
                    </p>
                </div>

                <div className="empty-state">
                    <SettingsIcon size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">Settings Coming Soon</h3>
                    <p className="empty-state__description">
                        Project configuration and preferences will be available here
                    </p>
                </div>
            </div>
        </ProjectGuard>
    )
}

export default Settings