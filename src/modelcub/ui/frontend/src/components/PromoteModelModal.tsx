import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from '@/lib/toast';
import type { TrainingRun } from '@/lib/api/types';

interface PromoteModelModalProps {
    run: TrainingRun;
    onClose: () => void;
    onSuccess: () => void;
}

export default function PromoteModelModal({ run, onClose, onSuccess }: PromoteModelModalProps) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [isPromoting, setIsPromoting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!name.trim()) {
            toast.error('Model name is required');
            return;
        }

        setIsPromoting(true);
        try {
            const tagsList = tags.trim() ? tags.split(',').map(t => t.trim()).filter(Boolean) : undefined;

            await api.promoteModel(
                run.id,
                name.trim(),
                description.trim() || undefined,
                tagsList
            );

            toast.success(`Model "${name}" promoted successfully`);
            onSuccess();
            onClose();

            setName('');
            setDescription('');
            setTags('');
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to promote model');
        } finally {
            setIsPromoting(false);
        }
    };

    const formatPercent = (val: number | null | undefined) =>
        val !== null && val !== undefined ? `${(val * 100).toFixed(1)}%` : 'N/A';

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Upload size={20} />
                        </div>
                        <div>
                            <h2 className="modal__title">Promote Model</h2>
                            <p className="modal__subtitle">Promote trained model to production</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="modal__close"
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="modal__body">
                    {/* Run Info */}
                    <div style={{
                        padding: 'var(--spacing-md)',
                        backgroundColor: 'var(--color-surface)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--border-radius-md)',
                        marginBottom: 'var(--spacing-lg)'
                    }}>
                        <div style={{
                            display: 'grid',
                            gap: 'var(--spacing-sm)',
                            fontSize: 'var(--font-size-sm)',
                            marginBottom: 'var(--spacing-md)'
                        }}>
                            <div>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Run ID:</span>{' '}
                                <code style={{
                                    padding: '2px 6px',
                                    backgroundColor: 'var(--color-background)',
                                    borderRadius: 'var(--border-radius-sm)',
                                    fontSize: 'var(--font-size-xs)',
                                    fontFamily: 'monospace'
                                }}>{run.id}</code>
                            </div>
                            <div>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Dataset:</span>{' '}
                                <strong>{run.dataset_name}</strong>
                            </div>
                            <div>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Model:</span>{' '}
                                <strong>{run.config.model}</strong>
                            </div>
                        </div>

                        <div style={{
                            display: 'grid',
                            gridTemplateColumns: '1fr 1fr',
                            gap: 'var(--spacing-md)',
                            paddingTop: 'var(--spacing-md)',
                            borderTop: '1px solid var(--color-border)'
                        }}>
                            <div>
                                <div style={{
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--color-text-secondary)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em',
                                    marginBottom: 'var(--spacing-xs)'
                                }}>MAP50</div>
                                <div style={{
                                    fontSize: 'var(--font-size-xl)',
                                    fontWeight: 600,
                                    color: 'var(--color-success)'
                                }}>
                                    {formatPercent(run.metrics?.map50)}
                                </div>
                            </div>
                            <div>
                                <div style={{
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--color-text-secondary)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em',
                                    marginBottom: 'var(--spacing-xs)'
                                }}>MAP50-95</div>
                                <div style={{
                                    fontSize: 'var(--font-size-xl)',
                                    fontWeight: 600,
                                    color: 'var(--color-success)'
                                }}>
                                    {formatPercent(run.metrics?.map50_95)}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="model-name" className="form-label">
                                Model Name <span style={{ color: 'var(--color-error)' }}>*</span>
                            </label>
                            <input
                                id="model-name"
                                type="text"
                                className="form-input"
                                placeholder="e.g., detector-v1, segmenter-prod"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                disabled={isPromoting}
                                required
                            />
                            <small className="form-help">Choose a unique name for this model</small>
                        </div>

                        <div className="form-group">
                            <label htmlFor="model-description" className="form-label">
                                Description (optional)
                            </label>
                            <textarea
                                id="model-description"
                                className="form-input"
                                placeholder="e.g., Improved detector with 10k labeled images"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                disabled={isPromoting}
                                rows={3}
                            />
                        </div>
                        <div style={{ marginBottom: '0' }}>
                            <label
                                htmlFor="tags"
                                style={{
                                    display: 'block',
                                    fontSize: '14px',
                                    fontWeight: 500,
                                    marginBottom: '8px',
                                    color: '#f1f5f9'
                                }}
                            >
                                Tags (optional)
                            </label>
                            <input
                                id="tags"
                                type="text"
                                value={tags}
                                onChange={(e) => setTags(e.target.value)}
                                placeholder="e.g., production, v1, yolov8"
                                disabled={isPromoting}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    backgroundColor: '#0f172a',
                                    border: '1px solid #334155',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    color: '#f1f5f9',
                                    outline: 'none'
                                }}
                            />
                            <small style={{
                                display: 'block',
                                marginTop: '6px',
                                fontSize: '12px',
                                color: '#94a3b8'
                            }}>
                                Comma-separated tags for organization
                            </small>
                        </div>
                    </form>
                </div>

                {/* Footer */}
                <div className="modal__footer">
                    <button
                        type="button"
                        onClick={onClose}
                        className="btn btn--secondary"
                        disabled={isPromoting}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        className="btn btn--primary"
                        disabled={isPromoting}
                    >
                        <Upload size={16} />
                        {isPromoting ? 'Promoting...' : 'Promote Model'}
                    </button>
                </div>
            </div>
        </div>
    );
}