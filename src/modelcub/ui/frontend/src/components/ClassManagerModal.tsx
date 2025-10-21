import { useState } from 'react';
import { X, Plus, Edit2, Trash2, Check, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from '@/lib/toast';

interface ClassManagerModalProps {

    onClose: () => void;
    datasetId: string;
    initialClasses: string[];
    onUpdate: () => void;
}

const ClassManagerModal = ({
    onClose,
    datasetId,
    initialClasses,
    onUpdate
}: ClassManagerModalProps) => {
    const [classes, setClasses] = useState<string[]>(initialClasses);
    const [newClassName, setNewClassName] = useState('');
    const [editingIndex, setEditingIndex] = useState<number | null>(null);
    const [editValue, setEditValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleAddClass = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newClassName.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const updatedClasses = await api.addClassToDataset(datasetId, newClassName.trim());
            setClasses(updatedClasses);
            setNewClassName('');
            toast.success(`Class '${newClassName}' added`);
            onUpdate();
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to add class';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
            onClose()
        }
    };

    const handleRenameClass = async (oldName: string, newName: string) => {
        if (!newName.trim() || newName === oldName) {
            setEditingIndex(null);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const updatedClasses = await api.renameClassInDataset(datasetId, oldName, newName.trim());
            setClasses(updatedClasses);
            setEditingIndex(null);
            toast.success(`Class renamed: '${oldName}' → '${newName}'`);
            onUpdate();
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to rename class';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
            onClose()

        }
    };

    const handleRemoveClass = async (className: string) => {
        if (!confirm(`Remove class '${className}'?\n\nNote: Existing labels will not be deleted.`)) {
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const updatedClasses = await api.removeClassFromDataset(datasetId, className);
            setClasses(updatedClasses);
            toast.success(`Class '${className}' removed`);
            onUpdate();
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to remove class';
            setError(message);
            toast.error(message);
        } finally {
            setLoading(false);
            onClose()

        }
    };

    const startEditing = (index: number, currentValue: string) => {
        setEditingIndex(index);
        setEditValue(currentValue);
    };

    const cancelEditing = () => {
        setEditingIndex(null);
        setEditValue('');
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div
                className="modal"
                style={{ maxWidth: '600px' }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="modal__header">
                    <h2 className="modal__title">Manage Classes</h2>
                    <button
                        className="modal__close"
                        onClick={onClose}
                        disabled={loading}
                        aria-label="Close"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="modal__body">
                    {/* Error Alert */}
                    {error && (
                        <div className="alert alert--error" style={{ marginBottom: 'var(--spacing-md)' }}>
                            <AlertCircle size={20} />
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Add New Class */}
                    <form onSubmit={handleAddClass} style={{ marginBottom: 'var(--spacing-xl)' }}>
                        <label className="form-label">Add New Class</label>
                        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="Enter class name"
                                value={newClassName}
                                onChange={(e) => setNewClassName(e.target.value)}
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                className="btn btn--primary"
                                disabled={!newClassName.trim() || loading}
                            >
                                <Plus size={18} />
                                Add
                            </button>
                        </div>
                    </form>

                    {/* Classes List */}
                    <div>
                        <label className="form-label">
                            Current Classes ({classes.length})
                        </label>
                        {classes.length === 0 ? (
                            <p style={{
                                textAlign: 'center',
                                color: 'var(--color-text-secondary)',
                                padding: 'var(--spacing-xl)'
                            }}>
                                No classes defined yet
                            </p>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                                {classes.map((cls, index) => (
                                    <div
                                        key={`${cls}-${index}`}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 'var(--spacing-sm)',
                                            padding: 'var(--spacing-sm)',
                                            backgroundColor: 'var(--color-background)',
                                            border: '1px solid var(--color-border)',
                                            borderRadius: 'var(--border-radius-md)'
                                        }}
                                    >
                                        {/* Class ID Badge */}
                                        <span
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                width: '32px',
                                                height: '32px',
                                                backgroundColor: 'var(--color-primary-100)',
                                                color: 'var(--color-primary-700)',
                                                borderRadius: 'var(--border-radius-md)',
                                                fontSize: 'var(--font-size-sm)',
                                                fontWeight: 600,
                                                flexShrink: 0
                                            }}
                                        >
                                            {index}
                                        </span>

                                        {/* Class Name (editable) */}
                                        {editingIndex === index ? (
                                            <>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={editValue}
                                                    onChange={(e) => setEditValue(e.target.value)}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter') {
                                                            handleRenameClass(cls, editValue);
                                                        } else if (e.key === 'Escape') {
                                                            cancelEditing();
                                                        }
                                                    }}
                                                    autoFocus
                                                    disabled={loading}
                                                    style={{ flex: 1 }}
                                                />
                                                <button
                                                    className="btn btn--sm btn--primary"
                                                    onClick={() => handleRenameClass(cls, editValue)}
                                                    disabled={loading}
                                                >
                                                    <Check size={16} />
                                                </button>
                                                <button
                                                    className="btn btn--sm btn--secondary"
                                                    onClick={cancelEditing}
                                                    disabled={loading}
                                                >
                                                    <X size={16} />
                                                </button>
                                            </>
                                        ) : (
                                            <>
                                                <span
                                                    style={{
                                                        flex: 1,
                                                        fontFamily: 'var(--font-family-mono)',
                                                        fontSize: 'var(--font-size-sm)',
                                                        color: 'var(--color-text-primary)'
                                                    }}
                                                >
                                                    {cls}
                                                </span>
                                                <button
                                                    className="btn btn--sm btn--secondary"
                                                    onClick={() => startEditing(index, cls)}
                                                    disabled={loading}
                                                    title="Rename class"
                                                >
                                                    <Edit2 size={16} />
                                                </button>
                                                <button
                                                    className="btn btn--sm btn--danger"
                                                    onClick={() => handleRemoveClass(cls)}
                                                    disabled={loading}
                                                    title="Remove class"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Info Note */}
                    <div
                        className="info-box"
                        style={{
                            marginTop: 'var(--spacing-lg)',
                            padding: 'var(--spacing-md)',
                            backgroundColor: 'var(--color-warning-50)',
                            border: '1px solid var(--color-warning-200)',
                            borderRadius: 'var(--border-radius-md)',
                            fontSize: 'var(--font-size-sm)',
                            color: 'var(--color-text-secondary)'
                        }}
                    >
                        <AlertCircle size={16} style={{ color: 'var(--color-warning-600)' }} />
                        <span>
                            <strong>Note:</strong> Removing a class does not delete existing labels.
                            Renamed classes will update in dataset.yaml and manifest.json.
                        </span>
                    </div>
                </div>

                {/* Footer */}
                <div className="modal__footer">
                    <button
                        className="btn btn--secondary"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ClassManagerModal;