// components/predictions/PredictionForm.tsx
import React from 'react'
import { Play } from 'lucide-react'
import { ModelSelector } from './ModelSelector'
import { InputTypeSelector } from './InputTypeSelector'
import { FileUploadZone } from './FileUploadZone'
import { AdvancedSettings } from './AdvancedSettings'
import type { PromotedModel, Dataset } from '@/lib/api/types'

interface PredictionFormProps {
    models: PromotedModel[]
    datasets: Dataset[]
    selectedModel: string
    inputType: 'image' | 'images' | 'dataset'
    inputPath: string
    selectedFiles: File[]
    previewUrls: string[]
    conf: number
    iou: number
    device: string
    batchSize: number
    classes: string
    saveTxt: boolean
    saveImg: boolean
    isProcessing: boolean
    uploading: boolean
    running: boolean
    onModelChange: (model: string) => void
    onInputTypeChange: (type: 'image' | 'images' | 'dataset') => void
    onFilesSelected: (files: File[]) => void
    onDatasetSelected: (name: string) => void
    onClearFiles: () => void
    onConfChange: (value: number) => void
    onIouChange: (value: number) => void
    onDeviceChange: (value: string) => void
    onBatchSizeChange: (value: number) => void
    onClassesChange: (value: string) => void
    onSaveTxtChange: (value: boolean) => void
    onSaveImgChange: (value: boolean) => void
    onRun: () => void
}

export const PredictionForm: React.FC<PredictionFormProps> = ({
    models,
    datasets,
    selectedModel,
    inputType,
    inputPath,
    selectedFiles,
    previewUrls,
    conf,
    iou,
    device,
    batchSize,
    classes,
    saveTxt,
    saveImg,
    isProcessing,
    uploading,
    running,
    onModelChange,
    onInputTypeChange,
    onFilesSelected,
    onDatasetSelected,
    onClearFiles,
    onConfChange,
    onIouChange,
    onDeviceChange,
    onBatchSizeChange,
    onClassesChange,
    onSaveTxtChange,
    onSaveImgChange,
    onRun
}) => {
    const hasFiles = selectedFiles.length > 0 || (inputType === 'dataset' && inputPath)

    return (
        <div className="predictions-form-card">
            <ModelSelector
                models={models}
                selectedModel={selectedModel}
                onChange={onModelChange}
                disabled={isProcessing}
            />

            <InputTypeSelector
                inputType={inputType}
                onChange={onInputTypeChange}
                disabled={isProcessing}
            />

            <FileUploadZone
                inputType={inputType}
                inputPath={inputPath}
                datasets={datasets}
                selectedFiles={selectedFiles}
                previewUrls={previewUrls}
                onFilesSelected={onFilesSelected}
                onDatasetSelected={onDatasetSelected}
                onClear={onClearFiles}
                disabled={isProcessing}
            />

            <AdvancedSettings
                conf={conf}
                iou={iou}
                device={device}
                batchSize={batchSize}
                classes={classes}
                saveTxt={saveTxt}
                saveImg={saveImg}
                onConfChange={onConfChange}
                onIouChange={onIouChange}
                onDeviceChange={onDeviceChange}
                onBatchSizeChange={onBatchSizeChange}
                onClassesChange={onClassesChange}
                onSaveTxtChange={onSaveTxtChange}
                onSaveImgChange={onSaveImgChange}
                disabled={isProcessing}
            />

            <button
                className="run-btn"
                onClick={onRun}
                disabled={isProcessing || !selectedModel || !hasFiles}
            >
                <Play size={16} />
                {uploading ? 'Uploading...' : running ? 'Running...' : 'Run Inference'}
            </button>
        </div>
    )
}