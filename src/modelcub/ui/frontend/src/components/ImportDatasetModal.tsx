import React, { useState, useRef } from 'react'
import { X, Upload, FolderOpen, Loader, FileImage } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from '@/lib/toast'

interface ImportDatasetModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
}

const ImportDatasetModal: React.FC<ImportDatasetModalProps> = ({
    isOpen,
    onClose,
    onSuccess
}) => {
    const [name, setName] = useState('')
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
    const [folderName, setFolderName] = useState('')
    const [uploadMode, setUploadMode] = useState<'folder' | 'files'>('folder')
    const [recursive, setRecursive] = useState(true)
    const [importing, setImporting] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const fileInputRef = useRef<HTMLInputElement>(null)

    if (!isOpen) return null

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (!files || files.length === 0) return

        setSelectedFiles(files)

        if (uploadMode === 'folder') {
            const firstFile = files[0]
            if (firstFile && firstFile.webkitRelativePath) {
                const parts = firstFile.webkitRelativePath.split('/')
                const folder = parts[0]
                setFolderName(folder ?? '')

                if (!name) {
                    setName((folder ?? '').toLowerCase().replace(/[^a-z0-9-_]/g, '-'))
                }
            }
        } else {
            setFolderName(`${files.length} file${files.length !== 1 ? 's' : ''} selected`)

            if (!name) {
                setName(`upload-${Date.now()}`)
            }
        }
    }

    const handleBrowseClick = () => {
        fileInputRef.current?.click()
    }

    const handleModeChange = (mode: 'folder' | 'files') => {
        setUploadMode(mode)
        setSelectedFiles(null)
        setFolderName('')
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!selectedFiles || selectedFiles.length === 0) {
            toast.error('Please select files or a folder')
            return
        }

        try {
            setImporting(true)
            setUploadProgress(0)

            const response = await api.importDatasetFiles(
                selectedFiles,
                name.trim() || undefined,
                recursive,
                (progress) => setUploadProgress(progress)
            )

            if (response.success) {
                const datasetName = response.data?.dataset?.name || 'dataset'
                const imageCount = response.data?.dataset?.images || 0

                toast.success(
                    `✨ Imported ${imageCount} image${imageCount !== 1 ? 's' : ''} into "${datasetName}"`
                )

                setName('')
                setSelectedFiles(null)
                setFolderName('')
                setRecursive(true)
                setUploadProgress(0)

                onClose()
                onSuccess()
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to import dataset'
            toast.error(message)
        } finally {
            setImporting(false)
            setUploadProgress(0)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">Import Dataset</h2>
                    <button className="modal__close" onClick={onClose} disabled={importing}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* Upload Mode Selection */}
                        <div className="form-group">
                            <label className="form-label">Upload Mode</label>
                            <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-xs)',
                                    cursor: 'pointer',
                                    fontSize: 'var(--font-size-sm)'
                                }}>
                                    <input
                                        type="radio"
                                        checked={uploadMode === 'folder'}
                                        onChange={() => handleModeChange('folder')}
                                        disabled={importing}
                                        style={{ cursor: 'pointer' }}
                                    />
                                    <FolderOpen size={16} />
                                    <span>Folder</span>
                                </label>
                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-xs)',
                                    cursor: 'pointer',
                                    fontSize: 'var(--font-size-sm)'
                                }}>
                                    <input
                                        type="radio"
                                        checked={uploadMode === 'files'}
                                        onChange={() => handleModeChange('files')}
                                        disabled={importing}
                                        style={{ cursor: 'pointer' }}
                                    />
                                    <FileImage size={16} />
                                    <span>Individual Files</span>
                                </label>
                            </div>
                        </div>

                        {/* Hidden file input */}
                        <input
                            ref={fileInputRef}
                            type="file"
                            // @ts-ignore
                            webkitdirectory={uploadMode === 'folder' ? "true" : undefined}
                            directory={uploadMode === 'folder' ? "true" : undefined}
                            multiple
                            style={{ display: 'none' }}
                            onChange={handleFileSelect}
                            accept="image/*"
                        />

                        {/* File/Folder Selection */}
                        <div className="form-group">
                            <label className="form-label">
                                Select {uploadMode === 'folder' ? 'Folder' : 'Files'} <span style={{ color: 'var(--color-error-500)' }}>*</span>
                            </label>
                            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center' }}>
                                <button
                                    type="button"
                                    className="btn btn--secondary"
                                    onClick={handleBrowseClick}
                                    disabled={importing}
                                    style={{ flex: 1 }}
                                >
                                    {uploadMode === 'folder' ? <FolderOpen size={20} /> : <FileImage size={20} />}
                                    {folderName || `Choose ${uploadMode === 'folder' ? 'Folder' : 'Files'}`}
                                </button>
                                {selectedFiles && (
                                    <span style={{
                                        fontSize: 'var(--font-size-sm)',
                                        color: 'var(--color-text-secondary)',
                                        whiteSpace: 'nowrap'
                                    }}>
                                        {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
                                    </span>
                                )}
                            </div>
                            <p style={{
                                fontSize: 'var(--font-size-xs)',
                                color: 'var(--color-text-secondary)',
                                marginTop: 'var(--spacing-xs)'
                            }}>
                                {uploadMode === 'folder'
                                    ? 'Select a folder containing images (jpg, png, etc.)'
                                    : 'Select one or more image files to upload'
                                }
                            </p>
                        </div>

                        {/* Dataset Name */}
                        <div className="form-group">
                            <label htmlFor="dataset-name" className="form-label">
                                Dataset Name <span style={{
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--color-text-secondary)'
                                }}>(optional)</span>
                            </label>
                            <input
                                id="dataset-name"
                                type="text"
                                className="form-input"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Auto-generated if empty"
                                disabled={importing}
                            />
                        </div>

                        {/* Options - only show recursive for folder mode */}
                        {uploadMode === 'folder' && (
                            <div className="form-group">
                                <label className="form-label">Options</label>

                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-sm)',
                                    cursor: 'pointer',
                                    fontSize: 'var(--font-size-sm)'
                                }}>
                                    <input
                                        type="checkbox"
                                        checked={recursive}
                                        onChange={(e) => setRecursive(e.target.checked)}
                                        disabled={importing}
                                        style={{ cursor: 'pointer' }}
                                    />
                                    <span>Include subdirectories (recursive)</span>
                                </label>
                            </div>
                        )}

                        {/* Upload Progress */}
                        {importing && (
                            <div style={{
                                padding: 'var(--spacing-md)',
                                backgroundColor: 'var(--color-primary-50)',
                                borderRadius: 'var(--border-radius-md)',
                                fontSize: 'var(--font-size-sm)',
                            }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-sm)',
                                    marginBottom: 'var(--spacing-sm)',
                                    color: 'var(--color-primary-700)'
                                }}>
                                    <Loader size={16} className="spin" />
                                    <span>Uploading images...</span>
                                </div>

                                <div style={{
                                    width: '100%',
                                    height: '8px',
                                    backgroundColor: 'var(--color-primary-100)',
                                    borderRadius: '4px',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        width: `${uploadProgress}%`,
                                        height: '100%',
                                        backgroundColor: 'var(--color-primary-500)',
                                        transition: 'width 0.3s ease'
                                    }} />
                                </div>

                                <div style={{
                                    marginTop: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--color-primary-600)',
                                    textAlign: 'right'
                                }}>
                                    {uploadProgress}%
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="modal__footer">
                        <button
                            type="button"
                            className="btn btn--secondary"
                            onClick={onClose}
                            disabled={importing}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn--primary"
                            disabled={importing || !selectedFiles}
                        >
                            {importing ? (
                                <>
                                    <Loader size={20} className="spin" />
                                    Importing...
                                </>
                            ) : (
                                <>
                                    <Upload size={20} />
                                    Import Dataset
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default ImportDatasetModal