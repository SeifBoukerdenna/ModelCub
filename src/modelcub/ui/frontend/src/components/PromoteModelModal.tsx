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
        <div
            onClick={onClose}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '20px'
            }}
        >
            <div
                onClick={(e) => e.stopPropagation()}
                style={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '12px',
                    width: '100%',
                    maxWidth: '600px',
                    maxHeight: '90vh',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column'
                }}
            >
                {/* Header */}
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '24px 28px',
                    borderBottom: '1px solid #334155'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Upload size={24} style={{ color: '#60a5fa' }} />
                        <h2 style={{
                            fontSize: '20px',
                            fontWeight: 600,
                            margin: 0,
                            color: '#f1f5f9'
                        }}>
                            Promote Model
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#94a3b8',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Content */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '28px'
                }}>
                    <p style={{
                        color: '#94a3b8',
                        fontSize: '14px',
                        margin: '0 0 24px 0'
                    }}>
                        Promote trained model to production
                    </p>

                    {/* Run Info */}
                    <div style={{
                        padding: '20px',
                        backgroundColor: '#334155',
                        borderRadius: '8px',
                        marginBottom: '24px'
                    }}>
                        <div style={{ marginBottom: '12px', fontSize: '14px' }}>
                            <span style={{ color: '#94a3b8' }}>Run ID: </span>
                            <code style={{
                                color: '#f1f5f9',
                                fontFamily: 'monospace'
                            }}>
                                {run.id}
                            </code>
                        </div>
                        <div style={{ marginBottom: '12px', fontSize: '14px' }}>
                            <span style={{ color: '#94a3b8' }}>Dataset: </span>
                            <span style={{ color: '#f1f5f9' }}>{run.dataset_name}</span>
                        </div>
                        <div style={{ marginBottom: '20px', fontSize: '14px' }}>
                            <span style={{ color: '#94a3b8' }}>Model: </span>
                            <code style={{
                                color: '#f1f5f9',
                                fontFamily: 'monospace'
                            }}>
                                {run.config?.model}
                            </code>
                        </div>

                        {run.metrics && (
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(2, 1fr)',
                                gap: '20px',
                                paddingTop: '16px',
                                borderTop: '1px solid #475569'
                            }}>
                                <div>
                                    <div style={{
                                        fontSize: '11px',
                                        color: '#94a3b8',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.5px',
                                        marginBottom: '6px'
                                    }}>
                                        MAP50
                                    </div>
                                    <div style={{
                                        fontSize: '20px',
                                        fontWeight: 600,
                                        color: '#10b981'
                                    }}>
                                        {formatPercent(run.metrics.map50)}
                                    </div>
                                </div>
                                <div>
                                    <div style={{
                                        fontSize: '11px',
                                        color: '#94a3b8',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.5px',
                                        marginBottom: '6px'
                                    }}>
                                        MAP50-95
                                    </div>
                                    <div style={{
                                        fontSize: '20px',
                                        fontWeight: 600,
                                        color: '#10b981'
                                    }}>
                                        {formatPercent(run.metrics.map50_95)}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '20px' }}>
                            <label
                                htmlFor="name"
                                style={{
                                    display: 'block',
                                    fontSize: '14px',
                                    fontWeight: 500,
                                    marginBottom: '8px',
                                    color: '#f1f5f9'
                                }}
                            >
                                Model Name <span style={{ color: '#ef4444' }}>*</span>
                            </label>
                            <input
                                id="name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="e.g., detector-v1, segmenter-prod"
                                required
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
                                Choose a unique name for this model
                            </small>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label
                                htmlFor="description"
                                style={{
                                    display: 'block',
                                    fontSize: '14px',
                                    fontWeight: 500,
                                    marginBottom: '8px',
                                    color: '#f1f5f9'
                                }}
                            >
                                Description (optional)
                            </label>
                            <textarea
                                id="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="e.g., Improved detector with 10k labeled images"
                                rows={3}
                                disabled={isPromoting}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    backgroundColor: '#0f172a',
                                    border: '1px solid #334155',
                                    borderRadius: '6px',
                                    fontSize: '14px',
                                    color: '#f1f5f9',
                                    resize: 'vertical',
                                    fontFamily: 'inherit',
                                    outline: 'none'
                                }}
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
                <div style={{
                    padding: '20px 28px',
                    borderTop: '1px solid #334155',
                    display: 'flex',
                    gap: '12px',
                    justifyContent: 'flex-end'
                }}>
                    <button
                        type="button"
                        onClick={onClose}
                        disabled={isPromoting}
                        style={{
                            padding: '10px 24px',
                            backgroundColor: 'transparent',
                            color: '#f1f5f9',
                            border: '1px solid #475569',
                            borderRadius: '6px',
                            fontSize: '14px',
                            fontWeight: 500,
                            cursor: isPromoting ? 'not-allowed' : 'pointer',
                            opacity: isPromoting ? 0.5 : 1
                        }}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        disabled={isPromoting}
                        style={{
                            padding: '10px 24px',
                            backgroundColor: '#3b82f6',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '14px',
                            fontWeight: 500,
                            cursor: isPromoting ? 'not-allowed' : 'pointer',
                            opacity: isPromoting ? 0.5 : 1,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                    >
                        <Upload size={16} />
                        {isPromoting ? 'Promoting...' : 'Promote Model'}
                    </button>
                </div>
            </div>
        </div>
    );
}