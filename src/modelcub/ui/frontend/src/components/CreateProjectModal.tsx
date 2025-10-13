import { useState } from 'react';
import { Plus, X, AlertCircle } from 'lucide-react';

interface CreateProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string, path?: string) => Promise<void>;
    isCreating: boolean;
}

const CreateProjectModal = ({ isOpen, onClose, onSubmit, isCreating }: CreateProjectModalProps) => {
    const [name, setName] = useState('');
    const [path, setPath] = useState('');
    const [useCustomPath, setUseCustomPath] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!name.trim()) {
            setError('Project name is required');
            return;
        }

        if (useCustomPath && !path.trim()) {
            setError('Path is required when using custom path');
            return;
        }

        try {
            await onSubmit(name.trim(), useCustomPath ? path.trim() : undefined);
            // Reset form on success
            setName('');
            setPath('');
            setUseCustomPath(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create project');
        }
    };

    const handleClose = () => {
        if (!isCreating) {
            setName('');
            setPath('');
            setUseCustomPath(false);
            setError(null);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">
                        <Plus size={24} />
                        Create New Project
                    </h2>
                    <button className="modal__close" onClick={handleClose} disabled={isCreating}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        <div className="form-group">
                            <label htmlFor="project-name">Project Name *</label>
                            <input
                                id="project-name"
                                type="text"
                                placeholder="my-cv-project"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                disabled={isCreating}
                                required
                                autoFocus
                            />
                            <small style={{ color: 'var(--color-text-secondary)' }}>
                                A unique name for your project
                            </small>
                        </div>

                        <div className="form-group">
                            <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                                <input
                                    type="checkbox"
                                    checked={useCustomPath}
                                    onChange={(e) => setUseCustomPath(e.target.checked)}
                                    disabled={isCreating}
                                />
                                Use custom path
                            </label>
                        </div>

                        {useCustomPath && (
                            <div className="form-group">
                                <label htmlFor="project-path">Project Path *</label>
                                <input
                                    id="project-path"
                                    type="text"
                                    placeholder="/path/to/project"
                                    value={path}
                                    onChange={(e) => setPath(e.target.value)}
                                    disabled={isCreating}
                                    required
                                />
                                <small style={{ color: 'var(--color-text-secondary)' }}>
                                    Absolute or relative path where project will be created
                                </small>
                            </div>
                        )}

                        {!useCustomPath && (
                            <div className="alert alert--info">
                                <AlertCircle size={20} />
                                <div>
                                    <strong>Default Location</strong>
                                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                                        Project will be created in current working directory: <code>./{name || 'project-name'}</code>
                                    </p>
                                </div>
                            </div>
                        )}

                        {error && (
                            <div className="alert alert--error">
                                <AlertCircle size={20} />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>

                    <div className="modal__footer">
                        <button
                            type="button"
                            className="btn btn--secondary"
                            onClick={handleClose}
                            disabled={isCreating}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn--primary"
                            disabled={isCreating || !name.trim()}
                        >
                            {isCreating ? (
                                <>
                                    <Plus size={18} className="spinner" />
                                    Creating...
                                </>
                            ) : (
                                <>
                                    <Plus size={18} />
                                    Create Project
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateProjectModal;