// components/predictions/PredictionsList.tsx
import React from 'react'
import { PredictionCard } from './PredictionCard'
import type { PredictionJob } from '@/lib/api/types'

interface PredictionsListProps {
    predictions: PredictionJob[]
    onViewResults: (id: string) => void
    onDelete: (id: string) => void
}

export const PredictionsList: React.FC<PredictionsListProps> = ({
    predictions,
    onViewResults,
    onDelete
}) => (
    <div className="predictions-history">
        <h2>Recent Predictions</h2>
        {predictions.length === 0 ? (
            <p className="empty-state">No predictions yet</p>
        ) : (
            <div className="predictions-list">
                {predictions.map((pred) => (
                    <PredictionCard
                        key={pred.id}
                        prediction={pred}
                        onView={() => onViewResults(pred.id)}
                        onDelete={() => onDelete(pred.id)}
                    />
                ))}
            </div>
        )}
    </div>
)