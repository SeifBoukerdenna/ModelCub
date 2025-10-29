// components/predictions/PredictionCard.tsx
import React from 'react'
import { Eye, Trash2 } from 'lucide-react'
import type { PredictionJob } from '@/lib/api/types'

interface PredictionCardProps {
    prediction: PredictionJob
    onView: () => void
    onDelete: () => void
}

export const PredictionCard: React.FC<PredictionCardProps> = ({
    prediction,
    onView,
    onDelete
}) => (
    <div className="prediction-card">
        <div className="prediction-header">
            <div className="prediction-id">{prediction.id}</div>
            <span className={`status-badge status-${prediction.status}`}>
                {prediction.status}
            </span>
        </div>
        <div className="prediction-info">
            <div>Model: {prediction.model_source}</div>
            <div>Input: {prediction.input_path}</div>
            {prediction.stats && (
                <div className="prediction-stats">
                    <span>{prediction.stats.total_images} images</span>
                    <span>{prediction.stats.total_detections} detections</span>
                    <span>{prediction.stats.avg_inference_time_ms.toFixed(1)}ms</span>
                </div>
            )}
        </div>
        <div className="prediction-actions">
            {prediction.status === 'completed' && (
                <button
                    className="view-btn"
                    onClick={onView}
                    title="View results"
                >
                    <Eye size={14} />
                </button>
            )}
            <button
                className="delete-btn"
                onClick={onDelete}
                title="Delete prediction"
            >
                <Trash2 size={14} />
            </button>
        </div>
    </div>
)