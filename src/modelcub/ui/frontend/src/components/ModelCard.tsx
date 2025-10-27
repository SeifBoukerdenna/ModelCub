import React from 'react';
import { Brain, Calendar, TrendingUp, Tag, Trash2 } from 'lucide-react';
import { PromotedModel } from '@/lib/api/types';


interface ModelCardProps {
    model: PromotedModel;
    onClick?: () => void;
    onDelete: () => void;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, onClick, onDelete }) => {
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

    return (
        <div
            className="card"
            style={{
                cursor: onClick ? 'pointer' : 'default',
                transition: 'all 150ms ease',
            }}
            onClick={onClick}
            onMouseEnter={(e) => {
                if (onClick) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                }
            }}
            onMouseLeave={(e) => {
                if (onClick) {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '';
                }
            }}
        >
            {/* Header */}
            <div className="card__header" style={{ paddingBottom: 'var(--spacing-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <Brain size={20} style={{ color: 'var(--color-primary-500)' }} />
                        <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, margin: 0 }}>
                            {model.name}
                        </h3>
                    </div>
                    <span
                        style={{
                            fontSize: 'var(--font-size-xs)',
                            backgroundColor: 'var(--color-surface)',
                            padding: '2px 8px',
                            borderRadius: 'var(--border-radius-sm)',
                            color: 'var(--color-text-secondary)'
                        }}
                    >
                        v{model.version.slice(0, 8)}
                    </span>
                </div>
            </div>

            {/* Body */}
            <div className="card__body">
                {/* Description */}
                {model.description && (
                    <p style={{
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)',
                        marginBottom: 'var(--spacing-md)',
                        lineHeight: 1.5
                    }}>
                        {model.description}
                    </p>
                )}

                {/* Metrics */}
                {model.metrics && Object.keys(model.metrics).length > 0 && (
                    <div style={{
                        backgroundColor: 'var(--color-surface)',
                        padding: 'var(--spacing-md)',
                        borderRadius: 'var(--border-radius-md)',
                        marginBottom: 'var(--spacing-md)'
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--spacing-xs)',
                            marginBottom: 'var(--spacing-sm)'
                        }}>
                            <TrendingUp size={16} style={{ color: 'var(--color-success-500)' }} />
                            <span style={{
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 600,
                                color: 'var(--color-text-primary)'
                            }}>
                                Performance
                            </span>
                        </div>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: '1fr 1fr',
                            gap: 'var(--spacing-sm)'
                        }}>
                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                    mAP50
                                </div>
                                <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>
                                    {formatMetric(model.metrics.map50)}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                                    mAP50-95
                                </div>
                                <div style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>
                                    {formatMetric(model.metrics.map50_95)}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Info */}
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
                    <div>
                        <span style={{ fontWeight: 500 }}>Run:</span>{' '}
                        <code style={{
                            fontSize: 'var(--font-size-xs)',
                            backgroundColor: 'var(--color-surface)',
                            padding: '2px 4px',
                            borderRadius: 'var(--border-radius-sm)'
                        }}>
                            {model.run_id}
                        </code>
                    </div>
                    {model.dataset_name && (
                        <div>
                            <span style={{ fontWeight: 500 }}>Dataset:</span> {model.dataset_name}
                        </div>
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
                                    backgroundColor: 'var(--color-primary-100)',
                                    color: 'var(--color-primary-700)',
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

            {/* Card Footer - Delete Button */}
            <div className="card__footer" style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                    className="btn btn--text btn--sm"
                    style={{ color: 'var(--color-error)' }}
                    onClick={onDelete}
                >
                    <Trash2 size={16} />
                </button>
            </div>
        </div>
    );
};

export default ModelCard;