import type { Dataset } from '@/lib/api/types';

interface DatasetStatsProps {
    dataset: Dataset;
    totalJobs: number;
}

export const DatasetStats = ({ dataset, totalJobs }: DatasetStatsProps) => {
    return (
        <div className="stats-grid">
            <div className="stat-card">
                <div className="stat-label">Total Images</div>
                <div className="stat-value">{dataset?.images?.toLocaleString()}</div>
            </div>
            <div className="stat-card">
                <div className="stat-label">Classes</div>
                <div className="stat-value">{dataset.classes?.length || 0}</div>
            </div>
            <div className="stat-card">
                <div className="stat-label">Size</div>
                <div className="stat-value">{dataset.size_bytes}</div>
            </div>
            <div className="stat-card">
                <div className="stat-label">Number of jobs</div>
                <div className="stat-value">{totalJobs}</div>
            </div>
            <div className="stat-card">
                <div className="stat-label">Created</div>
                <div className="stat-value">
                    {dataset.created ? new Date(dataset.created).toLocaleDateString() : '-'}
                </div>
            </div>
        </div>
    );
};