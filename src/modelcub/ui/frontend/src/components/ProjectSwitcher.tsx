import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check, FolderKanban } from 'lucide-react'
import type { Project } from '@/types'

interface ProjectSwitcherProps {
    currentProject: Project
    projects: Project[]
    onProjectChange: (project: Project) => void
}

const ProjectSwitcher: React.FC<ProjectSwitcherProps> = ({
    currentProject,
    projects,
    onProjectChange,
}) => {
    const [isOpen, setIsOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false)
            }
        }

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [isOpen])

    // Close dropdown on escape
    useEffect(() => {
        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsOpen(false)
            }
        }

        if (isOpen) {
            document.addEventListener('keydown', handleEscape)
        }

        return () => {
            document.removeEventListener('keydown', handleEscape)
        }
    }, [isOpen])

    const handleProjectSelect = (project: Project) => {
        onProjectChange(project)
        setIsOpen(false)
    }

    return (
        <div className="project-switcher" ref={dropdownRef}>
            <button
                className="project-switcher__trigger"
                onClick={() => setIsOpen(!isOpen)}
                aria-expanded={isOpen}
                aria-haspopup="true"
            >
                <div className="project-switcher__current">
                    <FolderKanban size={20} className="project-switcher__icon" />
                    <div className="project-switcher__info">
                        <span className="project-switcher__name">{currentProject.name}</span>
                        <span className="project-switcher__count">
                            {projects.length} {projects.length === 1 ? 'project' : 'projects'}
                        </span>
                    </div>
                </div>
                <ChevronDown
                    size={16}
                    className={`project-switcher__chevron ${isOpen ? 'project-switcher__chevron--open' : ''}`}
                />
            </button>

            {isOpen && (
                <div className="project-switcher__dropdown">
                    <div className="project-switcher__header">
                        <span>Switch Project</span>
                    </div>
                    <div className="project-switcher__list">
                        {projects.map((project) => {
                            const isActive = project.path === currentProject.path
                            return (
                                <button
                                    key={project.path}
                                    className={`project-switcher__item ${isActive ? 'project-switcher__item--active' : ''
                                        }`}
                                    onClick={() => handleProjectSelect(project)}
                                >
                                    <div className="project-switcher__item-content">
                                        <div className="project-switcher__item-name">{project.name}</div>
                                        <div className="project-switcher__item-path">{project.path}</div>
                                    </div>
                                    {isActive && <Check size={16} className="project-switcher__check" />}
                                </button>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}

export default ProjectSwitcher