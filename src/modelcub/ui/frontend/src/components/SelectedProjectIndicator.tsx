// src/modelcub/ui/frontend/src/components/SelectedProjectIndicator.tsx
import React from 'react'
import { CheckCircle } from 'lucide-react'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'

const SelectedProjectIndicator: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)

    if (!selectedProject) {
        return null
    }

    return (
        <div className="selected-indicator">
            <CheckCircle size={14} className="selected-indicator__icon" />
            <span className="selected-indicator__text">
                Selected: {selectedProject.name}
            </span>
        </div>
    )
}

export default SelectedProjectIndicator