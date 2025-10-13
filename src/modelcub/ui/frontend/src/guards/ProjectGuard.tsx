import React, { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import { FolderOpen } from 'lucide-react'

interface ProjectGuardProps {
    children: React.ReactNode
}

const ProjectGuard: React.FC<ProjectGuardProps> = ({ children }) => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        // Only redirect if no project is selected and we're not already on /projects
        if (!selectedProject && location.pathname !== '/projects') {
            console.log('No project selected, redirecting to /projects')
            navigate('/projects', { replace: true })
        }
    }, [selectedProject, navigate, location.pathname])

    // Show loading state while redirecting
    if (!selectedProject) {
        return (
            <div className="empty-state">
                <FolderOpen size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">No Project Selected</h3>
                <p className="empty-state__description">
                    Redirecting to projects page...
                </p>
            </div>
        )
    }

    return <>{children}</>
}

export default ProjectGuard