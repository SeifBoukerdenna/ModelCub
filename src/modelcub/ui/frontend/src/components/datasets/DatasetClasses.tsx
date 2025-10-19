import { Settings } from 'lucide-react';

interface DatasetClassesProps {
    classes: string[];
    onManage: () => void;
}

export const DatasetClasses = ({ classes, onManage }: DatasetClassesProps) => {
    return (
        <div className="dataset-section">
            <div className="section-header">
                <h3>Classes</h3>
                <button className="btn btn--sm btn--secondary" onClick={onManage}>
                    <Settings size={16} />
                    Manage
                </button>
            </div>
            {classes && classes.length > 0 ? (
                <div className="classes-list">
                    {classes.map((cls, idx) => (
                        <span key={idx} className="class-badge">{cls}</span>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <p>No classes defined yet</p>
                    <button className="btn btn--sm btn--primary" onClick={onManage}>
                        Add Classes
                    </button>
                </div>
            )}
        </div>
    );
};