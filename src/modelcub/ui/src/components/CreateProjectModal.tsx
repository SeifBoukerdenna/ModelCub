import React, { useState } from 'react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'

interface CreateProjectModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
    isOpen,
    onClose,
    onSuccess,
}) => {
    const [name, setName] = useState('')
    const [path, setPath] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            await api.createProject(name, path || undefined)
            toast.success(`Project "${name}" created successfully!`)
            onSuccess()
            onClose()
            // Reset form
            setName('')
            setPath('')
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create project'
            setError(message)
            toast.error(message)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">Create New Project</h2>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {error && (
                            <div className="error" style={{ marginBottom: 'var(--spacing-md)' }}>
                                {error}
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="project-name" className="form-label">
                                Project Name *
                            </label>
                            <input
                                id="project-name"
                                type="text"
                                className="form-input"
                                placeholder="my-project"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="project-path" className="form-label">
                                Path (optional)
                            </label>
                            <input
                                id="project-path"
                                type="text"
                                className="form-input"
                                placeholder={`./my-project`}
                                value={path}
                                onChange={(e) => setPath(e.target.value)}
                                disabled={loading}
                            />
                            <p className="form-help">Leave empty to use default: ./{name || 'project-name'}</p>
                        </div>
                    </div>

                    <div className="modal__footer">
                        <button
                            type="button"
                            className="btn btn--secondary"
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button type="submit" className="btn btn--primary" disabled={loading || !name}>
                            {loading ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default CreateProjectModal