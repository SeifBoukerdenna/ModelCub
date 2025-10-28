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

    const handleClose = () => {
        if (!isCreating) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal create-run-modal" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="modal__header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                        <div className="modal__icon">
                            <Zap size={20} />
                        </div>
                        <h2 className="modal__title">Create Training Run</h2>
                    </div>
                    <button
                        className="modal__close"
                        onClick={handleClose}
                        disabled={isCreating}
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal__body">
                        {/* Dataset */}
                        <div className="form-group">
                            <label htmlFor="dataset" className="form-label">
                                Dataset <span style={{ color: 'var(--color-error)' }}>*</span>
                            </label>
                            <select
                                id="dataset"
                                className="form-input"
                                value={datasetName}
                                onChange={(e) => setDatasetName(e.target.value)}
                                required
                                disabled={datasetsLoading || isCreating}
                            >
                                <option value="">Select a dataset</option>
                                {datasets?.map((ds) => (
                                    <option key={ds.name} value={ds.name}>
                                        {ds.name} ({ds.images} images)
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Model & Device */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                            <div className="form-group">
                                <label htmlFor="model" className="form-label">Model</label>
                                <select
                                    id="model"
                                    className="form-input"
                                    value={model}
                                    onChange={(e) => setModel(e.target.value)}
                                    disabled={isCreating}
                                >
                                    <option value="yolov8n">YOLOv8n (Nano)</option>
                                    <option value="yolov8s">YOLOv8s (Small)</option>
                                    <option value="yolov8m">YOLOv8m (Medium)</option>
                                    <option value="yolov8l">YOLOv8l (Large)</option>
                                    <option value="yolov8x">YOLOv8x (Extra Large)</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="device" className="form-label">Device</label>
                                <select
                                    id="device"
                                    className="form-input"
                                    value={device}
                                    onChange={(e) => setDevice(e.target.value)}
                                    disabled={isCreating}
                                >
                                    <option value="auto">Auto</option>
                                    <option value="cpu">CPU</option>
                                    <option value="0">GPU (cuda:0)</option>
                                </select>
                            </div>
                        </div>

                        {/* Training Parameters */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
                            <div className="form-group">
                                <label htmlFor="epochs" className="form-label">Epochs</label>
                                <input
                                    id="epochs"
                                    type="number"
                                    className="form-input"
                                    min="1"
                                    max="1000"
                                    value={epochs}
                                    onChange={(e) => setEpochs(parseInt(e.target.value))}
                                    disabled={isCreating}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="batch" className="form-label">Batch Size</label>
                                <input
                                    id="batch"
                                    type="number"
                                    className="form-input"
                                    min="1"
                                    max="128"
                                    value={batch}
                                    onChange={(e) => setBatch(parseInt(e.target.value))}
                                    disabled={isCreating}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="imgsz" className="form-label">Image Size</label>
                                <select
                                    id="imgsz"
                                    className="form-input"
                                    value={imgsz}
                                    onChange={(e) => setImgsz(parseInt(e.target.value))}
                                    disabled={isCreating}
                                >
                                    <option value="320">320</option>
                                    <option value="416">416</option>
                                    <option value="640">640</option>
                                    <option value="1280">1280</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label htmlFor="patience" className="form-label">Patience</label>
                                <input
                                    id="patience"
                                    type="number"
                                    className="form-input"
                                    min="0"
                                    max="200"
                                    value={patience}
                                    onChange={(e) => setPatience(parseInt(e.target.value))}
                                    disabled={isCreating}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="modal__footer">
                        <button
                            type="button"
                            className="btn btn--secondary"
                            onClick={handleClose}
                            disabled={isCreating}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn--primary"
                            disabled={isCreating || !datasetName}
                        >
                            {isCreating ? (
                                <>
                                    <Zap size={18} className="spinner" />
                                    Creating...
                                </>
                            ) : (
                                <>
                                    <Zap size={18} />
                                    Create Run
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateRunModal;