// components/predictions/PredictionCard.tsx
import React from 'react'
import { Eye, Trash2, Clock, Image, Layers } from 'lucide-react'
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
}) => {
    const formatTime = (isoString: string) => {
        const date = new Date(isoString)
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date)
    }

    return (
        <div className="prediction-card">
            <div className="prediction-card__header">
                <div className="prediction-card__title">
                    <span className="prediction-card__id">{prediction.id}</span>
                    <span className="prediction-card__time">
                        <Clock size={12} />
                        {formatTime(prediction.created)}
                    </span>
                </div>
                <span className={`prediction-card__status prediction-card__status--${prediction.status}`}>
                    {prediction.status}
                </span>
            </div>

            <div className="prediction-card__content">
                <div className="prediction-card__model">
                    <Layers size={14} />
                    <span>{prediction.model_source}</span>
                </div>

                <div className="prediction-card__input">
                    <span className="prediction-card__label">Input:</span>
                    <span className="prediction-card__value" title={prediction.input_path}>
                        {prediction.input_path.length > 40
                            ? '...' + prediction.input_path.slice(-37)
                            : prediction.input_path}
                    </span>
                </div>

                {prediction.stats && (
                    <div className="prediction-card__stats">
                        <div className="prediction-card__stat">
                            <Image size={14} />
                            <span>{prediction.stats.total_images}</span>
                        </div>
                        <div className="prediction-card__stat">
                            <span className="prediction-card__stat-label">detections:</span>
                            <span className="prediction-card__stat-value">
                                {prediction.stats.total_detections}
                            </span>
                        </div>
                        <div className="prediction-card__stat">
                            <span className="prediction-card__stat-label">avg:</span>
                            <span className="prediction-card__stat-value">
                                {prediction.stats.avg_inference_time_ms.toFixed(1)}ms
                            </span>
                        </div>
                    </div>
                )}
            </div>

            <div className="prediction-card__actions">
                {prediction.status === 'completed' && (
                    <button
                        className="prediction-card__btn prediction-card__btn--primary"
                        onClick={onView}
                        title="View results"
                    >
                        <Eye size={16} />
                        <span>View Results</span>
                    </button>
                )}
                <button
                    className="prediction-card__btn prediction-card__btn--danger"
                    onClick={onDelete}
                    title="Delete prediction"
                >
                    <Trash2 size={16} />
                </button>
            </div>
        </div>
    )
}