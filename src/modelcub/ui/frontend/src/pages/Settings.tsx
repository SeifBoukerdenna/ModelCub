import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save, AlertCircle, Info, RefreshCw, AlertTriangle } from 'lucide-react'
import { toast } from '@/lib/toast'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import Loading from '@/components/Loading'
import ErrorMessage from '@/components/ErrorMessage'

interface ConfigData {
    project: {
        name: string
        created: string
        version: string
    }
    defaults: {
        device: string
        batch_size: number
        image_size: number
        workers: number
        format: string
    }
    paths: {
        data: string
        runs: string
        reports: string
    }
}

const Settings: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const [config, setConfig] = useState<ConfigData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [saving, setSaving] = useState(false)
    const [hasChanges, setHasChanges] = useState(false)

    const [device, setDevice] = useState('')
    const [batchSize, setBatchSize] = useState(16)
    const [imageSize, setImageSize] = useState(640)
    const [workers, setWorkers] = useState(8)

    useEffect(() => {
        if (selectedProject) {
            loadConfig()
        } else {
            setConfig(null)
        }
    }, [selectedProject?.path])

    const loadConfig = async () => {
        if (!selectedProject) return

        try {
            setLoading(true)
            setError(null)

            const response = await fetch(`/api/projects/config?path=${encodeURIComponent(selectedProject.path)}`)
            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Failed to load configuration')
            }

            if (data.success && data.config) {
                setConfig(data.config)
                setDevice(data.config.defaults.device)
                setBatchSize(data.config.defaults.batch_size)
                setImageSize(data.config.defaults.image_size)
                setWorkers(data.config.defaults.workers)
                setHasChanges(false)
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load configuration')
        } finally {
            setLoading(false)
        }
    }

    const saveConfig = async (key: string, value: string | number) => {
        if (!selectedProject) return

        const response = await fetch(`/api/projects/config?path=${encodeURIComponent(selectedProject.path)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, value }),
        })

        const data = await response.json()
        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Failed to save configuration')
        }
        return data
    }

    const handleSave = async () => {
        if (!config || !selectedProject) return

        try {
            setSaving(true)
            const updates = []

            if (device !== config.defaults.device) updates.push(saveConfig('defaults.device', device))
            if (batchSize !== config.defaults.batch_size) updates.push(saveConfig('defaults.batch_size', batchSize))
            if (imageSize !== config.defaults.image_size) updates.push(saveConfig('defaults.image_size', imageSize))
            if (workers !== config.defaults.workers) updates.push(saveConfig('defaults.workers', workers))

            await Promise.all(updates)
            toast.success('Settings saved successfully')
            setHasChanges(false)
            await loadConfig()
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to save settings')
        } finally {
            setSaving(false)
        }
    }

    const handleReset = () => {
        if (config) {
            setDevice(config.defaults.device)
            setBatchSize(config.defaults.batch_size)
            setImageSize(config.defaults.image_size)
            setWorkers(config.defaults.workers)
            setHasChanges(false)
        }
    }

    useEffect(() => {
        if (config) {
            const changed =
                device !== config.defaults.device ||
                batchSize !== config.defaults.batch_size ||
                imageSize !== config.defaults.image_size ||
                workers !== config.defaults.workers
            setHasChanges(changed)
        }
    }, [device, batchSize, imageSize, workers, config])

    if (!selectedProject) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Settings</h1>
                </div>
                <div className="empty-state">
                    <AlertTriangle size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No Project Selected</h3>
                    <p className="empty-state__description">
                        Please select a project to view and edit its settings.
                    </p>
                </div>
            </div>
        )
    }

    if (loading) {
        return <Loading message={`Loading settings for ${selectedProject.name}...`} />
    }

    if (error) {
        return (
            <div>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-lg)' }}>
                    Settings
                </h1>
                <ErrorMessage message={error} />
                <button onClick={loadConfig} className="btn btn--secondary" style={{ marginTop: 'var(--spacing-md)' }}>
                    <RefreshCw size={18} />
                    Retry
                </button>
            </div>
        )
    }

    if (!config) {
        return <Loading message="Loading configuration..." />
    }

    return (
        <div style={{ maxWidth: '800px' }}>
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

            <div className="alert alert--warning" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <AlertCircle size={20} />
                <div>
                    <strong>Do Not Edit Config Files Directly</strong>
                    <p style={{ marginTop: 'var(--spacing-xs)', fontSize: 'var(--font-size-sm)' }}>
                        Never manually edit .modelcub/config.yaml. Always use this UI, the CLI, or the Python SDK.
                    </p>
                </div>
            </div>

            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Project Information
                </h3>
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)', alignItems: 'center' }}>
                    <Info size={16} style={{ color: 'var(--color-primary-500)' }} />
                    <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                        These fields are immutable
                    </span>
                </div>
                <dl style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Project Name
                        </dt>
                        <dd>{config.project.name}</dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Project Path
                        </dt>
                        <dd style={{ fontFamily: 'monospace', fontSize: 'var(--font-size-sm)', wordBreak: 'break-all' }}>
                            {selectedProject.path}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Created
                        </dt>
                        <dd>{new Date(config.project.created).toLocaleDateString()}</dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Version
                        </dt>
                        <dd>{config.project.version}</dd>
                    </div>
                </dl>
            </div>

            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Default Settings
                </h3>

                <div style={{ display: 'grid', gap: 'var(--spacing-lg)' }}>
                    <div className="form-group">
                        <label htmlFor="device" className="form-label">Device</label>
                        <select id="device" value={device} onChange={(e) => setDevice(e.target.value)} className="form-input">
                            <option value="cuda">CUDA (GPU)</option>
                            <option value="mps">MPS (Apple Silicon)</option>
                            <option value="cpu">CPU</option>
                        </select>
                        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Computation device for training
                        </p>
                    </div>

                    <div className="form-group">
                        <label htmlFor="batch-size" className="form-label">Batch Size</label>
                        <input
                            id="batch-size"
                            type="number"
                            value={batchSize}
                            onChange={(e) => setBatchSize(parseInt(e.target.value) || 16)}
                            min="1"
                            max="256"
                            className="form-input"
                        />
                        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Number of images per batch
                        </p>
                    </div>

                    <div className="form-group">
                        <label htmlFor="image-size" className="form-label">Image Size</label>
                        <select id="image-size" value={imageSize} onChange={(e) => setImageSize(parseInt(e.target.value))} className="form-input">
                            <option value="320">320px</option>
                            <option value="416">416px</option>
                            <option value="640">640px (recommended)</option>
                            <option value="1280">1280px</option>
                        </select>
                        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Input resolution for training
                        </p>
                    </div>

                    <div className="form-group">
                        <label htmlFor="workers" className="form-label">Workers</label>
                        <input
                            id="workers"
                            type="number"
                            value={workers}
                            onChange={(e) => setWorkers(parseInt(e.target.value) || 8)}
                            min="0"
                            max="32"
                            className="form-input"
                        />
                        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-xs)' }}>
                            Number of DataLoader workers
                        </p>
                    </div>
                </div>
            </div>

            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Project Paths
                </h3>
                <dl style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Data Directory
                        </dt>
                        <dd style={{ fontFamily: 'monospace' }}>{config.paths.data}</dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Runs Directory
                        </dt>
                        <dd style={{ fontFamily: 'monospace' }}>{config.paths.runs}</dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                            Reports Directory
                        </dt>
                        <dd style={{ fontFamily: 'monospace' }}>{config.paths.reports}</dd>
                    </div>
                </dl>
            </div>

            {hasChanges && (
                <div style={{
                    display: 'flex',
                    gap: 'var(--spacing-sm)',
                    justifyContent: 'flex-end',
                    position: 'sticky',
                    bottom: 'var(--spacing-md)',
                    backgroundColor: 'var(--color-background)',
                    padding: 'var(--spacing-md)',
                    borderRadius: 'var(--border-radius-md)',
                    boxShadow: 'var(--shadow-lg)',
                }}>
                    <button onClick={handleReset} disabled={saving} className="btn btn--secondary">
                        Cancel
                    </button>
                    <button onClick={handleSave} disabled={saving} className="btn btn--primary">
                        {saving ? 'Saving...' : <><Save size={18} /> Save Changes</>}
                    </button>
                </div>
            )}
        </div>
    )
}

export default Settings