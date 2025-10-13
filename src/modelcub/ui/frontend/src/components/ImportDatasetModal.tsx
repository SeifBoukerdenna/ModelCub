import { useState } from 'react';
import { Upload, FolderOpen, X, AlertCircle, File as FileIcon } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from '@/lib/toast';

interface ImportDatasetModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const ImportDatasetModal = ({ isOpen, onClose, onSuccess }: ImportDatasetModalProps) => {
    const [importSource, setImportSource] = useState('');
    const [datasetName, setDatasetName] = useState('');
    const [recursive, setRecursive] = useState(true);
    const [copyFiles, setCopyFiles] = useState(true);
    const [importType, setImportType] = useState<'path' | 'files'>('path');
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (importType === 'path') {
            // Import from filesystem path
            if (!importSource.trim()) {
                toast.error('Please enter a source path');
                return;
            }

            try {
                setUploading(true);
                await api.importDataset({
                    source: importSource,
                    name: datasetName || undefined,
                    recursive,
                    copy_files: copyFiles,
                });
                handleSuccess();
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to import dataset');
            } finally {
                setUploading(false);
            }
        } else {
            // Upload files/folders
            if (!selectedFiles || selectedFiles.length === 0) {
                toast.error('Please select files or a folder');
                return;
            }

            try {
                setUploading(true);

                await api.importDatasetFiles(
                    selectedFiles,
                    datasetName || undefined,
                    recursive
                );

                handleSuccess();
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to upload files');
            } finally {
                setUploading(false);
                setUploadProgress(0);
            }
        }
    };

    const handleSuccess = () => {
        setImportSource('');
        setDatasetName('');
        setSelectedFiles(null);
        setUploadProgress(0);
        onSuccess();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(e.target.files);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">
                        <Upload size={24} />
                        Import Dataset
                    </h2>
                    <button className="modal__close" onClick={onClose} disabled={uploading}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* Import Type Selector */}
                        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                                <button
                                    type="button"
                                    className={`btn ${importType === 'path' ? 'btn--primary' : 'btn--secondary'}`}
                                    onClick={() => setImportType('path')}
                                    disabled={uploading}
                                >
                                    <FolderOpen size={18} />
                                    From Path
                                </button>
                                <button
                                    type="button"
                                    className={`btn ${importType === 'files' ? 'btn--primary' : 'btn--secondary'}`}
                                    onClick={() => setImportType('files')}
                                    disabled={uploading}
                                >
                                    <FileIcon size={18} />
                                    Upload Files/Folder
                                </button>
                            </div>
                        </div>

                        {/* Import from Path */}
                        {importType === 'path' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="source">Source Path *</label>
                                    <input
                                        id="source"
                                        type="text"
                                        placeholder="/path/to/images or https://..."
                                        value={importSource}
                                        onChange={(e) => setImportSource(e.target.value)}
                                        disabled={uploading}
                                        required
                                    />
                                    <small style={{ color: 'var(--color-text-secondary)' }}>
                                        Local directory path, Roboflow URL, or remote archive
                                    </small>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="name">Dataset Name (Optional)</label>
                                    <input
                                        id="name"
                                        type="text"
                                        placeholder="Leave empty to use source name"
                                        value={datasetName}
                                        onChange={(e) => setDatasetName(e.target.value)}
                                        disabled={uploading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                                        <input
                                            type="checkbox"
                                            checked={recursive}
                                            onChange={(e) => setRecursive(e.target.checked)}
                                            disabled={uploading}
                                        />
                                        Search subdirectories recursively
                                    </label>
                                </div>

                                <div className="form-group">
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                                        <input
                                            type="checkbox"
                                            checked={copyFiles}
                                            onChange={(e) => setCopyFiles(e.target.checked)}
                                            disabled={uploading}
                                        />
                                        Copy files to project (recommended)
                                    </label>
                                    <small style={{ color: 'var(--color-text-secondary)' }}>
                                        If unchecked, files will be symlinked instead
                                    </small>
                                </div>
                            </>
                        )}

                        {/* Upload Files/Folders */}
                        {importType === 'files' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="files">Select Files or Folder *</label>
                                    <input
                                        id="files"
                                        type="file"
                                        onChange={handleFileChange}
                                        disabled={uploading}
                                        multiple
                                        accept="image/*"  // Accept images
                                        required
                                    />
                                    <small style={{ color: 'var(--color-text-secondary)' }}>
                                        Select multiple images or use folder button below
                                    </small>
                                    <button
                                        type="button"
                                        className="btn btn--secondary btn--sm"
                                        style={{ marginTop: 'var(--spacing-xs)', width: '100%' }}
                                        onClick={() => {
                                            const input = document.createElement('input');
                                            input.type = 'file';
                                            input.multiple = true;
                                            // @ts-ignore
                                            input.webkitdirectory = true;
                                            input.onchange = (e: any) => {
                                                if (e.target.files) {
                                                    setSelectedFiles(e.target.files);
                                                }
                                            };
                                            input.click();
                                        }}
                                        disabled={uploading}
                                    >
                                        <FolderOpen size={16} />
                                        Or Select Folder
                                    </button>
                                    {selectedFiles && (
                                        <div style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                                            Selected: <strong>{selectedFiles.length} file(s)</strong>
                                        </div>
                                    )}
                                </div>
                                <div className="form-group">
                                    <label htmlFor="upload-name">Dataset Name (Optional)</label>
                                    <input
                                        id="upload-name"
                                        type="text"
                                        placeholder="Leave empty to use folder name"
                                        value={datasetName}
                                        onChange={(e) => setDatasetName(e.target.value)}
                                        disabled={uploading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                                        <input
                                            type="checkbox"
                                            checked={recursive}
                                            onChange={(e) => setRecursive(e.target.checked)}
                                            disabled={uploading}
                                        />
                                        Include subdirectories
                                    </label>
                                </div>

                                {uploading && uploadProgress > 0 && (
                                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                                        <div style={{
                                            width: '100%',
                                            height: '8px',
                                            backgroundColor: 'var(--color-gray-200)',
                                            borderRadius: 'var(--border-radius-sm)',
                                            overflow: 'hidden'
                                        }}>
                                            <div style={{
                                                width: `${uploadProgress}%`,
                                                height: '100%',
                                                backgroundColor: 'var(--color-primary-500)',
                                                transition: 'width 0.3s ease'
                                            }} />
                                        </div>
                                        <small style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                                            Uploading: {uploadProgress}%
                                        </small>
                                    </div>
                                )}
                            </>
                        )}

                        {error && (
                            <div className="alert alert--error">
                                <AlertCircle size={20} />
                                <span>{error}</span>
                            </div>
                        )}
                    </div>

                    <div className="modal__footer">
                        <button type="button" className="btn btn--secondary" onClick={onClose} disabled={uploading}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn--primary" disabled={uploading}>
                            {uploading ? (
                                <>
                                    <Upload size={18} className="spinner" />
                                    {importType === 'path' ? 'Importing...' : `Uploading... ${uploadProgress}%`}
                                </>
                            ) : (
                                <>
                                    <Upload size={18} />
                                    Import
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ImportDatasetModal;