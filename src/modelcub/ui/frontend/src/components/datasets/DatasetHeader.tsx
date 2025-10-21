import { ArrowLeft, Trash2 } from 'lucide-react';

interface DatasetHeaderProps {
    datasetName: string;
    onBack: () => void;

    onDelete: () => void;
}

export const DatasetHeader = ({
    datasetName,
    onBack,
    onDelete,
}: DatasetHeaderProps) => {
    return (
        <div className="dataset-header">

            <div className="dataset-header__title">
                <h1>{datasetName}</h1>
                <div className="dataset-header__actions">
                    <button className="btn btn--ghost" onClick={onBack}>
                        <ArrowLeft size={18} />
                        Back to Datasets
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