// components/predictions/ModelSelector.tsx
import React from 'react'
import type { PromotedModel } from '@/lib/api/types'

interface ModelSelectorProps {
    models: PromotedModel[]
    selectedModel: string
    onChange: (modelName: string) => void
    disabled?: boolean
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
    models,
    selectedModel,
    onChange,
    disabled
}) => (
    <div className="form-group">
        <select
            value={selectedModel}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
        >
            <option value="">Select model...</option>
            {models.map((m) => (
                <option key={m.name} value={m.name}>
                    {m.name} (v{m.version.slice(0, 8)})
                </option>
            ))}
        </select>
    </div>
)