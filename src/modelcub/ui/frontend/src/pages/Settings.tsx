import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save, AlertCircle, Info, RefreshCw, AlertTriangle } from 'lucide-react'
import { useProject } from '@/hooks/useProject'
import { useToast } from '@/hooks/useToast'
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
    const { project, loading: projectLoading } = useProject()
    const { showToast } = useToast()

    const [config, setConfig] = useState<ConfigData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [saving, setSaving] = useState(false)
    const [hasChanges, setHasChanges] = useState(false)

    // Form state
    const [device, setDevice] = useState('')
    const [batchSize, setBatchSize] = useState(16)
    const [imageSize, setImageSize] = useState(640)
    const [workers, setWorkers] = useState(8)

    // Load config when project changes
    useEffect(() => {
        if (project) {
            loadConfig()
        } else {
            setConfig(null)
        }
    }, [project?.path]) // Reload when project path changes

    const loadConfig = async () => {
        if (!project) return

        try {
            setLoading(true)
            setError(null)

            // Use query parameter instead of path parameter
            const response = await fetch(`/api/projects/config?path=${encodeURIComponent(project.path)}`)
            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Failed to load configuration')
            }

            if (data.success && data.config) {
                setConfig(data.config)
                // Initialize form with current values
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
        if (!project) return

        try {
            const response = await fetch(`/api/projects/config?path=${encodeURIComponent(project.path)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key, value }),
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || data.error || 'Failed to save configuration')
            }

            return data
        } catch (err) {
            throw err
        }
    }

    const handleSave = async () => {
        if (!config || !project) return

        try {
            setSaving(true)
            const updates = []

            // Save each changed value
            if (device !== config.defaults.device) {
                updates.push(saveConfig('defaults.device', device))
            }
            if (batchSize !== config.defaults.batch_size) {
                updates.push(saveConfig('defaults.batch_size', batchSize))
            }
            if (imageSize !== config.defaults.image_size) {
                updates.push(saveConfig('defaults.image_size', imageSize))
            }
            if (workers !== config.defaults.workers) {
                updates.push(saveConfig('defaults.workers', workers))
            }

            await Promise.all(updates)

            showToast('Settings saved successfully', 'success')
            setHasChanges(false)

            // Reload config to get fresh data
            await loadConfig()
        } catch (err) {
            showToast(
                err instanceof Error ? err.message : 'Failed to save settings',
                'error'
            )
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

    // Track changes
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

    if (projectLoading) {
        return <Loading text="Loading projects..." />
    }

    // No project selected - show prominent message
    if (!project) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                        Settings
                    </h1>
                    <p style={{ color: 'var(--color-gray-600)' }}>
                        Configure your project defaults and paths
                    </p>
                </div>

                <div className="empty-state">
                    <AlertTriangle size={48} className="empty-state__icon" style={{ color: 'var(--color-warning)' }} />
                    <h3 className="empty-state__title">No Project Selected</h3>
                    <p className="empty-state__description">
                        Please select a project using the project switcher above to view and edit its settings.
                    </p>
                </div>
            </div>
        )
    }

    if (loading) {
        return <Loading text={`Loading settings for ${project.name}...`} />
    }

    if (error) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                        Settings
                    </h1>
                    <p style={{ color: 'var(--color-gray-600)' }}>
                        Configure settings for <strong>{project.name}</strong>
                    </p>
                </div>
                <ErrorMessage message={error} />
                <div style={{ marginTop: 'var(--spacing-md)', textAlign: 'center' }}>
                    <button onClick={loadConfig} className="btn btn--secondary">
                        <RefreshCw size={18} style={{ marginRight: 'var(--spacing-xs)' }} />
                        Retry
                    </button>
                </div>
            </div>
        )
    }

    if (!config) {
        return <Loading text="Loading configuration..." />
    }

    return (
        <div style={{ maxWidth: '800px' }}>
            {/* Header with current project indicator */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    Settings
                </h1>
                <p style={{ color: 'var(--color-gray-600)', marginBottom: 'var(--spacing-md)' }}>
                    Configure your project defaults and paths
                </p>

                {/* Current Project Indicator */}
                <div
                    style={{
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        backgroundColor: 'var(--color-blue-50)',
                        border: '2px solid var(--color-primary)',
                        borderRadius: 'var(--radius-md)',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-xs)',
                    }}
                >
                    <SettingsIcon size={16} style={{ color: 'var(--color-primary)' }} />
                    <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-primary)' }}>
                        Editing: {config.project.name}
                    </span>
                </div>
            </div>

            {/* Warning Banner */}
            <div
                className="card"
                style={{
                    marginBottom: 'var(--spacing-lg)',
                    padding: 'var(--spacing-md)',
                    backgroundColor: 'var(--color-warning-bg)',
                    borderLeft: '4px solid var(--color-warning)',
                }}
            >
                <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                    <AlertCircle size={20} style={{ color: 'var(--color-warning)', flexShrink: 0, marginTop: '2px' }} />
                    <div>
                        <h4 style={{ fontWeight: 600, marginBottom: 'var(--spacing-xs)', color: 'var(--color-warning)' }}>
                            Do Not Edit Config Files Directly
                        </h4>
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-700)', lineHeight: 1.5 }}>
                            Never manually edit <code style={{
                                backgroundColor: 'var(--color-gray-100)',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontFamily: 'monospace'
                            }}>.modelcub/config.yaml</code> directly.
                            Always use this UI, the CLI (<code style={{
                                backgroundColor: 'var(--color-gray-100)',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontFamily: 'monospace'
                            }}>modelcub project config set</code>),
                            or the Python SDK to modify configuration. Manual edits may cause data corruption.
                        </p>
                    </div>
                </div>
            </div>

            {/* Project Info (Read-only) */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Project Information
                </h3>
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)', alignItems: 'center' }}>
                    <Info size={16} style={{ color: 'var(--color-blue-500)' }} />
                    <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        These fields are immutable and cannot be changed
                    </span>
                </div>
                <dl style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Project Name
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)' }}>
                            {config.project.name}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Project Path
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-900)', fontFamily: 'monospace', wordBreak: 'break-all' }}>
                            {project.path}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Created
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)' }}>
                            {new Date(config.project.created).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                            })}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Version
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)' }}>
                            {config.project.version}
                        </dd>
                    </div>
                </dl>
            </div>

            {/* Default Settings (Editable) */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Default Settings
                </h3>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)', marginBottom: 'var(--spacing-lg)' }}>
                    Configure default values for training and inference
                </p>

                <div style={{ display: 'grid', gap: 'var(--spacing-lg)' }}>
                    {/* Device */}
                    <div>
                        <label
                            htmlFor="device"
                            style={{
                                display: 'block',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                                marginBottom: 'var(--spacing-xs)',
                                color: 'var(--color-gray-700)',
                            }}
                        >
                            Device
                        </label>
                        <select
                            id="device"
                            value={device}
                            onChange={(e) => setDevice(e.target.value)}
                            className="input"
                            style={{ width: '100%' }}
                        >
                            <option value="cuda">CUDA (GPU)</option>
                            <option value="mps">MPS (Apple Silicon)</option>
                            <option value="cpu">CPU</option>
                        </select>
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', marginTop: 'var(--spacing-xs)' }}>
                            Computation device for training and inference
                        </p>
                    </div>

                    {/* Batch Size */}
                    <div>
                        <label
                            htmlFor="batch-size"
                            style={{
                                display: 'block',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                                marginBottom: 'var(--spacing-xs)',
                                color: 'var(--color-gray-700)',
                            }}
                        >
                            Batch Size
                        </label>
                        <input
                            id="batch-size"
                            type="number"
                            value={batchSize}
                            onChange={(e) => setBatchSize(parseInt(e.target.value) || 16)}
                            min="1"
                            max="256"
                            className="input"
                            style={{ width: '100%' }}
                        />
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', marginTop: 'var(--spacing-xs)' }}>
                            Number of images per training batch (typically 8, 16, or 32)
                        </p>
                    </div>

                    {/* Image Size */}
                    <div>
                        <label
                            htmlFor="image-size"
                            style={{
                                display: 'block',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                                marginBottom: 'var(--spacing-xs)',
                                color: 'var(--color-gray-700)',
                            }}
                        >
                            Image Size
                        </label>
                        <select
                            id="image-size"
                            value={imageSize}
                            onChange={(e) => setImageSize(parseInt(e.target.value))}
                            className="input"
                            style={{ width: '100%' }}
                        >
                            <option value="320">320px</option>
                            <option value="416">416px</option>
                            <option value="640">640px (recommended)</option>
                            <option value="1280">1280px</option>
                        </select>
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', marginTop: 'var(--spacing-xs)' }}>
                            Input image resolution for training (higher = slower but more accurate)
                        </p>
                    </div>

                    {/* Workers */}
                    <div>
                        <label
                            htmlFor="workers"
                            style={{
                                display: 'block',
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: 500,
                                marginBottom: 'var(--spacing-xs)',
                                color: 'var(--color-gray-700)',
                            }}
                        >
                            Workers
                        </label>
                        <input
                            id="workers"
                            type="number"
                            value={workers}
                            onChange={(e) => setWorkers(parseInt(e.target.value) || 8)}
                            min="0"
                            max="32"
                            className="input"
                            style={{ width: '100%' }}
                        />
                        <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', marginTop: 'var(--spacing-xs)' }}>
                            Number of DataLoader worker processes (0 = use main process)
                        </p>
                    </div>
                </div>
            </div>

            {/* Paths (Read-only for now) */}
            <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>
                    Project Paths
                </h3>
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)', alignItems: 'center' }}>
                    <Info size={16} style={{ color: 'var(--color-blue-500)' }} />
                    <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-600)' }}>
                        Directory paths relative to project root
                    </span>
                </div>
                <dl style={{ display: 'grid', gap: 'var(--spacing-md)' }}>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Data Directory
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)', fontFamily: 'monospace' }}>
                            {config.paths.data}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Runs Directory
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)', fontFamily: 'monospace' }}>
                            {config.paths.runs}
                        </dd>
                    </div>
                    <div>
                        <dt style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-gray-500)', fontWeight: 500, marginBottom: 'var(--spacing-xs)' }}>
                            Reports Directory
                        </dt>
                        <dd style={{ fontSize: 'var(--font-size-base)', color: 'var(--color-gray-900)', fontFamily: 'monospace' }}>
                            {config.paths.reports}
                        </dd>
                    </div>
                </dl>
            </div>

            {/* Action Buttons */}
            {hasChanges && (
                <div
                    style={{
                        display: 'flex',
                        gap: 'var(--spacing-sm)',
                        justifyContent: 'flex-end',
                        position: 'sticky',
                        bottom: 'var(--spacing-md)',
                        backgroundColor: 'var(--color-bg)',
                        padding: 'var(--spacing-md)',
                        borderRadius: 'var(--radius-md)',
                        boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.1)',
                    }}
                >
                    <button
                        onClick={handleReset}
                        disabled={saving}
                        className="btn btn--secondary"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="btn btn--primary"
                        style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}
                    >
                        {saving ? (
                            <>
                                <div className="spinner" style={{ width: '16px', height: '16px' }} />
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
            )}
        </div>
    )
}

export default Settings