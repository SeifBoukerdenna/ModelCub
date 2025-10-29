// components/predictions/ResultsModal.tsx
import React, { useEffect, useState } from 'react'
import { X, Download, ExternalLink, ZoomIn } from 'lucide-react'
import { api } from '@/lib/api'

interface ResultsModalProps {
    predictionId: string
    onClose: () => void
}

export const ResultsModal: React.FC<ResultsModalProps> = ({ predictionId, onClose }) => {
    const [results, setResults] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [selectedImage, setSelectedImage] = useState<string | null>(null)
    const [imageUrls, setImageUrls] = useState<Record<string, string>>({})

    useEffect(() => {
        loadResults()
    }, [predictionId])

    useEffect(() => {
        if (results?.output_images) {
            loadImages(results.output_images)
        }
        return () => {
            Object.values(imageUrls).forEach(url => URL.revokeObjectURL(url))
        }
    }, [results])

    const loadResults = async () => {
        try {
            setLoading(true)
            setError(null)
            const data = await api.getPrediction(predictionId)
            setResults(data)

            if (!data.output_images || data.output_images.length === 0) {
                setError('No output images found. Make sure "Save Images" was enabled.')
            }
        } catch (error) {
            console.error('Failed to load results:', error)
            setError('Failed to load prediction results')
        } finally {
            setLoading(false)
        }
    }

    const loadImages = async (imageNames: string[]) => {
        const urls: Record<string, string> = {}
        for (const img of imageNames) {
            try {
                urls[img] = await api.getPredictionImage(predictionId, img)
            } catch (error) {
                console.error(`Failed to load image ${img}:`, error)
            }
        }
        setImageUrls(urls)
    }

    const downloadImage = (imageName: string) => {
        const url = imageUrls[imageName]
        if (!url) return

        const link = document.createElement('a')
        link.href = url
        link.download = imageName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const openInNewTab = (imageName: string) => {
        const url = imageUrls[imageName]
        if (url) window.open(url, '_blank')
    }

    return (
        <>
            <div className="modal-overlay" onClick={onClose}>
                <div className="modal-content results-modal" onClick={(e) => e.stopPropagation()}>
                    <div className="modal-header">
                        <div className="modal-header-info">
                            <h2>Prediction Results</h2>
                            <span className="modal-subtitle">{predictionId}</span>
                        </div>
                        <button className="close-btn" onClick={onClose}>
                            <X size={20} />
                        </button>
                    </div>

                    <div className="modal-body">
                        {loading ? (
                            <div className="results-loading">
                                <div className="spinner"></div>
                                <p>Loading results...</p>
                            </div>
                        ) : error ? (
                            <div className="results-error">
                                <p>{error}</p>
                            </div>
                        ) : results?.output_images?.length > 0 ? (
                            <>
                                <div className="results-summary">
                                    <div className="summary-stat">
                                        <span className="summary-label">Total Images:</span>
                                        <span className="summary-value">{results.output_images.length}</span>
                                    </div>
                                    {results.stats && (
                                        <>
                                            <div className="summary-stat">
                                                <span className="summary-label">Detections:</span>
                                                <span className="summary-value">{results.stats.total_detections}</span>
                                            </div>
                                            <div className="summary-stat">
                                                <span className="summary-label">Avg Time:</span>
                                                <span className="summary-value">
                                                    {results.stats.avg_inference_time_ms.toFixed(1)}ms
                                                </span>
                                            </div>
                                        </>
                                    )}
                                </div>

                                <div className="results-grid">
                                    {results.output_images.map((img: string, idx: number) => (
                                        <div key={idx} className="result-image-card">
                                            <div className="result-image-container">
                                                {imageUrls[img] ? (
                                                    <img
                                                        src={imageUrls[img]}
                                                        alt={img}
                                                        className="result-image"
                                                        onClick={() => setSelectedImage(img)}
                                                    />
                                                ) : (
                                                    <div className="result-image-loading">Loading...</div>
                                                )}
                                                <div className="result-image-overlay">
                                                    <button
                                                        className="overlay-btn"
                                                        onClick={() => setSelectedImage(img)}
                                                        title="View full size"
                                                    >
                                                        <ZoomIn size={18} />
                                                    </button>
                                                    <button
                                                        className="overlay-btn"
                                                        onClick={() => downloadImage(img)}
                                                        title="Download"
                                                    >
                                                        <Download size={18} />
                                                    </button>
                                                    <button
                                                        className="overlay-btn"
                                                        onClick={() => openInNewTab(img)}
                                                        title="Open in new tab"
                                                    >
                                                        <ExternalLink size={18} />
                                                    </button>
                                                </div>
                                            </div>
                                            <span className="result-image-name">{img}</span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="results-empty">
                                <p>No results to display</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {selectedImage && imageUrls[selectedImage] && (
                <div className="image-viewer-overlay" onClick={() => setSelectedImage(null)}>
                    <div className="image-viewer-content">
                        <button
                            className="image-viewer-close"
                            onClick={() => setSelectedImage(null)}
                        >
                            <X size={24} />
                        </button>
                        <img
                            src={imageUrls[selectedImage]}
                            alt={selectedImage}
                            className="image-viewer-img"
                        />
                        <div className="image-viewer-name">{selectedImage}</div>
                    </div>
                </div>
            )}
        </>
    )
}