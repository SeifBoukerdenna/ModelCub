import { useEffect, useState } from 'react';
import {
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

import type { TrainingRun } from '@/lib/api/types';
import { api } from '@/lib/api';
import { useApiSync } from '@/hooks/useApiSync';

interface DashboardData {
    summary: {
        datasets: number;
        models: number;
        totalRuns: number;
        runningRuns: number;
        completedRuns: number;
        failedRuns: number;
    };
    recentRuns: TrainingRun[];
    metrics: {
        averageMap50: number | null;
        successRate: number;
        totalTrainingTime: number;
        bestRun: {
            id: string;
            map50: number;
            datasetName: string;
            model: string;
        } | null;
    };
    chartData: {
        performanceOverTime: Array<{
            runId: string;
            created: string;
            map50: number;
            map50_95: number;
        }>;
        statusCounts: Record<string, number>;
    };
}


export default function Dashboard() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useApiSync();


    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchDashboardData = async () => {
        try {
            // Fetch all required data using the API client
            const [datasets, models, allRuns] = await Promise.all([
                api.listDatasets(),
                api.listModels(),
                api.listRuns()
            ]);

            // Calculate status counts
            const statusCounts: Record<string, number> = {
                pending: 0,
                running: 0,
                completed: 0,
                failed: 0,
                cancelled: 0
            };

            allRuns.forEach(run => {
                const status = run.status || 'pending';
                statusCounts[status] = (statusCounts[status] || 0) + 1;
            });

            // Sort runs by creation date
            const sortedRuns = [...allRuns].sort((a, b) =>
                new Date(b.created || 0).getTime() - new Date(a.created || 0).getTime()
            );

            const completedRuns = allRuns.filter(r => r.status === 'completed');

            // Calculate metrics
            const map50Values = completedRuns
                .map(r => r.metrics?.map50)
                .filter((v): v is number => v !== null && v !== undefined);

            const averageMap50 = map50Values.length > 0
                ? map50Values.reduce((a, b) => a + b, 0) / map50Values.length
                : null;

            const successRate = allRuns.length > 0
                ? completedRuns.length / allRuns.length
                : 0;

            const totalTrainingTime = completedRuns.reduce(
                (sum, r) => sum + (r.duration_ms || 0),
                0
            );

            let bestRun = null;
            if (map50Values.length > 0) {
                const best = completedRuns.reduce((prev, curr) =>
                    (curr.metrics?.map50 || 0) > (prev.metrics?.map50 || 0) ? curr : prev
                );
                bestRun = {
                    id: best.id,
                    map50: best.metrics?.map50 || 0,
                    datasetName: best.dataset_name || 'unknown',
                    model: best.config?.model || 'unknown'
                };
            }

            // Performance over time chart data
            const performanceOverTime = completedRuns
                .filter(r => r.metrics?.map50 !== null && r.metrics?.map50 !== undefined)
                .map(r => ({
                    runId: r.id.slice(0, 12) + '...',
                    created: r.created || '',
                    map50: r.metrics?.map50 || 0,
                    map50_95: r.metrics?.map50_95 || 0
                }))
                .sort((a, b) => new Date(a.created).getTime() - new Date(b.created).getTime());

            setData({
                summary: {
                    datasets: datasets.length,
                    models: models.length,
                    totalRuns: allRuns.length,
                    runningRuns: statusCounts.running ?? 0,
                    completedRuns: statusCounts.completed ?? 0,
                    failedRuns: statusCounts.failed ?? 0
                },
                recentRuns: sortedRuns.slice(0, 10),
                metrics: {
                    averageMap50,
                    successRate,
                    totalTrainingTime,
                    bestRun
                },
                chartData: {
                    performanceOverTime,
                    statusCounts
                }
            });

            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-error">
                <p>Error loading dashboard: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    const formatPercent = (val: number | null) =>
        val !== null ? `${(val * 100).toFixed(1)}%` : 'N/A';

    const formatDuration = (ms: number) => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>Dashboard</h1>
                <p className="dashboard-subtitle">Project: Imfao</p>
            </div>

            {/* Summary Cards */}
            <div className="summary-cards">
                <div className="summary-card summary-card-blue">
                    <div className="summary-card-content">
                        <span className="summary-card-icon">🗄️</span>
                        <div className="summary-card-text">
                            <p className="summary-card-label">Datasets</p>
                            <p className="summary-card-value">{data.summary.datasets}</p>
                        </div>
                    </div>
                </div>

                <div className="summary-card summary-card-green">
                    <div className="summary-card-content">
                        <span className="summary-card-icon">📊</span>
                        <div className="summary-card-text">
                            <p className="summary-card-label">Models</p>
                            <p className="summary-card-value">{data.summary.models}</p>
                        </div>
                    </div>
                </div>

                <div className="summary-card summary-card-orange">
                    <div className="summary-card-content">
                        <span className="summary-card-icon">⚡</span>
                        <div className="summary-card-text">
                            <p className="summary-card-label">Training Runs</p>
                            <p className="summary-card-value">{data.summary.totalRuns}</p>
                            <p className="summary-card-subtitle">
                                {data.summary.runningRuns} running, {data.summary.completedRuns} completed
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Key Metrics */}
            {data.summary.totalRuns > 0 && (
                <div className="metrics-grid">
                    <div className="metric-card">
                        <p className="metric-label">Avg mAP50</p>
                        <p className="metric-value">{formatPercent(data.metrics.averageMap50)}</p>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">Success Rate</p>
                        <p className="metric-value">{formatPercent(data.metrics.successRate)}</p>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">Total Training Time</p>
                        <p className="metric-value">{formatDuration(data.metrics.totalTrainingTime)}</p>
                    </div>
                    <div className="metric-card">
                        <p className="metric-label">Best mAP50</p>
                        <p className="metric-value">
                            {data.metrics.bestRun ? formatPercent(data.metrics.bestRun.map50) : 'N/A'}
                        </p>
                        {data.metrics.bestRun && (
                            <p className="metric-subtitle">{data.metrics.bestRun.model}</p>
                        )}
                    </div>
                </div>
            )}

            {/* Charts */}
            {data.summary.totalRuns > 0 && (
                <div className="charts-grid">
                    <div className="chart-card">
                        <h2>Performance Over Time</h2>
                        {data.chartData.performanceOverTime.length > 0 ? (
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={data.chartData.performanceOverTime}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                    <XAxis
                                        dataKey="runId"
                                        stroke="#9ca3af"
                                        tick={{ fontSize: 11 }}
                                        angle={-45}
                                        textAnchor="end"
                                        height={80}
                                    />
                                    <YAxis stroke="#9ca3af" domain={[0, 1]} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#1f2937',
                                            border: '1px solid #374151',
                                            borderRadius: '8px'
                                        }}
                                        formatter={(value: any) => formatPercent(value)}
                                    />
                                    <Legend />
                                    <Line
                                        type="monotone"
                                        dataKey="map50"
                                        stroke="#3b82f6"
                                        name="mAP50"
                                        strokeWidth={2}
                                        dot={{ r: 4 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="map50_95"
                                        stroke="#10b981"
                                        name="mAP50-95"
                                        strokeWidth={2}
                                        dot={{ r: 4 }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="empty-state">No completed runs with metrics yet</div>
                        )}
                    </div>

                    <div className="chart-card">
                        <h2>Status Distribution</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={Object.entries(data.chartData.statusCounts)
                                        .filter(([_, value]) => value > 0)
                                        .map(([status, value]) => ({
                                            name: status.charAt(0).toUpperCase() + status.slice(1),
                                            value,
                                            status
                                        }))}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent as number * 100).toFixed(0)}%`}
                                    outerRadius={90}
                                    dataKey="value"
                                >
                                    {Object.entries(data.chartData.statusCounts)
                                        .filter(([_, value]) => value > 0)
                                        .map(([status, _], index) => (
                                            <Cell key={`cell-${index}`} fill={STATUS_COLORS[status]} />
                                        ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {/* Recent Runs Table */}
            <div className="runs-section">
                <div className="runs-header">
                    <h2>Recent Training Runs</h2>
                    {data.recentRuns.length > 0 && (
                        <a href="/runs" className="view-all-link">View All →</a>
                    )}
                </div>

                {data.recentRuns.length > 0 ? (
                    <div className="table-container">
                        <table className="runs-table">
                            <thead>
                                <tr>
                                    <th>Run ID</th>
                                    <th>Dataset</th>
                                    <th>Model</th>
                                    <th>Status</th>
                                    <th>mAP50</th>
                                    <th>mAP50-95</th>
                                    <th>Duration</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.recentRuns.map((run) => (
                                    <tr
                                        key={run.id}
                                        onClick={() => window.location.href = `/runs?runId=${run.id}`}
                                    >
                                        <td className="run-id">{run.id.slice(0, 18)}...</td>
                                        <td>{run.dataset_name}</td>
                                        <td>
                                            <code className="model-code">{run.config?.model || 'unknown'}</code>
                                        </td>
                                        <td>
                                            <StatusBadge status={run.status || 'pending'} />
                                        </td>
                                        <td className="metric-cell">
                                            {run.metrics?.map50 !== null && run.metrics?.map50 !== undefined
                                                ? formatPercent(run.metrics.map50)
                                                : '-'}
                                        </td>
                                        <td>
                                            {run.metrics?.map50_95 !== null && run.metrics?.map50_95 !== undefined
                                                ? formatPercent(run.metrics.map50_95)
                                                : '-'}
                                        </td>
                                        <td>{run.duration_ms ? formatDuration(run.duration_ms) : '-'}</td>
                                        <td className="date-cell">
                                            {new Date(run.created || '').toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>No training runs yet</p>
                        <button
                            onClick={() => window.location.href = '/datasets'}
                            className="primary-button"
                        >
                            Start Your First Training Run
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

const STATUS_COLORS: Record<string, string> = {
    completed: '#10b981',
    failed: '#ef4444',
    running: '#3b82f6',
    cancelled: '#6b7280',
    pending: '#f59e0b'
};

function StatusBadge({ status }: { status: string }) {
    return <span className={`status-badge status-${status}`}>{status}</span>;
}

