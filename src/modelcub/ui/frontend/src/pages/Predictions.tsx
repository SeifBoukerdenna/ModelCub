import React, { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { Play, Image as ImageIcon, Folder, Database, ChevronDown, Trash2, Upload, X } from 'lucide-react'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import type { PromotedModel, Dataset, PredictionJob } from '@/lib/api/types'
import { api } from '@/lib/api'

const Predictions: React.FC = () => {
    const location = useLocation()
    const project = useProjectStore(selectSelectedProject)
    const fileInputRef = useRef<HTMLInputElement>(null)
    const folderInputRef = useRef<HTMLInputElement>(null)
    const dropZoneRef = useRef<HTMLDivElement>(null)

    const [models, setModels] = useState<PromotedModel[]>([])
    const [datasets, setDatasets] = useState<Dataset[]>([])
    const [predictions, setPredictions] = useState<PredictionJob[]>([])
    const [loading, setLoading] = useState(false)
    const [running, setRunning] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [isDragging, setIsDragging] = useState(false)

    // Form state
    const [selectedModel, setSelectedModel] = useState('')
    const [inputType, setInputType] = useState<'image' | 'images' | 'dataset'>('image')
    const [inputPath, setInputPath] = useState('')
    const [selectedFiles, setSelectedFiles] = useState<File[]>([])
    const [uploadedPath, setUploadedPath] = useState<string>('')
    const [conf, setConf] = useState(0.25)
    const [iou, setIou] = useState(0.45)
    const [device, setDevice] = useState('cpu')
    const [batchSize, setBatchSize] = useState(16)
    const [saveImg, setSaveImg] = useState(false)
    const [saveTxt, setSaveTxt] = useState(true)
    const [classes, setClasses] = useState('')

    useEffect(() => {
        if (project) {
            loadData()
        }
    }, [project])

    useEffect(() => {
        const state = location.state as { modelName?: string } | null
        if (state?.modelName) {
            setSelectedModel(state.modelName)
        }
    }, [location.state])

    // Drag and drop handlers
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
            if (e.target === dropZone) {
                setIsDragging(false)
            }
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
            if (files.length > 0) {
                handleFilesSelected(files)
            }
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
    }, [inputType])

    const loadData = async () => {
        setLoading(true)
        try {
            const [modelsData, datasetsData, predictionsData] = await Promise.all([
                api.listModels(),
                api.listDatasets(),
                api.listPredictions()
            ])
            setModels(modelsData)
            setDatasets(datasetsData)
            setPredictions(predictionsData)
            if (modelsData.length > 0 && !selectedModel) {
                setSelectedModel(modelsData[0].name)
            }
        } catch (error) {
            console.error('Failed to load data:', error)
        } finally {
            setLoading(false)
        }
    }

    const uploadFiles = async (files: File[]): Promise<string> => {
        setUploading(true)
        try {
            const formData = new FormData()

            // Append all files with proper structure
            files.forEach((file) => {
                // For folders, preserve the relative path
                const path = (file as any).webkitRelativePath || file.name
                formData.append('files', file, path)
            })

            const headers: Record<string, string> = {}
            if (api.getProjectPath()) {
                headers['X-Project-Path'] = api.getProjectPath()!
            }

            const response = await fetch('/api/v1/predictions/upload', {
                method: 'POST',
                headers,
                body: formData
            })

            const data = await response.json()
            if (!response.ok || !data.success) {
                throw new Error(data.error?.message || 'Upload failed')
            }

            return data.data.path
        } finally {
            setUploading(false)
        }
    }

    const handleFilesSelected = (files: File[]) => {
        if (files.length === 0) return

        setSelectedFiles(files)
        setUploadedPath('')

        if (inputType === 'image') {
            setInputPath(`${files[0].name}`)
        } else {
            // For folder/multiple files
            const firstPath = (files[0] as any).webkitRelativePath || files[0].name
            const folderName = firstPath.includes('/')
                ? firstPath.split('/')[0]
                : 'selected-files'
            setInputPath(`${folderName} (${files.length} files)`)
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        handleFilesSelected(files)
    }

    const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        handleFilesSelected(files)
    }

    const handleInputTypeChange = (type: 'image' | 'images' | 'dataset') => {
        setInputType(type)
        setInputPath('')
        setSelectedFiles([])
        setUploadedPath('')

        // Clear file inputs
        if (fileInputRef.current) fileInputRef.current.value = ''
        if (folderInputRef.current) folderInputRef.current.value = ''
    }

    const clearFiles = () => {
        setSelectedFiles([])
        setInputPath('')
        setUploadedPath('')
        if (fileInputRef.current) fileInputRef.current.value = ''
        if (folderInputRef.current) folderInputRef.current.value = ''
    }

    const runInference = async () => {
        if (!selectedModel) {
            alert('Please select a model')
            return
        }

        let finalPath = inputPath

        // Upload files first if needed
        if ((inputType === 'image' || inputType === 'images') && selectedFiles.length > 0 && !uploadedPath) {
            try {
                finalPath = await uploadFiles(selectedFiles)
                setUploadedPath(finalPath)
                setInputPath(finalPath)
            } catch (error) {
                const message = error instanceof Error ? error.message : 'Upload failed'
                alert(`File upload failed: ${message}`)
                return
            }
        } else if (uploadedPath) {
            finalPath = uploadedPath
        } else if (inputType === 'dataset' && !inputPath) {
            alert('Please select a dataset')
            return
        } else if (!inputPath && !uploadedPath) {
            alert('Please provide input')
            return
        }

        setRunning(true)
        try {
            await api.createPrediction({
                model_name: selectedModel,
                input_type: inputType,
                input_path: finalPath,
                conf,
                iou,
                device,
                batch_size: batchSize,
                save_img: saveImg,
                save_txt: saveTxt,
                classes: classes || undefined
            })
            alert('Inference completed successfully!')
            loadData()
            // Reset
            clearFiles()
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unknown error'
            alert(`Inference failed: ${message}`)
        } finally {
            setRunning(false)
        }
    }

    const deletePrediction = async (id: string) => {
        if (!confirm('Delete this prediction?')) return
        try {
            await api.deletePrediction(id)
            loadData()
        } catch (error) {
            alert('Failed to delete prediction')
        }
    }

    if (loading) {
        return <div className="predictions-loading">Loading...</div>
    }

    const isProcessing = running || uploading
    const hasFiles = selectedFiles.length > 0 || uploadedPath || (inputType === 'dataset' && inputPath)

    return (
        <div className="predictions-page">
            <div className="predictions-header">
                <h1>Predictions</h1>
                <p>Run inference on images, directories, or datasets</p>
            </div>

            <div className="predictions-content">
                {/* Inference Form */}
                <div className="predictions-form-card">
                    <h2>New Prediction</h2>

                    {/* Model Selection */}
                    <div className="form-group">
                        <label>Model</label>
                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            disabled={isProcessing}
                        >
                            <option value="">Select model...</option>
                            {models.map((m) => (
                                <option key={m.name} value={m.name}>
                                    {m.name} (v{m.version.slice(0, 8)})
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Input Type */}
                    <div className="form-group">
                        <label>Input Type</label>
                        <div className="input-type-buttons">
                            <button
                                className={`input-type-btn ${inputType === 'image' ? 'active' : ''}`}
                                onClick={() => handleInputTypeChange('image')}
                                disabled={isProcessing}
                            >
                                <ImageIcon size={16} />
                                Single Image
                            </button>
                            <button
                                className={`input-type-btn ${inputType === 'images' ? 'active' : ''}`}
                                onClick={() => handleInputTypeChange('images')}
                                disabled={isProcessing}
                            >
                                <Folder size={16} />
                                Directory
                            </button>
                            <button
                                className={`input-type-btn ${inputType === 'dataset' ? 'active' : ''}`}
                                onClick={() => handleInputTypeChange('dataset')}
                                disabled={isProcessing}
                            >
                                <Database size={16} />
                                Dataset
                            </button>
                        </div>
                    </div>

                    {/* Input Selection with Drag & Drop */}
                    <div className="form-group">
                        <label>
                            {inputType === 'dataset' ? 'Dataset Name' : 'Input'}
                        </label>

                        {inputType === 'dataset' ? (
                            <select
                                value={inputPath}
                                onChange={(e) => setInputPath(e.target.value)}
                                disabled={isProcessing}
                            >
                                <option value="">Select dataset...</option>
                                {datasets.map((ds) => (
                                    <option key={ds.name} value={ds.name}>
                                        {ds.name}
                                    </option>
                                ))}
                            </select>
                        ) : (
                            <>
                                {/* Hidden file inputs */}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                    disabled={isProcessing}
                                    style={{ display: 'none' }}
                                />
                                <input
                                    ref={folderInputRef}
                                    type="file"
                                    // @ts-ignore
                                    webkitdirectory="true"
                                    directory="true"
                                    multiple
                                    onChange={handleFolderSelect}
                                    disabled={isProcessing}
                                    style={{ display: 'none' }}
                                />

                                {/* Drag & Drop Zone */}
                                <div
                                    ref={dropZoneRef}
                                    className={`drop-zone ${isDragging ? 'dragging' : ''} ${hasFiles ? 'has-files' : ''}`}
                                    onClick={() => {
                                        if (isProcessing) return
                                        if (inputType === 'image') {
                                            fileInputRef.current?.click()
                                        } else {
                                            folderInputRef.current?.click()
                                        }
                                    }}
                                >
                                    {hasFiles ? (
                                        <div className="drop-zone-content">
                                            <div className="file-info">
                                                {inputType === 'image' ? (
                                                    <ImageIcon size={24} />
                                                ) : (
                                                    <Folder size={24} />
                                                )}
                                                <span>{inputPath || uploadedPath}</span>
                                            </div>
                                            {!isProcessing && (
                                                <button
                                                    className="clear-files-btn"
                                                    onClick={(e) => {
                                                        e.stopPropagation()
                                                        clearFiles()
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
                                            <span className="drop-zone-hint">
                                                Supports JPG, PNG, BMP, GIF
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </>
                        )}
                    </div>

                    {/* Advanced Settings */}
                    <details className="advanced-settings">
                        <summary>
                            <ChevronDown size={16} />
                            Advanced Settings
                        </summary>
                        <div className="advanced-grid">
                            <div className="form-group">
                                <label>Confidence Threshold</label>
                                <input
                                    type="number"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    value={conf}
                                    onChange={(e) => setConf(parseFloat(e.target.value))}
                                    disabled={isProcessing}
                                />
                            </div>
                            <div className="form-group">
                                <label>IoU Threshold</label>
                                <input
                                    type="number"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    value={iou}
                                    onChange={(e) => setIou(parseFloat(e.target.value))}
                                    disabled={isProcessing}
                                />
                            </div>
                            <div className="form-group">
                                <label>Device</label>
                                <select
                                    value={device}
                                    onChange={(e) => setDevice(e.target.value)}
                                    disabled={isProcessing}
                                >
                                    <option value="cpu">CPU</option>
                                    <option value="cuda">CUDA</option>
                                    <option value="mps">MPS</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Batch Size</label>
                                <input
                                    type="number"
                                    min="1"
                                    max="128"
                                    value={batchSize}
                                    onChange={(e) => setBatchSize(parseInt(e.target.value))}
                                    disabled={isProcessing}
                                />
                            </div>
                            <div className="form-group">
                                <label>Filter Classes</label>
                                <input
                                    type="text"
                                    value={classes}
                                    onChange={(e) => setClasses(e.target.value)}
                                    placeholder="0,1,2 (comma-separated)"
                                    disabled={isProcessing}
                                />
                            </div>
                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={saveTxt}
                                        onChange={(e) => setSaveTxt(e.target.checked)}
                                        disabled={isProcessing}
                                    />
                                    Save Labels
                                </label>
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={saveImg}
                                        onChange={(e) => setSaveImg(e.target.checked)}
                                        disabled={isProcessing}
                                    />
                                    Save Images
                                </label>
                            </div>
                        </div>
                    </details>

                    <button
                        className="run-btn"
                        onClick={runInference}
                        disabled={isProcessing || !selectedModel || !hasFiles}
                    >
                        <Play size={16} />
                        {uploading ? 'Uploading...' : running ? 'Running...' : 'Run Inference'}
                    </button>
                </div>

                {/* Recent Predictions */}
                <div className="predictions-history">
                    <h2>Recent Predictions</h2>
                    {predictions.length === 0 ? (
                        <p className="empty-state">No predictions yet</p>
                    ) : (
                        <div className="predictions-list">
                            {predictions.map((pred) => (
                                <div key={pred.id} className="prediction-card">
                                    <div className="prediction-header">
                                        <div className="prediction-id">{pred.id}</div>
                                        <span className={`status-badge status-${pred.status}`}>
                                            {pred.status}
                                        </span>
                                    </div>
                                    <div className="prediction-info">
                                        <div>Model: {pred.model_source}</div>
                                        <div>Input: {pred.input_path}</div>
                                        {pred.stats && (
                                            <div className="prediction-stats">
                                                <span>{pred.stats.total_images} images</span>
                                                <span>{pred.stats.total_detections} detections</span>
                                                <span>{pred.stats.avg_inference_time_ms.toFixed(1)}ms</span>
                                            </div>
                                        )}
                                    </div>
                                    <button
                                        className="delete-btn"
                                        onClick={() => deletePrediction(pred.id)}
                                        title="Delete prediction"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Predictions