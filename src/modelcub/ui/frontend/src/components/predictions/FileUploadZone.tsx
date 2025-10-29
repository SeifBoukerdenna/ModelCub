// components/predictions/FileUploadZone.tsx
import React, { useRef, useEffect, useState } from 'react'
import { Upload, X, Image as ImageIcon, Folder } from 'lucide-react'
import type { Dataset } from '@/lib/api/types'

interface FileUploadZoneProps {
    inputType: 'image' | 'images' | 'dataset'
    inputPath: string
    datasets: Dataset[]
    selectedFiles: File[]
    previewUrls: string[]
    onFilesSelected: (files: File[]) => void
    onDatasetSelected: (name: string) => void
    onClear: () => void
    disabled?: boolean
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
    inputType,
    inputPath,
    datasets,
    selectedFiles,
    previewUrls,
    onFilesSelected,
    onDatasetSelected,
    onClear,
    disabled
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null)
    const folderInputRef = useRef<HTMLInputElement>(null)
    const dropZoneRef = useRef<HTMLDivElement>(null)
    const [isDragging, setIsDragging] = useState(false)

    useEffect(() => {
        const dropZone = dropZoneRef.current
        if (!dropZone || inputType === 'dataset') return

        const handleDragEnter = (e: DragEvent) => {
            e.preventDefault()
            e.stopPropagation()
            setIsDragging(true)
        }

        const handleDragLeave = (e: DragEvent) => {
            e.preventDefault()
            e.stopPropagation()
            if (e.target === dropZone) setIsDragging(false)
        }

        const handleDragOver = (e: DragEvent) => {
            e.preventDefault()
            e.stopPropagation()
        }

        const handleDrop = (e: DragEvent) => {
            e.preventDefault()
            e.stopPropagation()
            setIsDragging(false)
            const files = Array.from(e.dataTransfer?.files || [])
            if (files.length > 0) onFilesSelected(files)
        }

        dropZone.addEventListener('dragenter', handleDragEnter)
        dropZone.addEventListener('dragleave', handleDragLeave)
        dropZone.addEventListener('dragover', handleDragOver)
        dropZone.addEventListener('drop', handleDrop)

        return () => {
            dropZone.removeEventListener('dragenter', handleDragEnter)
            dropZone.removeEventListener('dragleave', handleDragLeave)
            dropZone.removeEventListener('dragover', handleDragOver)
            dropZone.removeEventListener('drop', handleDrop)
        }
    }, [inputType, onFilesSelected])

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        onFilesSelected(files)
    }

    const handleClick = () => {
        if (disabled) return
        if (inputType === 'image') fileInputRef.current?.click()
        else folderInputRef.current?.click()
    }

    const hasFiles = selectedFiles.length > 0

    if (inputType === 'dataset') {
        return (
            <div className="form-group">
                <label>Dataset Name</label>
                <select
                    value={inputPath}
                    onChange={(e) => onDatasetSelected(e.target.value)}
                    disabled={disabled}
                >
                    <option value="">Select dataset...</option>
                    {datasets.map((ds) => (
                        <option key={ds.name} value={ds.name}>
                            {ds.name}
                        </option>
                    ))}
                </select>
            </div>
        )
    }

    return (
        <div className="form-group">
            <label>Input</label>

            <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                disabled={disabled}
                style={{ display: 'none' }}
            />
            <input
                ref={folderInputRef}
                type="file"
                // @ts-ignore
                webkitdirectory="true"
                directory="true"
                multiple
                onChange={handleFileChange}
                disabled={disabled}
                style={{ display: 'none' }}
            />

            <div
                ref={dropZoneRef}
                className={`drop-zone ${isDragging ? 'dragging' : ''} ${hasFiles ? 'has-files' : ''}`}
                onClick={handleClick}
            >
                {hasFiles ? (
                    <div className="drop-zone-content">
                        <div className="file-info">
                            {inputType === 'image' ? <ImageIcon size={24} /> : <Folder size={24} />}
                            <span>{inputPath}</span>
                        </div>
                        {!disabled && (
                            <button
                                className="clear-files-btn"
                                onClick={(e) => {
                                    e.stopPropagation()
                                    onClear()
                                }}
                            >
                                <X size={16} />
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="drop-zone-content">
                        <Upload size={32} />
                        <p>
                            {inputType === 'image'
                                ? 'Click to select or drag & drop an image'
                                : 'Click to select or drag & drop a folder'}
                        </p>
                        <span className="drop-zone-hint">Supports JPG, PNG, BMP, GIF</span>
                    </div>
                )}
            </div>

            {previewUrls.length > 0 && (
                <div className="image-previews">
                    {previewUrls.map((url, idx) => (
                        <div key={idx} className="preview-item">
                            <img src={url} alt={`Preview ${idx + 1}`} />
                        </div>
                    ))}
                    {selectedFiles.length > 3 && (
                        <div className="preview-more">
                            +{selectedFiles.length - 3} more
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}