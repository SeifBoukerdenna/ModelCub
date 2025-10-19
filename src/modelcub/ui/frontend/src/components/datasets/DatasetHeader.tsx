import { ArrowLeft, Settings, Trash2 } from 'lucide-react';

interface DatasetHeaderProps {
    datasetName: string;
    onBack: () => void;
    onManageClasses: () => void;
    onDelete: () => void;
}

export const DatasetHeader = ({
    datasetName,
    onBack,
    onManageClasses,
    onDelete,
}: DatasetHeaderProps) => {
    return (
        <div className="dataset-header">
            <button className="btn btn--ghost" onClick={onBack}>
                <ArrowLeft size={18} />
                Back to Datasets
            </button>

            <div className="dataset-header__title">
                <h1>{datasetName}</h1>
                <div className="dataset-header__actions">
                    <button className="btn btn--secondary" onClick={onManageClasses}>
                        <Settings size={18} />
                        Manage Classes
                    </button>
                    <button className="btn btn--danger" onClick={onDelete}>
                        <Trash2 size={18} />
                        Delete
                    </button>
                </div>
            </div>
        </div>
    );
};