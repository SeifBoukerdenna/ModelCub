import React, { useState } from 'react'
import { X } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'

interface CreateProjectModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: (projectPath: string) => void
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const [name, setName] = useState('')
    const [path, setPath] = useState('')
    const [creating, setCreating] = useState(false)

    if (!isOpen) return null

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!name.trim()) {
            toast.error('Project name is required')
            return
        }

        try {
            setCreating(true)
            const response = await api.createProject(name.trim(), path.trim() || undefined)

            if (response.success && response.data) {
                toast.success(`Project "${name}" created`)
                const projectPath = response.data.path as string
                setName('')
                setPath('')
                onClose()
                onSuccess(projectPath)
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create project'
            toast.error(message)
        } finally {
            setCreating(false)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">Create New Project</h2>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        <div className="form-group">
                            <label htmlFor="project-name" className="form-label">
                                Project Name <span style={{ color: 'var(--color-error-500)' }}>*</span>
                            </label>
                            <input
                                id="project-name"
                                type="text"
                                className="form-input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="my-project"
                                disabled={creating}
                                autoFocus
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="project-path" className="form-label">
                                Path <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>(optional)</span>
                            </label>
                            <input
                                id="project-path"
                                type="text"
                                className="form-input"
                                value={path}
                                onChange={(e) => setPath(e.target.value)}
                                placeholder="Leave empty for default location"
                                disabled={creating}
                            />
                            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                                Absolute or relative path for the project directory
                            </p>
                        </div>
                    </div>

                    <div className="modal__footer">
                        <button type="button" className="btn btn--secondary" onClick={onClose} disabled={creating}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn--primary" disabled={creating || !name.trim()}>
                            {creating ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default CreateProjectModal