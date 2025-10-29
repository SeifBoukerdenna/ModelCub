// components/predictions/InputTypeSelector.tsx
import React from 'react'
import { Image as ImageIcon, Folder, Database } from 'lucide-react'

interface InputTypeSelectorProps {
    inputType: 'image' | 'images' | 'dataset'
    onChange: (type: 'image' | 'images' | 'dataset') => void
    disabled?: boolean
}

export const InputTypeSelector: React.FC<InputTypeSelectorProps> = ({
    inputType,
    onChange,
    disabled
}) => (
    <div className="form-group">
        <label>Input Type</label>
        <div className="input-type-buttons">
            <button
                className={`input-type-btn ${inputType === 'image' ? 'active' : ''}`}
                onClick={() => onChange('image')}
                disabled={disabled}
            >
                <ImageIcon size={16} />
                Single Image
            </button>
            <button
                className={`input-type-btn ${inputType === 'images' ? 'active' : ''}`}
                onClick={() => onChange('images')}
                disabled={disabled}
            >
                <Folder size={16} />
                Directory
            </button>
            <button
                className={`input-type-btn ${inputType === 'dataset' ? 'active' : ''}`}
                onClick={() => onChange('dataset')}
                disabled={disabled}
            >
                <Database size={16} />
                Dataset
            </button>
        </div>
    </div>
)