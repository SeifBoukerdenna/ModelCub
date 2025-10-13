import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Save, AlertCircle, RefreshCw } from 'lucide-react';

// NEW: Use API hooks
import { useGetProjectConfig, useSetProjectConfig } from '@/lib/api';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import { toast } from '@/lib/toast';

// Components
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';


const Settings = () => {
    const selectedProject = useProjectStore(selectSelectedProject);

    // API hooks
    const { data: config, loading, error, execute: loadConfig } = useGetProjectConfig();
    const { loading: saving, execute: saveConfigValue } = useSetProjectConfig();

    // Form state
    const [device, setDevice] = useState('');
    const [batchSize, setBatchSize] = useState(16);
    const [imageSize, setImageSize] = useState(640);
    const [workers, setWorkers] = useState(8);
    const [hasChanges, setHasChanges] = useState(false);

    // Load config when project changes
    useEffect(() => {
        if (selectedProject) {
            loadConfig(selectedProject.path);
        }
    }, [selectedProject?.path]);

    // Update form when config loads
    useEffect(() => {
        if (config) {
            setDevice(config.defaults.device);
            setBatchSize(config.defaults.batch_size);
            setImageSize(config.defaults.image_size);
            setWorkers(config.defaults.workers);
            setHasChanges(false);
        }
    }, [config]);

    // Track changes
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

    // No project selected
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

    // Loading state
    if (loading && !config) {
        return <Loading message={`Loading settings for ${selectedProject.name}...`} />;
    }

    // Error state
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
        <div style={{ maxWidth: '800px' }}>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    Settings
                </h1>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-md)' }}>
                    Configure your project defaults and paths
                </p>
                <div style={{
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    backgroundColor: 'var(--color-primary-50)',
                    border: '2px solid var(--color-primary-500)',
                    borderRadius: 'var(--border-radius-md)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-xs)',
                }}>
                    <SettingsIcon size={16} style={{ color: 'var(--color-primary-600)' }} />
                    <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-primary-700)' }}>
                        Editing: {config.project.name}
                    </span>
                </div>
            </div>

            {/* Warning */}
            <div className="alert alert--warning" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <AlertCircle size={20} />
                <div>
                    <strong>Do Not Edit Config Files Directly</strong>
                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                        Never manually edit .modelcub/config.yaml. Always use this UI, the CLI, or the Python SDK.
                    </p>
                </div>
            </div>

            {/* Settings Form */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ marginBottom: 'var(--spacing-lg)' }}>Training Defaults</h3>

                <div className="form-group">
                    <label htmlFor="device">Device</label>
                    <select
                        id="device"
                        value={device}
                        onChange={(e) => setDevice(e.target.value)}
                        disabled={saving}
                    >
                        <option value="cuda">CUDA (GPU)</option>
                        <option value="cpu">CPU</option>
                        <option value="mps">MPS (Apple Silicon)</option>
                    </select>
                    <small style={{ color: 'var(--color-text-secondary)' }}>
                        Device to use for training
                    </small>
                </div>

                <div className="form-group">
                    <label htmlFor="batch-size">Batch Size</label>
                    <input
                        id="batch-size"
                        type="number"
                        min="1"
                        max="256"
                        value={batchSize}
                        onChange={(e) => setBatchSize(parseInt(e.target.value))}
                        disabled={saving}
                    />
                    <small style={{ color: 'var(--color-text-secondary)' }}>
                        Number of images per training batch (1-256)
                    </small>
                </div>

                <div className="form-group">
                    <label htmlFor="image-size">Image Size</label>
                    <input
                        id="image-size"
                        type="number"
                        min="32"
                        max="1280"
                        step="32"
                        value={imageSize}
                        onChange={(e) => setImageSize(parseInt(e.target.value))}
                        disabled={saving}
                    />
                    <small style={{ color: 'var(--color-text-secondary)' }}>
                        Input image size for training (32-1280, multiples of 32)
                    </small>
                </div>

                <div className="form-group">
                    <label htmlFor="workers">Data Workers</label>
                    <input
                        id="workers"
                        type="number"
                        min="0"
                        max="32"
                        value={workers}
                        onChange={(e) => setWorkers(parseInt(e.target.value))}
                        disabled={saving}
                    />
                    <small style={{ color: 'var(--color-text-secondary)' }}>
                        Number of workers for data loading (0-32)
                    </small>
                </div>
            </div>

            {/* Project Info (Read-only) */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ marginBottom: 'var(--spacing-md)' }}>Project Information</h3>

                <div style={{ display: 'grid', gap: 'var(--spacing-sm)', fontSize: 'var(--font-size-sm)' }}>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Name:</span>
                        <strong style={{ marginLeft: 'var(--spacing-xs)' }}>{config.project.name}</strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Created:</span>
                        <strong style={{ marginLeft: 'var(--spacing-xs)' }}>
                            {new Date(config.project.created).toLocaleDateString()}
                        </strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Version:</span>
                        <strong style={{ marginLeft: 'var(--spacing-xs)' }}>{config.project.version}</strong>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'flex-end' }}>
                <button
                    onClick={handleReset}
                    disabled={!hasChanges || saving}
                    className="btn btn--secondary"
                >
                    Reset
                </button>
                <button
                    onClick={handleSave}
                    disabled={!hasChanges || saving}
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
    );
};

export default Settings;