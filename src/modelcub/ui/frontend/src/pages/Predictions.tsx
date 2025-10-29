import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Play } from 'lucide-react'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import type { PromotedModel, Dataset, PredictionJob } from '@/lib/api/types'
import { api } from '@/lib/api'
import { ModelSelector } from '@/components/predictions/ModelSelector'
import { InputTypeSelector } from '@/components/predictions/InputTypeSelector'
import { FileUploadZone } from '@/components/predictions/FileUploadZone'
import { AdvancedSettings } from '@/components/predictions/AdvancedSettings'
import { PredictionsList } from '@/components/predictions/PredictionsList'
import { ResultsModal } from '@/components/predictions/ResultsModal'


// ==================== MAIN COMPONENT ====================

const Predictions: React.FC = () => {
    const location = useLocation()
    const project = useProjectStore(selectSelectedProject)

    const [models, setModels] = useState<PromotedModel[]>([])
    const [datasets, setDatasets] = useState<Dataset[]>([])
    const [predictions, setPredictions] = useState<PredictionJob[]>([])
    const [loading, setLoading] = useState(false)
    const [running, setRunning] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [selectedPrediction, setSelectedPrediction] = useState<string | null>(null)

    const [selectedModel, setSelectedModel] = useState('')
    const [inputType, setInputType] = useState<'image' | 'images' | 'dataset'>('image')
    const [inputPath, setInputPath] = useState('')
    const [selectedFiles, setSelectedFiles] = useState<File[]>([])
    const [previewUrls, setPreviewUrls] = useState<string[]>([])
    const [uploadedPath, setUploadedPath] = useState<string>('')
    const [conf, setConf] = useState(0.25)
    const [iou, setIou] = useState(0.45)
    const [device, setDevice] = useState('cpu')
    const [batchSize, setBatchSize] = useState(16)
    const [saveImg, setSaveImg] = useState(false)
    const [saveTxt, setSaveTxt] = useState(true)
    const [classes, setClasses] = useState('')

    useEffect(() => { if (project) loadData() }, [project])
    useEffect(() => { const state = location.state as { modelName?: string } | null; if (state?.modelName) setSelectedModel(state.modelName) }, [location.state])

    useEffect(() => {
        let cleanup: (() => void) | undefined
        if (selectedFiles.length > 0) {
            const urls = selectedFiles.filter(f => f.type.startsWith('image/')).slice(0, 3).map(file => URL.createObjectURL(file))
            setPreviewUrls(urls)
            cleanup = () => urls.forEach(url => URL.revokeObjectURL(url))
        } else {
            setPreviewUrls([])
        }
        return cleanup
    }, [selectedFiles])

    const loadData = async () => {
        setLoading(true)
        try {
            const [modelsData, datasetsData, predictionsData] = await Promise.all([api.listModels(), api.listDatasets(), api.listPredictions()])
            setModels(modelsData)
            setDatasets(datasetsData)
            setPredictions(predictionsData)
            if (modelsData.length > 0 && !selectedModel && modelsData[0]) setSelectedModel(modelsData[0].name)
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
            files.forEach((file) => formData.append('files', file, (file as any).webkitRelativePath || file.name))
            const headers: Record<string, string> = {}
            if (api.getProjectPath()) headers['X-Project-Path'] = api.getProjectPath()!
            const response = await fetch('/api/v1/predictions/upload', { method: 'POST', headers, body: formData })
            const data = await response.json()
            if (!response.ok || !data.success) throw new Error(data.error?.message || 'Upload failed')
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
            const firstPath = (files[0] as any).webkitRelativePath || files[0].name
            const folderName = firstPath.includes('/') ? firstPath.split('/')[0] : 'selected-files'
            setInputPath(`${folderName} (${files.length} files)`)
        }
    }

    const handleInputTypeChange = (type: 'image' | 'images' | 'dataset') => {
        setInputType(type)
        setInputPath('')
        setSelectedFiles([])
        setUploadedPath('')
    }

    const runInference = async () => {
        if (!selectedModel) { alert('Please select a model'); return }

        let finalPath = inputPath
        if ((inputType === 'image' || inputType === 'images') && selectedFiles.length > 0 && !uploadedPath) {
            try {
                finalPath = await uploadFiles(selectedFiles)
                setUploadedPath(finalPath)
                setInputPath(finalPath)
            } catch (error) {
                alert(`File upload failed: ${error instanceof Error ? error.message : 'Upload failed'}`)
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
                model_name: selectedModel, input_type: inputType, input_path: finalPath,
                conf, iou, device, batch_size: batchSize, save_img: saveImg, save_txt: saveTxt,
                classes: classes || undefined
            })
            alert('Inference completed successfully!')
            loadData()
            setSelectedFiles([])
            setInputPath('')
            setUploadedPath('')
        } catch (error) {
            alert(`Inference failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
        } finally {
            setRunning(false)
        }
    }

    const handleDeletePrediction = async (id: string) => {
        if (!confirm('Delete this prediction?')) return
        try {
            await api.deletePrediction(id)
            loadData()
        } catch (error) {
            alert('Failed to delete prediction')
        }
    }

    if (loading) return <div className="predictions-loading">Loading...</div>

    const isProcessing = running || uploading
    const hasFiles = selectedFiles.length > 0 || uploadedPath || (inputType === 'dataset' && inputPath)

    return (
        <div className="predictions-page">
            <div className="predictions-header"><h1>Predictions</h1></div>
            <div className="predictions-content">
                <div className="predictions-form-card">
                    <ModelSelector models={models} selectedModel={selectedModel} onChange={setSelectedModel} disabled={isProcessing} />
                    <InputTypeSelector inputType={inputType} onChange={handleInputTypeChange} disabled={isProcessing} />
                    <FileUploadZone
                        inputType={inputType} inputPath={inputPath} datasets={datasets} selectedFiles={selectedFiles} previewUrls={previewUrls}
                        onFilesSelected={handleFilesSelected} onDatasetSelected={setInputPath}
                        onClear={() => { setSelectedFiles([]); setInputPath(''); setUploadedPath('') }}
                        disabled={isProcessing}
                    />
                    <AdvancedSettings
                        conf={conf} iou={iou} device={device} batchSize={batchSize} classes={classes} saveTxt={saveTxt} saveImg={saveImg}
                        onConfChange={setConf} onIouChange={setIou} onDeviceChange={setDevice} onBatchSizeChange={setBatchSize}
                        onClassesChange={setClasses} onSaveTxtChange={setSaveTxt} onSaveImgChange={setSaveImg} disabled={isProcessing}
                    />
                    <button className="run-btn" onClick={runInference} disabled={isProcessing || !selectedModel || !hasFiles}>
                        <Play size={16} />
                        {uploading ? 'Uploading...' : running ? 'Running...' : 'Run Inference'}
                    </button>
                </div>
                <PredictionsList predictions={predictions} onViewResults={setSelectedPrediction} onDelete={handleDeletePrediction} />
            </div>
            {selectedPrediction && <ResultsModal predictionId={selectedPrediction} onClose={() => setSelectedPrediction(null)} />}
        </div>
    )
}

export default Predictions