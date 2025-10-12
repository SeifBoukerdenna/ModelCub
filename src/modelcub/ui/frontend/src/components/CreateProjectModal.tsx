import React, { useState, useMemo } from 'react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'

interface CreateProjectModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
}

const validateName = (name: string): string | null => {
    if (!name) return 'Project name is required.'
    if (/^\d/.test(name)) return 'Project name cannot start with a number.'
    if (/\s/.test(name)) return 'Project name cannot contain spaces.'
    if (!/^[a-zA-Z0-9-_]+$/.test(name))
        return 'Only letters, numbers, hyphens, and underscores are allowed.'
    return null
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
    isOpen,
    onClose,
    onSuccess,
}) => {
    const [name, setName] = useState('')
    const [path, setPath] = useState('')
    const [loading, setLoading] = useState(false)
    const [submitError, setSubmitError] = useState<string | null>(null)

    // live validation
    const nameError = useMemo(() => validateName(name), [name])
    const canSubmit = !nameError && !!name && !loading

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitError(null)

        const err = validateName(name)
        if (err) {
            setSubmitError(err)
            toast.error(err)
            return
        }

        setLoading(true)
        try {
            await api.createProject(name, path || undefined)
            toast.success(`Project "${name}" created successfully!`)
            onSuccess()
            onClose()
            setName('')
            setPath('')
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to create project'
            setSubmitError(message)
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

                <form onSubmit={handleSubmit} noValidate>
                    <div className="modal__body">
                        {(submitError || nameError) && (
                            <div className="error" style={{ marginBottom: 'var(--spacing-md)' }}>
                                {submitError || nameError}
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="project-name" className="form-label">
                                Project Name *
                            </label>
                            <input
                                id="project-name"
                                type="text"
                                className={`form-input ${nameError ? 'is-invalid' : ''}`}
                                placeholder="my-project"
                                value={name}
                                onChange={(e) => setName(e.target.value.trimStart())}
                                autoComplete="off"
                                spellCheck={false}
                                inputMode="text"
                                disabled={loading}
                                aria-invalid={!!nameError}
                                aria-describedby="project-name-help"
                            />
                            <p id="project-name-help" className="form-help">
                                Allowed: <code>a–z</code>, <code>A–Z</code>, <code>0–9</code>, <code>-</code>, <code>_</code>. No spaces. Cannot start with a number.
                            </p>
                        </div>

                        <div className="form-group">
                            <label htmlFor="project-path" className="form-label">
                                Path (optional)
                            </label>
                            <input
                                id="project-path"
                                type="text"
                                className="form-input"
                                placeholder="./my-project"
                                value={path}
                                onChange={(e) => setPath(e.target.value)}
                                disabled={loading}
                            />
                            <p className="form-help">
                                Leave empty to use default: <code>./{name || 'project-name'}</code>
                            </p>
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
                        <button type="submit" className="btn btn--primary" disabled={!canSubmit}>
                            {loading ? 'Creating...' : 'Create Project'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default CreateProjectModal
