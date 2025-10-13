import { useEffect, useState } from 'react';
import { Database, BarChart3, FolderOpen, TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import Loading from '@/components/Loading';

const Dashboard = () => {
    const selectedProject = useProjectStore(selectSelectedProject);
    const [stats, setStats] = useState({
        datasets: 0,
        models: 0,
        runs: 0,
        totalImages: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, [selectedProject?.path]);

    const loadStats = async () => {
        if (!selectedProject) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            api.setProjectPath(selectedProject.path);

            const [datasets, models] = await Promise.all([
                api.listDatasets().catch(() => []),
                api.listModels().catch(() => []),
            ]);

            const totalImages = datasets.reduce((sum, ds) => sum + (ds.images || 0), 0);

            setStats({
                datasets: datasets.length,
                models: models.length,
                runs: 0,
                totalImages,
            });
        } catch (err) {
            console.error('Failed to load stats:', err);
        } finally {
            setLoading(false);
        }
    };

    if (!selectedProject) {
        return (
            <div>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Dashboard</h1>
                <div className="empty-state">
                    <FolderOpen size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No Project Selected</h3>
                    <p className="empty-state__description">Select a project to view dashboard</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return <Loading message="Loading dashboard..." />;
    }

    return (
        <div>
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                    Dashboard
                </h1>
                <p style={{ color: 'var(--color-text-secondary)' }}>Project: <strong>{selectedProject.name}</strong></p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-2xl)' }}>
                <StatCard icon={<Database size={24} />} label="Datasets" value={stats.datasets} color="var(--color-primary-500)" />
                <StatCard icon={<BarChart3 size={24} />} label="Models" value={stats.models} color="var(--color-success)" />
                <StatCard icon={<TrendingUp size={24} />} label="Training Runs" value={stats.runs} color="var(--color-warning)" />
            </div>

            <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                <BarChart3 size={48} style={{ margin: '0 auto', color: 'var(--color-text-secondary)' }} />
                <h3 style={{ marginTop: 'var(--spacing-lg)', marginBottom: 'var(--spacing-xs)' }}>Dashboard Coming Soon</h3>
                <p style={{ color: 'var(--color-text-secondary)' }}>Project overview and statistics will be displayed here</p>
            </div>
        </div>
    );
};

interface StatCardProps {
    icon: React.ReactNode;
    label: string;
    value: number;
    color: string;
}

const StatCard = ({ icon, label, value, color }: StatCardProps) => (
    <div className="card" style={{ padding: 'var(--spacing-xl)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
            <div style={{ color }}>{icon}</div>
            <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontWeight: 500 }}>{label}</span>
        </div>
        <div style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 700 }}>{value}</div>
    </div>
);

export default Dashboard;