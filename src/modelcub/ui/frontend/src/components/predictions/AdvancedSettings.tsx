// components/predictions/AdvancedSettings.tsx
import React from 'react'
import { ChevronDown } from 'lucide-react'

interface AdvancedSettingsProps {
    conf: number
    iou: number
    device: string
    batchSize: number
    classes: string
    saveTxt: boolean
    saveImg: boolean
    onConfChange: (value: number) => void
    onIouChange: (value: number) => void
    onDeviceChange: (value: string) => void
    onBatchSizeChange: (value: number) => void
    onClassesChange: (value: string) => void
    onSaveTxtChange: (value: boolean) => void
    onSaveImgChange: (value: boolean) => void
    disabled?: boolean
}

export const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({
    conf,
    iou,
    device,
    batchSize,
    classes,
    saveTxt,
    saveImg,
    onConfChange,
    onIouChange,
    onDeviceChange,
    onBatchSizeChange,
    onClassesChange,
    onSaveTxtChange,
    onSaveImgChange,
    disabled
}) => (
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
                    onChange={(e) => onConfChange(parseFloat(e.target.value))}
                    disabled={disabled}
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
                    onChange={(e) => onIouChange(parseFloat(e.target.value))}
                    disabled={disabled}
                />
            </div>
            <div className="form-group">
                <label>Device</label>
                <select
                    value={device}
                    onChange={(e) => onDeviceChange(e.target.value)}
                    disabled={disabled}
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
                    onChange={(e) => onBatchSizeChange(parseInt(e.target.value))}
                    disabled={disabled}
                />
            </div>
            <div className="form-group">
                <label>Filter Classes</label>
                <input
                    type="text"
                    value={classes}
                    onChange={(e) => onClassesChange(e.target.value)}
                    placeholder="0,1,2 (comma-separated)"
                    disabled={disabled}
                />
            </div>
            <div className="form-group checkbox-group">
                <label>
                    <input
                        type="checkbox"
                        checked={saveTxt}
                        onChange={(e) => onSaveTxtChange(e.target.checked)}
                        disabled={disabled}
                    />
                    Save Labels
                </label>
                <label>
                    <input
                        type="checkbox"
                        checked={saveImg}
                        onChange={(e) => onSaveImgChange(e.target.checked)}
                        disabled={disabled}
                    />
                    Save Images
                </label>
            </div>
        </div>
    </details>
)