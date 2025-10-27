import React, { useState, useEffect } from 'react';
import { X, Zap } from 'lucide-react';
import { api, useListDatasets } from '@/lib/api';
import { toast } from '@/lib/toast';

interface CreateRunModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const CreateRunModal: React.FC<CreateRunModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const [datasetName, setDatasetName] = useState('');
    const [model, setModel] = useState('yolov8n');
    const [epochs, setEpochs] = useState(100);
    const [batch, setBatch] = useState(16);
    const [imgsz, setImgsz] = useState(640);
    const [device, setDevice] = useState('auto');
    const [patience, setPatience] = useState(50);
    const [workers, setWorkers] = useState(8);
    const [isCreating, setIsCreating] = useState(false);

    const { data: datasets, loading: datasetsLoading, execute: loadDatasets } = useListDatasets();

    useEffect(() => {
        if (isOpen) {
            loadDatasets();
        }
    }, [isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!datasetName) {
            toast.error('Please select a dataset');
            return;
        }

        setIsCreating(true);
        try {
            await api.createRun({
                dataset_name: datasetName,
                model,
                epochs,
                batch,
                imgsz,
                device,
                patience,
                workers,
                task: 'detect',
                save_period: 10,
                seed: null
            });

            toast.success('Training run created successfully');
            onSuccess();
            onClose();

            // Reset form
            setDatasetName('');
            setModel('yolov8n');
            setEpochs(100);
            setBatch(16);
            setImgsz(640);
            setDevice('auto');
            setPatience(50);
            setWorkers(8);
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to create run');
        } finally {
            setIsCreating(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.75)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: 'var(--spacing-lg)',
            }}
            onClick={onClose}
        >
            <div
                style={{
                    backgroundColor: 'var(--color-bg)',
                    borderRadius: 'var(--border-radius-lg)',
                    maxWidth: '600px',
                    width: '100%',
                    maxHeight: '90vh',
                    overflow: 'auto',
                    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    style={{
                        padding: 'var(--spacing-lg)',
                        borderBottom: '1px solid var(--color-border)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}
                >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <Zap size={24} style={{ color: '#10b981' }} />
                        <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, margin: 0 }}>
                            Create Training Run
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: 'var(--spacing-xs)',
                            color: 'var(--color-text-secondary)',
                        }}
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} style={{ padding: 'var(--spacing-lg)' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-lg)' }}>
                        {/* Dataset */}
                        <div>
                            <label
                                htmlFor="dataset"
                                style={{
                                    display: 'block',
                                    fontSize: 'var(--font-size-sm)',
                                    fontWeight: 600,
                                    marginBottom: 'var(--spacing-xs)',
                                }}
                            >
                                Dataset *
                            </label>
                            <select
                                id="dataset"
                                value={datasetName}
                                onChange={(e) => setDatasetName(e.target.value)}
                                required
                                disabled={datasetsLoading || isCreating}
                                style={{
                                    width: '100%',
                                    padding: 'var(--spacing-sm)',
                                    borderRadius: 'var(--border-radius-sm)',
                                    border: '1px solid var(--color-border)',
                                    backgroundColor: 'var(--color-surface)',
                                    fontSize: 'var(--font-size-sm)',
                                }}
                            >
                                <option value="">Select a dataset</option>
                                {datasets?.map((ds) => (
                                    <option key={ds.name} value={ds.name}>
                                        {ds.name} ({ds.images} images)
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Model */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                            <div>
                                <label
                                    htmlFor="model"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Model
                                </label>
                                <select
                                    id="model"
                                    value={model}
                                    onChange={(e) => setModel(e.target.value)}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                >
                                    <option value="yolov8n">YOLOv8n (Nano)</option>
                                    <option value="yolov8s">YOLOv8s (Small)</option>
                                    <option value="yolov8m">YOLOv8m (Medium)</option>
                                    <option value="yolov8l">YOLOv8l (Large)</option>
                                    <option value="yolov8x">YOLOv8x (XLarge)</option>
                                    <option value="yolov11n">YOLOv11n (Nano)</option>
                                    <option value="yolov11s">YOLOv11s (Small)</option>
                                    <option value="yolov11m">YOLOv11m (Medium)</option>
                                    <option value="yolov11l">YOLOv11l (Large)</option>
                                    <option value="yolov11x">YOLOv11x (XLarge)</option>
                                </select>
                            </div>

                            <div>
                                <label
                                    htmlFor="device"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Device
                                </label>
                                <select
                                    id="device"
                                    value={device}
                                    onChange={(e) => setDevice(e.target.value)}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                >
                                    <option value="auto">Auto</option>
                                    <option value="cpu">CPU</option>
                                    <option value="cuda">CUDA</option>
                                    <option value="cuda:0">CUDA:0</option>
                                    <option value="cuda:1">CUDA:1</option>
                                </select>
                            </div>
                        </div>

                        {/* Training Parameters */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                            <div>
                                <label
                                    htmlFor="epochs"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Epochs
                                </label>
                                <input
                                    id="epochs"
                                    type="number"
                                    min="1"
                                    max="1000"
                                    value={epochs}
                                    onChange={(e) => setEpochs(parseInt(e.target.value))}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                />
                            </div>

                            <div>
                                <label
                                    htmlFor="batch"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Batch Size
                                </label>
                                <input
                                    id="batch"
                                    type="number"
                                    min="1"
                                    max="128"
                                    value={batch}
                                    onChange={(e) => setBatch(parseInt(e.target.value))}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                />
                            </div>

                            <div>
                                <label
                                    htmlFor="imgsz"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Image Size
                                </label>
                                <select
                                    id="imgsz"
                                    value={imgsz}
                                    onChange={(e) => setImgsz(parseInt(e.target.value))}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                >
                                    <option value="320">320</option>
                                    <option value="416">416</option>
                                    <option value="640">640</option>
                                    <option value="1280">1280</option>
                                </select>
                            </div>

                            <div>
                                <label
                                    htmlFor="patience"
                                    style={{
                                        display: 'block',
                                        fontSize: 'var(--font-size-sm)',
                                        fontWeight: 600,
                                        marginBottom: 'var(--spacing-xs)',
                                    }}
                                >
                                    Patience
                                </label>
                                <input
                                    id="patience"
                                    type="number"
                                    min="0"
                                    max="200"
                                    value={patience}
                                    onChange={(e) => setPatience(parseInt(e.target.value))}
                                    disabled={isCreating}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        border: '1px solid var(--color-border)',
                                        backgroundColor: 'var(--color-surface)',
                                        fontSize: 'var(--font-size-sm)',
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div
                        style={{
                            marginTop: 'var(--spacing-xl)',
                            display: 'flex',
                            gap: 'var(--spacing-sm)',
                            justifyContent: 'flex-end',
                        }}
                    >
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={isCreating}
                            style={{
                                padding: 'var(--spacing-sm) var(--spacing-lg)',
                                backgroundColor: '#374151',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: isCreating ? 'not-allowed' : 'pointer',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                                opacity: isCreating ? 0.6 : 1,
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isCreating || !datasetName}
                            style={{
                                padding: 'var(--spacing-sm) var(--spacing-lg)',
                                backgroundColor: '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: 'var(--border-radius-sm)',
                                cursor: isCreating || !datasetName ? 'not-allowed' : 'pointer',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 600,
                                opacity: isCreating || !datasetName ? 0.6 : 1,
                            }}
                        >
                            {isCreating ? 'Creating...' : 'Create Run'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateRunModal;