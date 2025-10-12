import React, { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Project } from '@/types'

interface DeleteProjectModalProps {
    project: Project
    isOpen: boolean
    onClose: () => void
    onConfirm: () => void
    isDeleting: boolean
}

const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({
    isOpen,
    project,
    onClose,
    onConfirm,
    isDeleting,
}) => {
    const [confirmText, setConfirmText] = useState('')

    const handleConfirm = () => {
        if (confirmText === project.name) {
            onConfirm()
        }
    }

    if (!isOpen) return null

    const isConfirmed = confirmText === project.name

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal modal--danger" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                        <AlertTriangle size={24} style={{ color: 'var(--color-error)' }} />
                        <h2 className="modal__title">Delete Project</h2>
                    </div>
                </div>

                <div className="modal__body">
                    <div className="alert alert--danger" style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <p style={{ fontWeight: 'var(--font-weight-semibold)', marginBottom: 'var(--spacing-xs)' }}>
                            ⚠️ This action cannot be undone
                        </p>
                        <p style={{ fontSize: 'var(--font-size-sm)' }}>
                            This will permanently delete the project and all its contents.
                        </p>
                    </div>

                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', marginBottom: 'var(--spacing-xs)' }}>
                            <strong>Project:</strong> {project.name}
                        </div>
                        <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                            <strong>Path:</strong>
                            <code style={{ display: 'block', marginTop: 'var(--spacing-xs)', padding: 'var(--spacing-xs)', backgroundColor: 'var(--color-gray-100)', borderRadius: 'var(--border-radius-sm)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {project.path}
                            </code>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirm-delete" className="form-label">
                            Type <strong>{project.name}</strong> to confirm deletion:
                        </label>
                        <input
                            id="confirm-delete"
                            type="text"
                            className="form-input"
                            placeholder={project.name}
                            value={confirmText}
                            onChange={(e) => setConfirmText(e.target.value)}
                            disabled={isDeleting}
                            autoComplete="off"
                        />
                    </div>
                </div>

                <div className="modal__footer">
                    <button
                        type="button"
                        className="btn btn--secondary"
                        onClick={onClose}
                        disabled={isDeleting}
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        className="btn btn--danger"
                        onClick={handleConfirm}
                        disabled={!isConfirmed || isDeleting}
                    >
                        {isDeleting ? 'Deleting...' : 'Delete Project'}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default DeleteProjectModal