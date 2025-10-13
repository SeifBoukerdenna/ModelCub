import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertCircle, RefreshCw, Info } from 'lucide-react';

import { useGetProjectConfig, useSetProjectConfig } from '@/lib/api';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import { toast } from '@/lib/toast';

import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';

const Settings = () => {
    const selectedProject = useProjectStore(selectSelectedProject);

    const { data: config, loading, error, execute: loadConfig } = useGetProjectConfig();
    const { loading: saving, execute: saveConfigValue } = useSetProjectConfig();

    const [device, setDevice] = useState('');
    const [batchSize, setBatchSize] = useState(16);
    const [imageSize, setImageSize] = useState(640);
    const [workers, setWorkers] = useState(8);
    const [hasChanges, setHasChanges] = useState(false);

    useEffect(() => {
        if (selectedProject) {
            loadConfig(selectedProject.path);
        }
    }, [selectedProject?.path]);

    useEffect(() => {
        if (config) {
            setDevice(config.defaults.device);
            setBatchSize(config.defaults.batch_size);
            setImageSize(config.defaults.image_size);
            setWorkers(config.defaults.workers);
            setHasChanges(false);
        }
    }, [config]);

    useEffect(() => {
        if (config) {
            const changed =
                device !== config.defaults.device ||
                batchSize !== config.defaults.batch_size ||
                imageSize !== config.defaults.image_size ||
                workers !== config.defaults.workers;
            setHasChanges(changed);
        }
    }, [device, batchSize, imageSize, workers, config]);

    const handleSave = async () => {
        if (!config || !selectedProject) return;

        try {
            const updates = [];

            if (device !== config.defaults.device) {
                updates.push(saveConfigValue(selectedProject.path, { key: 'defaults.device', value: device }));
            }
            if (batchSize !== config.defaults.batch_size) {
                updates.push(saveConfigValue(selectedProject.path, { key: 'defaults.batch_size', value: batchSize }));
            }
            if (imageSize !== config.defaults.image_size) {
                updates.push(saveConfigValue(selectedProject.path, { key: 'defaults.image_size', value: imageSize }));
            }
            if (workers !== config.defaults.workers) {
                updates.push(saveConfigValue(selectedProject.path, { key: 'defaults.workers', value: workers }));
            }

            await Promise.all(updates);
            toast.success('Settings saved successfully');
            setHasChanges(false);
            loadConfig(selectedProject.path);
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to save settings');
        }
    };

    const handleReset = () => {
        if (config) {
            setDevice(config.defaults.device);
            setBatchSize(config.defaults.batch_size);
            setImageSize(config.defaults.image_size);
            setWorkers(config.defaults.workers);
            setHasChanges(false);
        }
    };

    if (!selectedProject) {
        return (
            <div>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Settings</h1>
                <div className="empty-state">
                    <AlertCircle size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No Project Selected</h3>
                    <p className="empty-state__description">
                        Select a project to view and edit its settings.
                    </p>
                </div>
            </div>
        );
    }

    if (loading && !config) {
        return <Loading message={`Loading settings for ${selectedProject.name}...`} />;
    }

    if (error && !config) {
        return (
            <div>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Settings</h1>
                <ErrorMessage message={error} />
                <button
                    onClick={() => loadConfig(selectedProject.path)}
                    className="btn btn--secondary"
                    style={{ marginTop: 'var(--spacing-md)' }}
                >
                    <RefreshCw size={18} />
                    Retry
                </button>
            </div>
        );
    }

    if (!config) {
        return <Loading message="Loading configuration..." />;
    }

    return (
        <div className="settings-container">
            {/* Header */}
            <div className="settings-header">
                <div>
                    <h1 className="settings-header__title">Settings</h1>
                    <p className="settings-header__subtitle">
                        Configure your project defaults and paths
                    </p>
                </div>
                <div className="settings-header__badge">
                    <SettingsIcon size={16} />
                    <span>{config.project.name}</span>
                </div>
            </div>

            {/* Warning Alert */}
            <div className="alert alert--warning">
                <AlertCircle size={20} />
                <div>
                    <strong>Do Not Edit Config Files Directly</strong>
                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                        Never manually edit .modelcub/config.yaml. Always use this UI, the CLI, or the Python SDK.
                    </p>
                </div>
            </div>

            {/* Training Defaults Card */}
            <div className="settings-section">
                <div className="settings-section__header">
                    <h3 className="settings-section__title">Training Defaults</h3>
                    <p className="settings-section__description">
                        Default values for training configuration
                    </p>
                </div>

                <div className="settings-section__body">
                    <div className="settings-grid">
                        {/* Device */}
                        <div className="form-group">
                            <label htmlFor="device" className="form-label">
                                Device
                            </label>
                            <select
                                id="device"
                                className="form-input"
                                value={device}
                                onChange={(e) => setDevice(e.target.value)}
                                disabled={saving}
                            >
                                <option value="cuda">CUDA (GPU)</option>
                                <option value="cpu">CPU</option>
                                <option value="mps">MPS (Apple Silicon)</option>
                            </select>
                            <p className="form-help">Device to use for training</p>
                        </div>

                        {/* Batch Size */}
                        <div className="form-group">
                            <label htmlFor="batch-size" className="form-label">
                                Batch Size
                            </label>
                            <input
                                id="batch-size"
                                type="number"
                                className="form-input"
                                min="1"
                                max="256"
                                value={batchSize}
                                onChange={(e) => setBatchSize(parseInt(e.target.value))}
                                disabled={saving}
                            />
                            <p className="form-help">Number of images per training batch (1-256)</p>
                        </div>

                        {/* Image Size */}
                        <div className="form-group">
                            <label htmlFor="image-size" className="form-label">
                                Image Size
                            </label>
                            <input
                                id="image-size"
                                type="number"
                                className="form-input"
                                min="32"
                                max="1280"
                                step="32"
                                value={imageSize}
                                onChange={(e) => setImageSize(parseInt(e.target.value))}
                                disabled={saving}
                            />
                            <p className="form-help">Input image size for training (32-1280, multiples of 32)</p>
                        </div>

                        {/* Data Workers */}
                        <div className="form-group">
                            <label htmlFor="workers" className="form-label">
                                Data Workers
                            </label>
                            <input
                                id="workers"
                                type="number"
                                className="form-input"
                                min="0"
                                max="32"
                                value={workers}
                                onChange={(e) => setWorkers(parseInt(e.target.value))}
                                disabled={saving}
                            />
                            <p className="form-help">Number of workers for data loading (0-32)</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Project Info Card */}
            <div className="settings-section">
                <div className="settings-section__header">
                    <h3 className="settings-section__title">Project Information</h3>
                    <p className="settings-section__description">Read-only project metadata</p>
                </div>

                <div className="settings-section__body">
                    <div className="info-grid">
                        <div className="info-item">
                            <span className="info-item__label">Name</span>
                            <span className="info-item__value">{config.project.name}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-item__label">Created</span>
                            <span className="info-item__value">
                                {new Date(config.project.created).toLocaleDateString()}
                            </span>
                        </div>
                        <div className="info-item">
                            <span className="info-item__label">Version</span>
                            <span className="info-item__value">{config.project.version}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            {hasChanges && (
                <div className="settings-actions">
                    <div className="settings-actions__indicator">
                        <Info size={16} />
                        <span>You have unsaved changes</span>
                    </div>
                    <div className="settings-actions__buttons">
                        <button
                            onClick={handleReset}
                            disabled={saving}
                            className="btn btn--secondary"
                        >
                            Reset
                        </button>
                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="btn btn--primary"
                        >
                            {saving ? (
                                <>
                                    <Save size={18} className="spinner" />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={18} />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Settings;