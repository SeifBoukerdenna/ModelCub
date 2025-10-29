// components/predictions/ResultsModal.tsx
import React, { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { api } from '@/lib/api'

interface ResultsModalProps {
    predictionId: string
    onClose: () => void
}

export const ResultsModal: React.FC<ResultsModalProps> = ({ predictionId, onClose }) => {
    const [results, setResults] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadResults()
    }, [predictionId])

    const loadResults = async () => {
        try {
            const data = await api.getPrediction(predictionId)
            setResults(data)
        } catch (error) {
            console.error('Failed to load results:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Prediction Results</h2>
                    <button className="close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>
                <div className="modal-body">
                    {loading ? (
                        <div>Loading results...</div>
                    ) : results ? (
                        <div className="results-grid">
                            {results.output_images?.slice(0, 6).map((img: string, idx: number) => (
                                <div key={idx} className="result-image">
                                    <img
                                        src={`/api/v1/predictions/${predictionId}/images/${img}`}
                                        alt={img}
                                    />
                                    <span className="image-name">{img}</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div>No results found</div>
                    )}
                </div>
            </div>
        </div>
    )
}