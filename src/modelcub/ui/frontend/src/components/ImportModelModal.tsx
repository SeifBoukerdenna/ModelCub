/**
 * FILE LOCATION: src/modelcub/ui/frontend/src/components/ImportModelModal.tsx
 *
 * Import Model Modal Component
 * Matches existing UI patterns (similar to ImportDatasetModal)
 */

import { useState } from 'react';
import { Upload, X, AlertCircle, Package, FileCheck } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from '@/lib/toast';

interface ImportModelModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const ImportModelModal = ({ isOpen, onClose, onSuccess }: ImportModelModalProps) => {
    const [modelName, setModelName] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [validate, setValidate] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (!file.name.endsWith('.pt')) {
                setError('Please select a .pt (PyTorch) model file');
                return;
            }
            setSelectedFile(file);
            setError(null);

            // Auto-fill name if empty
            if (!modelName) {
                const name = file.name.replace('.pt', '').replace(/[^a-zA-Z0-9-_]/g, '-');
                setModelName(name);
            }
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!selectedFile) {
            toast.error('Please select a model file');
            return;
        }

        if (!modelName.trim()) {
            toast.error('Please enter a model name');
            return;
        }

        try {
            setUploading(true);
            setUploadProgress(0);

            // Simulate progress for better UX
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => Math.min(prev + 10, 90));
            }, 200);

            await api.importModel(selectedFile, modelName.trim(), {
                description: description.trim() || undefined,
                tags: tags.trim() || undefined,
                validate
            });

            clearInterval(progressInterval);
            setUploadProgress(100);

            toast.success(`Model "${modelName}" imported successfully`);
            handleSuccess();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to import model');
        } finally {
            setUploading(false);
            setUploadProgress(0);
        }
    };

    const handleSuccess = () => {
        setModelName('');
        setDescription('');
        setTags('');
        setSelectedFile(null);
        setUploadProgress(0);
        onSuccess();
    };

    const handleClose = () => {
        if (!uploading) {
            setModelName('');
            setDescription('');
            setTags('');
            setSelectedFile(null);
            setError(null);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal import-model-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Package size={20} />
                        </div>
                        <div>
                            <h2 className="modal__title">Import Model</h2>
                            <p className="modal__subtitle">Import a pre-trained YOLO model (.pt file)</p>
                        </div>
                    </div>
                    <button
                        className="modal__close"
                        onClick={handleClose}
                        disabled={uploading}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* File Upload Section */}
                        <div className="form-group">
                            <label className="form-label">
                                Model File (.pt)
                                <span style={{ color: 'var(--color-error)', marginLeft: 'var(--spacing-xs)' }}>*</span>
                            </label>

                            <div className="file-upload-area">
                                <input
                                    type="file"
                                    id="model-file-input"
                                    accept=".pt"
                                    onChange={handleFileChange}
                                    disabled={uploading}
                                    style={{ display: 'none' }}
                                />

                                {!selectedFile ? (
                                    <label htmlFor="model-file-input" className="file-upload-button file-upload-button--primary">
                                        <Upload size={18} />
                                        Choose Model File
                                    </label>
                                ) : (
                                    <div className="file-selection-info">
                                        <FileCheck size={18} style={{ color: 'var(--color-success)' }} />
                                        <span>{selectedFile.name}</span>
                                        <span style={{
                                            marginLeft: 'auto',
                                            fontSize: 'var(--font-size-sm)',
                                            color: 'var(--color-text-secondary)'
                                        }}>
                                            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                        </span>
                                        {!uploading && (
                                            <button
                                                type="button"
                                                onClick={() => setSelectedFile(null)}
                                                style={{
                                                    background: 'none',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    padding: 'var(--spacing-xs)',
                                                    color: 'var(--color-text-secondary)'
                                                }}
                                            >
                                                <X size={16} />
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                            <p className="form-help">
                                Upload a YOLO model file (.pt format)
                            </p>
                        </div>

                        {/* Upload Progress */}
                        {uploading && (
                            <div className="upload-progress">
                                <div className="upload-progress__bar">
                                    <div
                                        className="upload-progress__fill"
                                        style={{ width: `${uploadProgress}%` }}
                                    />
                                </div>
                                <p className="upload-progress__text">
                                    {uploadProgress < 100 ? `Uploading: ${uploadProgress}%` : 'Processing...'}
                                </p>
                            </div>
                        )}

                        {/* Model Name */}
                        <div className="form-group">
                            <label htmlFor="model-name" className="form-label">
                                Model Name
                                <span style={{ color: 'var(--color-error)', marginLeft: 'var(--spacing-xs)' }}>*</span>
                            </label>
                            <input
                                id="model-name"
                                type="text"
                                className="form-input"
                                placeholder="e.g., imported-detector-v1"
                                value={modelName}
                                onChange={(e) => setModelName(e.target.value)}
                                disabled={uploading}
                                required
                            />
                            <p className="form-help">
                                Unique name for this model
                            </p>
                        </div>

                        {/* Description */}
                        <div className="form-group">
                            <label htmlFor="description" className="form-label">
                                Description (Optional)
                            </label>
                            <textarea
                                id="description"
                                className="form-input"
                                placeholder="e.g., Pre-trained model from external source..."
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                disabled={uploading}
                                rows={3}
                                style={{ resize: 'vertical' }}
                            />
                        </div>

                        {/* Tags */}
                        <div className="form-group">
                            <label htmlFor="tags" className="form-label">
                                Tags (Optional)
                            </label>
                            <input
                                id="tags"
                                type="text"
                                className="form-input"
                                placeholder="e.g., production, imported, yolov8"
                                value={tags}
                                onChange={(e) => setTags(e.target.value)}
                                disabled={uploading}
                            />
                            <p className="form-help">
                                Comma-separated tags for organization
                            </p>
                        </div>

                        {/* Validate Checkbox */}
                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={validate}
                                    onChange={(e) => setValidate(e.target.checked)}
                                    disabled={uploading}
                                />
                                <span>Validate model after import</span>
                            </label>
                            <p className="form-help" style={{ marginTop: 'var(--spacing-xs)' }}>
                                Validates model compatibility and extracts metadata (recommended)
                            </p>
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
                            disabled={uploading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn--primary"
                            disabled={uploading || !selectedFile}
                        >
                            {uploading ? (
                                <>
                                    <Upload size={18} className="spinner" />
                                    Importing...
                                </>
                            ) : (
                                <>
                                    <Upload size={18} />
                                    Import Model
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ImportModelModal;