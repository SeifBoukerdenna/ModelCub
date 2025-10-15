import React, { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useProjectStore, selectSelectedProject, selectLoading } from '@/stores/projectStore'
import { FolderOpen } from 'lucide-react'

interface ProjectGuardProps {
    children: React.ReactNode
}

const ProjectGuard: React.FC<ProjectGuardProps> = ({ children }) => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const selectedProjectPath = useProjectStore(state => state.selectedProjectPath)
    const loading = useProjectStore(selectLoading)
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        // Only redirect if:
        // 1. Projects are loaded (not loading)
        // 2. No project path is selected
        // 3. We're not already on /projects
        if (!loading && !selectedProjectPath && location.pathname !== '/projects') {
            console.log('No project selected, redirecting to /projects')
            navigate('/projects', { replace: true })
        }
    }, [selectedProjectPath, loading, navigate, location.pathname])

    // Show loading state while projects are loading
    if (loading) {
        return (
            <div className="empty-state">
                <FolderOpen size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">Loading...</h3>
                <p className="empty-state__description">
                    Loading project data...
                </p>
            </div>
        )
    }

    // Show loading state while redirecting (no project path selected)
    if (!selectedProjectPath) {
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

    // Show error if project path exists but project not found (shouldn't happen normally)
    if (!selectedProject) {
        return (
            <div className="empty-state">
                <FolderOpen size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">Project Not Found</h3>
                <p className="empty-state__description">
                    The selected project could not be found.
                </p>
            </div>
        )
    }

    return <>{children}</>
}

export default ProjectGuard