import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check, FolderKanban } from 'lucide-react'
import { useProjectStore, selectSelectedProject, selectProjects } from '@/stores/projectStore'
import { toast } from '@/lib/toast'
import type { Project } from '@/types'

const ProjectSwitcher: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const projects = useProjectStore(selectProjects)
    const setSelectedProject = useProjectStore(state => state.setSelectedProject)

    const [isOpen, setIsOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

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
        setSelectedProject(project.path)
        setIsOpen(false)
        toast.success(`Switched to project: ${project.name}`)
        window.location.href = '/projects'
    }


    if (!selectedProject) {
        return (
            <div className="project-switcher">
                <div className="project-switcher__trigger" style={{ opacity: 0.6, cursor: 'default' }}>
                    <div className="project-switcher__current">
                        <FolderKanban size={20} className="project-switcher__icon" />
                        <div className="project-switcher__info">
                            <span className="project-switcher__name">No project selected</span>
                            <span className="project-switcher__count">
                                {projects.length} available
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        )
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
                        <span className="project-switcher__name">{selectedProject.name}</span>
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
                    <div className="project-switcher__header">Switch Project</div>
                    <div className="project-switcher__list">
                        {projects.map((project) => {
                            const isSelected = project.path === selectedProject.path

                            return (
                                <button
                                    key={project.path}
                                    className={`project-switcher__item ${isSelected ? 'project-switcher__item--selected' : ''}`}
                                    onClick={() => handleProjectSelect(project)}
                                >
                                    <div className="project-switcher__item-content">
                                        <FolderKanban size={16} className="project-switcher__item-icon" />
                                        <div className="project-switcher__item-info">
                                            <span className="project-switcher__item-name">{project.name}</span>
                                            <span className="project-switcher__item-path">{project.path}</span>
                                        </div>
                                    </div>
                                    {isSelected && (
                                        <Check size={16} className="project-switcher__check" />
                                    )}
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