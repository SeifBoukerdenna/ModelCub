import React, { useEffect, useState } from 'react'
import { Database, TrendingUp, Settings as SettingsIcon, BarChart3 } from 'lucide-react'
import { api } from '@/lib/api'
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore'
import Loading from '@/components/Loading'

const Dashboard: React.FC = () => {
    const selectedProject = useProjectStore(selectSelectedProject)
    const [stats, setStats] = useState({ datasets: 0, models: 0, runs: 0 })
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (selectedProject) {
            loadStats()
        }
    }, [selectedProject])

    const loadStats = async () => {
        if (!selectedProject) return

        try {
            setLoading(true)
            api.setCurrentProject(selectedProject.path)

            const datasetsRes = await api.listDatasets()
            const datasetCount = datasetsRes.success ? datasetsRes.datasets.length : 0

            setStats({ datasets: datasetCount, models: 0, runs: 0 })
        } catch (err) {
            console.error('Failed to load stats:', err)
        } finally {
            setLoading(false)
        }
    }

    if (!selectedProject) {
        return (
            <div className="empty-state">
                <h3 className="empty-state__title">No Project Selected</h3>
                <p className="empty-state__description">Select a project to view dashboard</p>
            </div>
        )
    }

    if (loading) return <Loading message="Loading dashboard..." />

    return (
        <div>
            <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                Dashboard
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xl)' }}>
                Project: <strong>{selectedProject.name}</strong>
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-xl)' }}>
                <div className="card">
                    <Database size={32} style={{ color: 'var(--color-primary-500)', marginBottom: 'var(--spacing-sm)' }} />
                    <h3 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                        Datasets
                    </h3>
                    <p style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 700 }}>{stats.datasets}</p>
                </div>

                <div className="card">
                    <SettingsIcon size={32} style={{ color: 'var(--color-primary-500)', marginBottom: 'var(--spacing-sm)' }} />
                    <h3 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                        Models
                    </h3>
                    <p style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 700 }}>{stats.models}</p>
                </div>

                <div className="card">
                    <TrendingUp size={32} style={{ color: 'var(--color-primary-500)', marginBottom: 'var(--spacing-sm)' }} />
                    <h3 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                        Training Runs
                    </h3>
                    <p style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 700 }}>{stats.runs}</p>
                </div>
            </div>

            <div className="empty-state">
                <BarChart3 size={48} className="empty-state__icon" />
                <h3 className="empty-state__title">Dashboard Coming Soon</h3>
                <p className="empty-state__description">Project overview and statistics will be displayed here</p>
            </div>
        </div>
    )
}

export default Dashboard