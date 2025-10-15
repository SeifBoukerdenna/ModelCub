import { Dataset } from "@/lib/api/types";
import { CheckCircle, Database, Settings, Trash2 } from "lucide-react";

// Dataset Card Component
interface DatasetCardProps {
    dataset: Dataset;
    onClick: () => void;
    onManageClasses: (e: React.MouseEvent) => void;
    onDelete: (e: React.MouseEvent) => void;
}

const DatasetCard = ({ dataset, onClick, onManageClasses, onDelete }: DatasetCardProps) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ready':
                return {
                    bg: 'var(--color-success-100)',
                    text: 'var(--color-success-700)'
                };
            case 'processing':
                return {
                    bg: 'var(--color-warning-100)',
                    text: 'var(--color-warning-700)'
                };
            default:
                return {
                    bg: 'var(--color-gray-100)',
                    text: 'var(--color-gray-700)'
                };
        }
    };

    const statusColor = getStatusColor(dataset.status);

    return (
        <div
            className="card"
            onClick={onClick}
            style={{
                cursor: 'pointer',
                transition: 'all 0.2s ease',
            }}
        >
            {/* Card Header */}
            <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                marginBottom: 'var(--spacing-md)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <Database size={20} style={{ color: 'var(--color-primary-500)' }} />
                    <h3 style={{
                        fontSize: 'var(--font-size-lg)',
                        fontWeight: 600,
                        color: 'var(--color-text-primary)',
                        margin: 0
                    }}>
                        {dataset.name}
                    </h3>
                </div>
                <span
                    className="badge"
                    style={{
                        backgroundColor: statusColor.bg,
                        color: statusColor.text,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 'var(--spacing-xs)'
                    }}
                >
                    <CheckCircle size={14} />
                    {dataset.status}
                </span>
            </div>

            {/* Card Body */}
            <div>
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 'var(--spacing-xs)',
                    marginBottom: 'var(--spacing-md)'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)'
                    }}>
                        <span>Images:</span>
                        <strong style={{ color: 'var(--color-text-primary)' }}>
                            {dataset.size_formatted}
                        </strong>
                    </div>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--color-text-secondary)'
                    }}>
                        <span>Size:</span>
                        <strong style={{ color: 'var(--color-text-primary)' }}>
                            {dataset.size_formatted}
                        </strong>
                    </div>
                </div>

                {/* Classes */}
                {(
                    <div style={{ marginTop: 'var(--spacing-md)' }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            marginBottom: 'var(--spacing-xs)'
                        }}>
                            <div style={{
                                fontSize: 'var(--font-size-xs)',
                                fontWeight: 500,
                                color: 'var(--color-text-secondary)'
                            }}>
                                {dataset.classes && dataset.classes.length > 0 &&
                                    <>
                                        Classes:
                                    </>
                                }
                            </div>
                            <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                                <button
                                    className="btn btn--xs btn--secondary"
                                    onClick={onManageClasses}
                                    title="Manage classes"
                                    style={{
                                        padding: '4px 8px',
                                        fontSize: 'var(--font-size-xs)'
                                    }}
                                >
                                    <Settings size={12} />
                                    Edit
                                </button>
                                <button
                                    className="btn btn--xs btn--danger"
                                    onClick={onDelete}
                                    title="Delete dataset"
                                    style={{ padding: '4px 8px', fontSize: 'var(--font-size-xs)' }}
                                >
                                    <Trash2 size={12} />
                                </button>
                            </div>
                        </div>
                        <div className="classes-list">
                            {dataset.classes && dataset.classes.length > 0 && dataset.classes.slice(0, 5).map((cls, idx) => (
                                <span key={`${cls}-${idx}`} className="class-badge">
                                    {cls}
                                </span>
                            ))}
                            {dataset.classes.length > 5 && (
                                <span className="badge badge--gray">
                                    +{dataset.classes.length - 5} more
                                </span>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DatasetCard;