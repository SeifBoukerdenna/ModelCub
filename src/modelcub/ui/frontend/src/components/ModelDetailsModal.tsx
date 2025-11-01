import React from 'react';
import { X, Brain, Box, Calendar, TrendingUp, Tag, Package, Upload, Zap, Database } from 'lucide-react';
import { PromotedModel } from '@/lib/api/types';

interface ModelDetailsModalProps {
    model: PromotedModel;
    isOpen: boolean;
    onClose: () => void;
}

const ModelDetailsModal: React.FC<ModelDetailsModalProps> = ({ model, isOpen, onClose }) => {
    const isImported = model.provenance === 'imported';

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatMetric = (value?: number) => {
        if (value === undefined || value === null) return 'N/A';
        return `${(value * 100).toFixed(1)}%`;
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ maxWidth: '700px' }} onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            {isImported ? <Box size={20} /> : <Brain size={20} />}
                        </div>
                        <div>
                            <h2 className="modal__title">{model.name}</h2>
                            <p className="modal__subtitle">
                                {isImported ? 'Imported Model Details' : 'Promoted Model Details'}
                            </p>
                        </div>
                    </div>
                    <button
                        className="modal__close"
                        onClick={onClose}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="modal__body">
                    {/* Provenance Badge */}
                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                            backgroundColor: isImported ? 'var(--color-primary-500)' : 'var(--color-success-500)',
                            color: 'white',
                            padding: '6px 12px',
                            borderRadius: 'var(--border-radius-md)',
                            fontSize: 'var(--font-size-sm)',
                            fontWeight: 600,
                            letterSpacing: '0.5px',
                        }}>
                            {isImported ? <Upload size={14} /> : <Zap size={14} />}
                            {isImported ? 'IMPORTED MODEL' : 'PROMOTED MODEL'}
                        </div>
                    </div>

                    {/* Description */}
                    {model.description && (
                        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <h3 style={{
                                fontSize: 'var(--font-size-md)',
                                fontWeight: 600,
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--color-text-primary)'
                            }}>
                                Description
                            </h3>
                            <p style={{
                                fontSize: 'var(--font-size-sm)',
                                color: 'var(--color-text-secondary)',
                                lineHeight: 1.5
                            }}>
                                {model.description}
                            </p>
                        </div>
                    )}

                    {/* Performance Metrics - Only for models with metrics */}
                    {model.metrics && (model.metrics.map50 || model.metrics.map50_95) && (
                        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <h3 style={{
                                fontSize: 'var(--font-size-md)',
                                fontWeight: 600,
                                marginBottom: 'var(--spacing-md)',
                                color: 'var(--color-text-primary)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-xs)'
                            }}>
                                <TrendingUp size={16} />
                                Performance Metrics
                            </h3>
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                                gap: 'var(--spacing-md)',
                                padding: 'var(--spacing-md)',
                                backgroundColor: 'var(--color-success-50)',
                                borderRadius: 'var(--border-radius-md)',
                                border: '1px solid var(--color-success-200)'
                            }}>
                                {Object.entries(model.metrics).map(([key, value]) => (
                                    <div key={key} style={{ textAlign: 'center' }}>
                                        <div style={{
                                            fontSize: 'var(--font-size-xs)',
                                            color: 'var(--color-text-secondary)',
                                            marginBottom: '4px',
                                            textTransform: 'uppercase',
                                            letterSpacing: '0.05em'
                                        }}>
                                            {key.replace('_', '-')}
                                        </div>
                                        <div style={{
                                            fontSize: 'var(--font-size-lg)',
                                            fontWeight: 600,
                                            color: 'var(--color-success-700)'
                                        }}>
                                            {typeof value === 'number' ? formatMetric(value) : value}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Model Info */}
                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <h3 style={{
                            fontSize: 'var(--font-size-md)',
                            fontWeight: 600,
                            marginBottom: 'var(--spacing-md)',
                            color: 'var(--color-text-primary)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--spacing-xs)'
                        }}>
                            <Package size={16} />
                            Model Information
                        </h3>
                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: '1fr 1fr',
                            gap: 'var(--spacing-md)',
                            fontSize: 'var(--font-size-sm)'
                        }}>
                            <div>
                                <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                    Created:
                                </span>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginTop: '2px' }}>
                                    <Calendar size={14} />
                                    {formatDate(model.created)}
                                </div>
                            </div>
                            <div>
                                <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                    Version:
                                </span>
                                <div style={{ marginTop: '2px' }}>
                                    <code style={{
                                        fontSize: 'var(--font-size-xs)',
                                        backgroundColor: 'var(--color-surface)',
                                        padding: '2px 6px',
                                        borderRadius: 'var(--border-radius-sm)'
                                    }}>
                                        {model.version}
                                    </code>
                                </div>
                            </div>

                            {isImported ? (
                                <>
                                    {model.provenance && (
                                        <div>
                                            <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                                Source File:
                                            </span>
                                            <div style={{ marginTop: '2px' }}>
                                                <code style={{
                                                    fontSize: 'var(--font-size-xs)',
                                                    backgroundColor: 'var(--color-surface)',
                                                    padding: '2px 6px',
                                                    borderRadius: 'var(--border-radius-sm)'
                                                }}>
                                                    {model.provenance}
                                                </code>
                                            </div>
                                        </div>
                                    )}
                                    {model.task && (
                                        <div>
                                            <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                                Task:
                                            </span>
                                            <div style={{ marginTop: '2px', textTransform: 'capitalize' }}>
                                                {model.task}
                                            </div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <>
                                    {model.run_id && (
                                        <div>
                                            <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                                Training Run:
                                            </span>
                                            <div style={{ marginTop: '2px' }}>
                                                <code style={{
                                                    fontSize: 'var(--font-size-xs)',
                                                    backgroundColor: 'var(--color-surface)',
                                                    padding: '2px 6px',
                                                    borderRadius: 'var(--border-radius-sm)'
                                                }}>
                                                    {model.run_id}
                                                </code>
                                            </div>
                                        </div>
                                    )}
                                    {model.dataset_name && (
                                        <div>
                                            <span style={{ fontWeight: 500, color: 'var(--color-text-secondary)' }}>
                                                Dataset:
                                            </span>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)', marginTop: '2px' }}>
                                                <Database size={14} />
                                                {model.dataset_name}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>

                    {/* Classes - For imported models */}
                    {isImported && model.classes && model.classes.length > 0 && (
                        <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            <h3 style={{
                                fontSize: 'var(--font-size-md)',
                                fontWeight: 600,
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--color-text-primary)'
                            }}>
                                Classes ({model.classes.length})
                            </h3>
                            <div style={{
                                maxHeight: '200px',
                                overflowY: 'auto',
                                padding: 'var(--spacing-md)',
                                backgroundColor: 'var(--color-surface)',
                                borderRadius: 'var(--border-radius-md)',
                                border: '1px solid var(--color-border)'
                            }}>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
                                    gap: 'var(--spacing-xs)',
                                    fontSize: 'var(--font-size-xs)'
                                }}>
                                    {model.classes.map((className, index) => (
                                        <div
                                            key={index}
                                            style={{
                                                padding: '4px 8px',
                                                backgroundColor: 'var(--color-primary-100)',
                                                color: 'var(--color-primary-700)',
                                                borderRadius: 'var(--border-radius-sm)',
                                                textAlign: 'center'
                                            }}
                                        >
                                            {className}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* File Path */}
                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <h3 style={{
                            fontSize: 'var(--font-size-md)',
                            fontWeight: 600,
                            marginBottom: 'var(--spacing-sm)',
                            color: 'var(--color-text-primary)'
                        }}>
                            File Location
                        </h3>
                        <div style={{
                            padding: 'var(--spacing-sm)',
                            backgroundColor: 'var(--color-surface)',
                            borderRadius: 'var(--border-radius-md)',
                            border: '1px solid var(--color-border)',
                            fontFamily: 'monospace',
                            fontSize: 'var(--font-size-xs)',
                            wordBreak: 'break-all',
                            color: 'var(--color-text-secondary)'
                        }}>
                            {model.path}
                        </div>
                    </div>

                    {/* Tags */}
                    {model.tags && model.tags.length > 0 && (
                        <div>
                            <h3 style={{
                                fontSize: 'var(--font-size-md)',
                                fontWeight: 600,
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--color-text-primary)'
                            }}>
                                Tags
                            </h3>
                            <div style={{
                                display: 'flex',
                                gap: 'var(--spacing-xs)',
                                flexWrap: 'wrap'
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
                                            padding: '4px 10px',
                                            borderRadius: 'var(--border-radius-sm)',
                                        }}
                                    >
                                        <Tag size={10} />
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="modal__footer">
                    <button
                        className="btn btn--secondary"
                        onClick={onClose}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ModelDetailsModal;