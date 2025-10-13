import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { FolderOpen } from 'lucide-react'

interface ProjectGuardProps {
    children: React.ReactNode
}

const ProjectGuard: React.FC<ProjectGuardProps> = ({ children }) => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const navigate = useNavigate()

    useEffect(() => {
        if (!selectedProject) {
            navigate('/projects')
        }
    }, [selectedProject, navigate])

    if (!selectedProject) {
        return (
            <div className="empty-state">
                <FolderOpen size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">No Project Selected</h3>
                <p className="empty-state__description">
                    Please select a project to continue
                </p>
            </div>
        )
    }

    return <>{children}</>
}

export default ProjectGuard