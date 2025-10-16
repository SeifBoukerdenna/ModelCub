import { useState, useEffect } from 'react';
import { Import, X, AlertCircle, CheckCircle, FolderOpen } from 'lucide-react';

interface ImportProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (path: string) => Promise<void>;
    isImporting: boolean;
}

interface ValidationResult {
    isValid: boolean;
    error?: string;
}

// Basic path validation for absolute/relative paths on macOS/Linux/Windows.
// Disallow quotes and reserved wildcard chars that break shells/FS.
const validateProjectPath = (raw: string): ValidationResult => {
    const path = raw.trim();

    if (!path) {
        return { isValid: false, error: 'Project path is required' };
    }

    // No illegal characters commonly problematic across platforms
    if (/[*"<>?|]/.test(path)) {
        return { isValid: false, error: 'Path cannot contain * " < > ? | characters' };
    }

    // Avoid trailing slash clutter (allowed, but we nudge)
    if (/[/\\]\s*$/.test(raw)) {
        return { isValid: false, error: 'Remove trailing slashes or spaces at the end of the path' };
    }

    // Very lenient absolute/relative heuristic (supports /, ./, ../, C:\, \\server\share)
    const looksLikePath =
        /^(\.|\.{2}|\/|[A-Za-z]:\\|\\\\)/.test(path) || path.includes('/') || path.includes('\\');

    if (!looksLikePath) {
        return { isValid: false, error: 'Provide an absolute or relative folder path' };
    }

    return { isValid: true };
};

const ImportProjectModal = ({ isOpen, onClose, onSubmit, isImporting }: ImportProjectModalProps) => {
    const [path, setPath] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [validationError, setValidationError] = useState<string | null>(null);
    const [touched, setTouched] = useState(false);

    useEffect(() => {
        if (!touched) return;
        const result = validateProjectPath(path);
        setValidationError(result.error || null);
    }, [path, touched]);

    const handlePathChange = (value: string) => {
        setPath(value);
        if (!touched) setTouched(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setTouched(true);

        const validation = validateProjectPath(path);
        if (!validation.isValid) {
            setValidationError(validation.error || 'Invalid path');
            return;
        }

        try {
            await onSubmit(path.trim());
            // Reset on success
            setPath('');
            setTouched(false);
            setValidationError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to import project');
        }
    };

    const handleClose = () => {
        if (isImporting) return; // prevent closing mid-import
        setPath('');
        setError(null);
        setValidationError(null);
        setTouched(false);
        onClose();
    };

    if (!isOpen) return null;

    const isValid = !validationError && path.trim().length > 0;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal import-project-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Import size={20} />
                        </div>
                        <h2 className="modal__title">Import Existing Project</h2>
                    </div>
                    <button
                        className="modal__close"
                        onClick={handleClose}
                        disabled={isImporting}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* Project Path */}
                        <div className="form-group">
                            <label htmlFor="project-path" className="form-label">
                                Project path <span style={{ color: 'var(--color-error)' }}>*</span>
                            </label>

                            <div className="form-input-wrapper">
                                <input
                                    id="project-path"
                                    type="text"
                                    className={`form-input ${validationError ? 'form-input--error' : ''} ${isValid && touched ? 'form-input--valid' : ''
                                        }`}
                                    placeholder="/path/to/modelcub-project"
                                    value={path}
                                    onChange={(e) => handlePathChange(e.target.value)}
                                    disabled={isImporting}
                                    required
                                />
                                {isValid && touched && (
                                    <div className="form-input-icon form-input-icon--success">
                                        <CheckCircle size={18} />
                                    </div>
                                )}
                            </div>

                            {validationError && touched ? (
                                <p className="form-error">
                                    <AlertCircle
                                        size={14}
                                        style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }}
                                    />
                                    {validationError}
                                </p>
                            ) : (
                                <p className="form-help">
                                    Absolute or relative folder path. The folder should contain your ModelCub project
                                    (e.g. <code>.modelcub/</code> and config).
                                </p>
                            )}
                        </div>

                        {/* Info box */}
                        <div className="info-box">
                            <div className="info-box__icon">
                                <FolderOpen size={20} />
                            </div>
                            <div className="info-box__content">
                                <div className="info-box__title">What happens on import?</div>
                                <div className="info-box__description">
                                    We validate the directory and register it in your workspace without copying files.
                                </div>
                                <code className="info-box__code">{path || '/path/to/modelcub-project'}</code>
                            </div>
                        </div>

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
                            disabled={isImporting}
                        >
                            Cancel
                        </button>
                        <button type="submit" className="btn btn--primary" disabled={isImporting || !isValid}>
                            {isImporting ? (
                                <>
                                    <Import size={18} className="spinner" />
                                    Importing...
                                </>
                            ) : (
                                <>
                                    <Import size={18} />
                                    Import Project
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ImportProjectModal;
