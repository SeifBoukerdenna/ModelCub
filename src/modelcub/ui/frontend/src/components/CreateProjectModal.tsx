import { useState, useEffect } from 'react';
import { Plus, X, AlertCircle, FolderOpen, CheckCircle } from 'lucide-react';

interface CreateProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string, path?: string) => Promise<void>;
    isCreating: boolean;
}

interface ValidationResult {
    isValid: boolean;
    error?: string;
}

const validateProjectName = (name: string): ValidationResult => {
    if (!name) {
        return { isValid: false, error: 'Project name is required' };
    }

    // Can't start with a number
    if (/^\d/.test(name)) {
        return { isValid: false, error: 'Project name cannot start with a number' };
    }

    // Check for spaces
    if (/\s/.test(name)) {
        return { isValid: false, error: 'Project name cannot contain spaces' };
    }

    // Check for quotes and special characters (allow only alphanumeric, hyphen, underscore)
    if (!/^[a-zA-Z][a-zA-Z0-9_-]*$/.test(name)) {
        return { isValid: false, error: 'Only letters, numbers, hyphens, and underscores allowed' };
    }

    return { isValid: true };
};

const CreateProjectModal = ({ isOpen, onClose, onSubmit, isCreating }: CreateProjectModalProps) => {
    const [name, setName] = useState('');
    const [path, setPath] = useState('');
    const [useCustomPath, setUseCustomPath] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [validationError, setValidationError] = useState<string | null>(null);
    const [touched, setTouched] = useState(false);

    // Real-time validation
    useEffect(() => {
        if (touched && name) {
            const result = validateProjectName(name);
            setValidationError(result.error || null);
        } else if (!name && touched) {
            setValidationError('Project name is required');
        } else {
            setValidationError(null);
        }
    }, [name, touched]);

    const handleNameChange = (value: string) => {
        setName(value);
        if (!touched) setTouched(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setTouched(true);

        const validation = validateProjectName(name);
        if (!validation.isValid) {
            setValidationError(validation.error || 'Invalid project name');
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
            setTouched(false);
            setValidationError(null);
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
            setValidationError(null);
            setTouched(false);
            onClose();
        }
    };

    if (!isOpen) return null;

    const isValid = !validationError && name.trim().length > 0;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal create-project-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Plus size={20} />
                        </div>
                        <h2 className="modal__title">Create New Project</h2>
                    </div>
                    <button
                        className="modal__close"
                        onClick={handleClose}
                        disabled={isCreating}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* Project Name */}
                        <div className="form-group">
                            <label htmlFor="project-name" className="form-label">
                                Project Name <span style={{ color: 'var(--color-error)' }}>*</span>
                            </label>
                            <div className="form-input-wrapper">
                                <input
                                    id="project-name"
                                    type="text"
                                    className={`form-input ${validationError ? 'form-input--error' : ''} ${isValid && touched ? 'form-input--valid' : ''}`}
                                    placeholder="my-cv-project"
                                    value={name}
                                    onChange={(e) => handleNameChange(e.target.value)}
                                    disabled={isCreating}
                                    required
                                    autoFocus
                                />
                                {isValid && touched && (
                                    <div className="form-input-icon form-input-icon--success">
                                        <CheckCircle size={18} />
                                    </div>
                                )}
                            </div>
                            {validationError && touched ? (
                                <p className="form-error">
                                    <AlertCircle size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                                    {validationError}
                                </p>
                            ) : (
                                <p className="form-help">
                                    Letters, numbers, hyphens, and underscores only. Cannot start with a number.
                                </p>
                            )}
                        </div>

                        {/* Custom Path Toggle */}
                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={useCustomPath}
                                    onChange={(e) => setUseCustomPath(e.target.checked)}
                                    disabled={isCreating}
                                    className="checkbox-input"
                                />
                                <span>Use custom path</span>
                            </label>
                        </div>

                        {/* Custom Path Input */}
                        {useCustomPath && (
                            <div className="form-group">
                                <label htmlFor="project-path" className="form-label">
                                    Project Path <span style={{ color: 'var(--color-error)' }}>*</span>
                                </label>
                                <input
                                    id="project-path"
                                    type="text"
                                    className="form-input"
                                    placeholder="/path/to/project"
                                    value={path}
                                    onChange={(e) => setPath(e.target.value)}
                                    disabled={isCreating}
                                    required
                                />
                                <p className="form-help">
                                    Absolute or relative path where project will be created
                                </p>
                            </div>
                        )}

                        {/* Default Location Info */}
                        {!useCustomPath && (
                            <div className="info-box">
                                <div className="info-box__icon">
                                    <FolderOpen size={20} />
                                </div>
                                <div className="info-box__content">
                                    <div className="info-box__title">Default Location</div>
                                    <div className="info-box__description">
                                        Project will be created in current working directory:
                                    </div>
                                    <code className="info-box__code">
                                        ./{name || 'project-name'}
                                    </code>
                                </div>
                            </div>
                        )}

                        {/* Error Alert */}
                        {error && (
                            <div className="alert alert--error">
                                <AlertCircle size={20} />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
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
                            disabled={isCreating || !isValid}
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