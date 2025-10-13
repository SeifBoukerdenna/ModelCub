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
    const [classes, setClasses] = useState('');
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

        const classes_to_send = classes.split(',').map(s => s.trim()).filter(s => s.length > 0)
        console.log(`The classe to send are ${classes_to_send}`)
        if (importType === 'path') {
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
                    classes: classes_to_send.length > 0 ? classes_to_send : undefined,

                });
                handleSuccess();
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to import dataset');
            } finally {
                setUploading(false);
            }
        } else {
            if (!selectedFiles || selectedFiles.length === 0) {
                toast.error('Please select files or a folder');
                return;
            }

            try {
                setUploading(true);
                await api.importDatasetFiles(
                    selectedFiles,
                    datasetName || undefined,
                    classes_to_send.length > 0 ? classes_to_send : undefined,
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

    const handleFolderSelect = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        // @ts-ignore - webkitdirectory is supported but not in types
        input.webkitdirectory = true;
        input.onchange = (e: any) => {
            if (e.target.files) {
                setSelectedFiles(e.target.files);
            }
        };
        input.click();
    };

    const handleClose = () => {
        if (!uploading) {
            setImportSource('');
            setDatasetName('');
            setSelectedFiles(null);
            setError(null);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal import-dataset-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Upload size={20} />
                        </div>
                        <h2 className="modal__title">Import Dataset</h2>
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
                        {/* Import Type Tabs */}
                        <div className="tab-group">
                            <button
                                type="button"
                                className={`tab-button ${importType === 'path' ? 'tab-button--active' : ''}`}
                                onClick={() => setImportType('path')}
                                disabled={uploading}
                            >
                                <FolderOpen size={18} />
                                From Path
                            </button>
                            <button
                                type="button"
                                className={`tab-button ${importType === 'files' ? 'tab-button--active' : ''}`}
                                onClick={() => setImportType('files')}
                                disabled={uploading}
                            >
                                <FileIcon size={18} />
                                Upload Files/Folder
                            </button>
                        </div>

                        {/* Import from Path */}
                        {importType === 'path' && (
                            <>
                                <div className="form-group">
                                    <label htmlFor="source" className="form-label">
                                        Source Path <span style={{ color: 'var(--color-error)' }}>*</span>
                                    </label>
                                    <input
                                        id="source"
                                        type="text"
                                        className="form-input"
                                        placeholder="/path/to/images or https://..."
                                        value={importSource}
                                        onChange={(e) => setImportSource(e.target.value)}
                                        disabled={uploading}
                                        required
                                        autoFocus
                                    />
                                    <p className="form-help">
                                        Local directory path, Roboflow URL, or remote archive
                                    </p>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="name" className="form-label">
                                        Dataset Name (Optional)
                                    </label>
                                    <input
                                        id="name"
                                        type="text"
                                        className="form-input"
                                        placeholder="Leave empty to use source name"
                                        value={datasetName}
                                        onChange={(e) => setDatasetName(e.target.value)}
                                        disabled={uploading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={recursive}
                                            onChange={(e) => setRecursive(e.target.checked)}
                                            disabled={uploading}
                                            className="checkbox-input"
                                        />
                                        <span>Search subdirectories recursively</span>
                                    </label>
                                </div>

                                <div className="form-group">
                                    <label className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={copyFiles}
                                            onChange={(e) => setCopyFiles(e.target.checked)}
                                            disabled={uploading}
                                            className="checkbox-input"
                                        />
                                        <span>Copy files to project (recommended)</span>
                                    </label>
                                    <p className="form-help" style={{ marginLeft: '26px' }}>
                                        If unchecked, files will be symlinked instead
                                    </p>
                                </div>
                            </>
                        )}

                        {/* Upload Files/Folders */}
                        {importType === 'files' && (
                            <>
                                <div className="form-group">
                                    <label className="form-label">
                                        Select Files or Folder <span style={{ color: 'var(--color-error)' }}>*</span>
                                    </label>

                                    {/* File Input (hidden) */}
                                    <input
                                        id="files"
                                        type="file"
                                        onChange={handleFileChange}
                                        disabled={uploading}
                                        multiple
                                        accept="image/*"
                                        style={{ display: 'none' }}
                                    />

                                    {/* File Selection UI */}
                                    <div className="file-upload-area">
                                        <label htmlFor="files" className="file-upload-button">
                                            <FileIcon size={20} />
                                            Choose Files
                                        </label>
                                        <button
                                            type="button"
                                            className="file-upload-button file-upload-button--secondary"
                                            onClick={handleFolderSelect}
                                            disabled={uploading}
                                        >
                                            <FolderOpen size={20} />
                                            Or Select Folder
                                        </button>
                                    </div>

                                    {selectedFiles && selectedFiles.length > 0 && (
                                        <div className="file-selection-info">
                                            <FileIcon size={16} />
                                            <span>
                                                <strong>{selectedFiles.length}</strong> file(s) selected
                                            </span>
                                        </div>
                                    )}

                                    <p className="form-help">
                                        Select multiple images or use folder button below
                                    </p>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="upload-name" className="form-label">
                                        Dataset Name (Optional)
                                    </label>
                                    <input
                                        id="upload-name"
                                        type="text"
                                        className="form-input"
                                        placeholder="Leave empty to use folder name"
                                        value={datasetName}
                                        onChange={(e) => setDatasetName(e.target.value)}
                                        disabled={uploading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="checkbox-label">
                                        <input
                                            type="checkbox"
                                            checked={recursive}
                                            onChange={(e) => setRecursive(e.target.checked)}
                                            disabled={uploading}
                                            className="checkbox-input"
                                        />
                                        <span>Include subdirectories</span>
                                    </label>
                                </div>

                                {/* Upload Progress */}
                                {uploading && uploadProgress > 0 && (
                                    <div className="upload-progress">
                                        <div className="upload-progress__bar">
                                            <div
                                                className="upload-progress__fill"
                                                style={{ width: `${uploadProgress}%` }}
                                            />
                                        </div>
                                        <p className="upload-progress__text">
                                            Uploading: {uploadProgress}%
                                        </p>
                                    </div>
                                )}
                            </>
                        )}

                        {/* Error Alert */}
                        {error && (
                            <div className="alert alert--error">
                                <AlertCircle size={20} />
                                <span>{error}</span>
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="name" className="form-label">
                                Classes (Optional)
                            </label>
                            <input
                                id="name"
                                type="text"
                                className="form-input"
                                placeholder="separate each class by a comma"
                                value={classes}
                                onChange={(e) => setClasses(e.target.value)}
                                disabled={uploading}
                            />
                        </div>
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
                            disabled={uploading}
                        >
                            {uploading ? (
                                <>
                                    <Upload size={18} className="spinner" />
                                    {importType === 'path' ? 'Importing...' : 'Uploading...'}
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