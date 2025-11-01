import React, { useState } from 'react';
import { Brain, Calendar, TrendingUp, Tag, Trash2, Zap, Upload, Box } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PromotedModel } from '@/lib/api/types';
import ModelDetailsModal from './ModelDetailsModal';

interface ModelCardProps {
    model: PromotedModel;
    onClick?: () => void;
    onDelete: () => void;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, onClick, onDelete }) => {
    const navigate = useNavigate();
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const isImported = model.provenance === 'imported';

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const formatMetric = (value?: number) => {
        if (value === undefined || value === null) return 'N/A';
        return `${(value * 100).toFixed(1)}%`;
    };

    const handlePredict = (e: React.MouseEvent) => {
        e.stopPropagation();
        navigate('/predictions', { state: { modelName: model.name } });
    };

    const handleCardClick = () => {
        setShowDetailsModal(true);
    };

    const handleDelete = (e: React.MouseEvent) => {
        e.stopPropagation();
        onDelete();
    };

    return (
        <div
            className="card"
            style={{
                cursor: onClick ? 'pointer' : 'default',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                border: isImported ? '2px solid var(--color-primary-300)' : undefined,
            }}
            onClick={handleCardClick}
        >
            {/* Provenance Badge - Top Right Corner */}
            {isImported && (
                <div style={{
                    position: 'absolute',
                    top: 'var(--spacing-md)',
                    right: 'var(--spacing-md)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    backgroundColor: 'var(--color-primary-500)',
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: 'var(--border-radius-md)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    letterSpacing: '0.5px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                }}>
                    <Upload size={12} />
                    IMPORTED
                </div>
            )}

            <div className="card__body" style={{ flex: 1 }}>
                {/* Header */}
                <div style={{ marginBottom: 'var(--spacing-md)' }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: 'var(--spacing-sm)',
                        marginBottom: 'var(--spacing-xs)'
                    }}>
                        {isImported ? (
                            <Box
                                size={20}
                                style={{
                                    color: 'var(--color-primary-500)',
                                    flexShrink: 0,
                                    marginTop: '2px'
                                }}
                            />
                        ) : (
                            <Brain
                                size={20}
                                style={{
                                    color: 'var(--color-primary)',
                                    flexShrink: 0,
                                    marginTop: '2px'
                                }}
                            />
                        )}
                        <div style={{ flex: 1, paddingRight: isImported ? '90px' : '0' }}>
                            <h3 style={{
                                fontSize: 'var(--font-size-lg)',
                                fontWeight: 600,
                                marginBottom: '4px',
                                wordBreak: 'break-word'
                            }}>
                                {model.name}
                            </h3>
                            {model.description && (
                                <p style={{
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-text-secondary)',
                                    margin: 0
                                }}>
                                    {model.description}
                                </p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Performance Metrics - Only for models with metrics */}
                {model.metrics && (model.metrics.map50 || model.metrics.map50_95) && (
                    <div style={{
                        padding: 'var(--spacing-md)',
                        backgroundColor: 'var(--color-success-50)',
                        borderRadius: 'var(--border-radius-md)',
                        marginBottom: 'var(--spacing-md)'
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--spacing-xs)',
                            marginBottom: 'var(--spacing-sm)',
                            color: 'var(--color-success-700)',
                            fontSize: 'var(--font-size-xs)',
                            fontWeight: 600
                        }}>
                            <TrendingUp size={14} />
                            Performance
                        </div>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: '1fr 1fr',
                            gap: 'var(--spacing-md)'
                        }}>
                            {model.metrics.map50 !== undefined && (
                                <div>
                                    <div style={{
                                        fontSize: 'var(--font-size-xs)',
                                        color: 'var(--color-text-secondary)',
                                        marginBottom: '2px'
                                    }}>
                                        mAP50
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>
                                        {formatMetric(model.metrics.map50)}
                                    </div>
                                </div>
                            )}
                            {model.metrics.map50_95 !== undefined && (
                                <div>
                                    <div style={{
                                        fontSize: 'var(--font-size-xs)',
                                        color: 'var(--color-text-secondary)',
                                        marginBottom: '2px'
                                    }}>
                                        mAP50-95
                                    </div>
                                    <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>
                                        {formatMetric(model.metrics.map50_95)}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Info Section - Different for imported vs promoted */}
                <div style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--color-text-secondary)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--spacing-xs)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                        <Calendar size={14} />
                        <span>{formatDate(model.created)}</span>
                    </div>

                    {isImported ? (
                        <>
                            {/* Show import-specific info */}
                            {model.provenance && (
                                <div>
                                    <span style={{ fontWeight: 500 }}>Source:</span>{' '}
                                    <code style={{
                                        fontSize: 'var(--font-size-xs)',
                                        backgroundColor: 'var(--color-surface)',
                                        padding: '2px 6px',
                                        borderRadius: 'var(--border-radius-sm)'
                                    }}>
                                        {model.provenance}
                                    </code>
                                </div>
                            )}
                            {model.classes && model.classes.length > 0 && (
                                <div>
                                    <span style={{ fontWeight: 500 }}>Classes:</span>{' '}
                                    <span style={{ fontSize: 'var(--font-size-xs)' }}>
                                        {model.classes.length} classes
                                        {model.task && ` (${model.task})`}
                                    </span>
                                    <div style={{
                                        marginTop: 'var(--spacing-xs)',
                                        padding: 'var(--spacing-xs)',
                                        backgroundColor: 'var(--color-surface)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        fontSize: 'var(--font-size-xs)',
                                        maxHeight: '80px',
                                        overflowY: 'auto',
                                        color: 'var(--color-text-secondary)'
                                    }}>
                                        {model.classes.slice(0, 10).join(', ')}
                                        {model.classes.length > 10 && ` ... and ${model.classes.length - 10} more`}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <>
                            {/* Show training run info for promoted models */}
                            {model.run_id && (
                                <div>
                                    <span style={{ fontWeight: 500 }}>Run:</span>{' '}
                                    <code style={{
                                        fontSize: 'var(--font-size-xs)',
                                        backgroundColor: 'var(--color-surface)',
                                        padding: '2px 6px',
                                        borderRadius: 'var(--border-radius-sm)'
                                    }}>
                                        {model.run_id}
                                    </code>
                                </div>
                            )}
                            {model.dataset_name && (
                                <div>
                                    <span style={{ fontWeight: 500 }}>Dataset:</span> {model.dataset_name}
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Tags */}
                {model.tags && model.tags.length > 0 && (
                    <div style={{
                        display: 'flex',
                        gap: 'var(--spacing-xs)',
                        flexWrap: 'wrap',
                        marginTop: 'var(--spacing-md)'
                    }}>
                        {model.tags.map((tag, index) => (
                            <span
                                key={index}
                                style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '4px',
                                    fontSize: 'var(--font-size-xs)',
                                    backgroundColor: isImported
                                        ? 'var(--color-primary-100)'
                                        : 'var(--color-gray-100)',
                                    color: isImported
                                        ? 'var(--color-primary-700)'
                                        : 'var(--color-gray-700)',
                                    padding: '2px 8px',
                                    borderRadius: 'var(--border-radius-sm)',
                                }}
                            >
                                <Tag size={10} />
                                {tag}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Card Footer - Actions */}
            <div className="card__footer" style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: 'var(--spacing-sm)'
            }}>
                <button
                    className="btn btn--sm"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-xs)',
                        backgroundColor: 'var(--color-primary-50)',
                        color: 'var(--color-primary-600)',
                        border: '1px solid var(--color-primary-200)',
                        padding: '6px 12px',
                    }}
                    onClick={handlePredict}
                    title="Run inference with this model"
                >
                    <Zap size={14} />
                    Predict
                </button>
                <button
                    className="btn btn--text btn--sm"
                    style={{ color: 'var(--color-error)' }}
                    onClick={handleDelete}
                    title="Delete model"
                >
                    <Trash2 size={16} />
                </button>
            </div>

            {/* Model Details Modal */}
            <ModelDetailsModal
                model={model}
                isOpen={showDetailsModal}
                onClose={() => setShowDetailsModal(false)}
            />
        </div>
    );
};

export default ModelCard;