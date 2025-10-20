import { AlertTriangle, X } from 'lucide-react';
import { ReactNode } from 'react';

interface DeleteConfirmModalProps {

    title: string;
    message: ReactNode;
    onConfirm: () => void;
    onCancel: () => void;
    isDeleting: boolean;
}

const DeleteConfirmModal = ({
    title,
    message,
    onConfirm,
    onCancel,
    isDeleting
}: DeleteConfirmModalProps) => {

    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal modal--danger" onClick={(e) => e.stopPropagation()}>
                <div className="modal__header">
                    <h2 className="modal__title">
                        <AlertTriangle size={24} />
                        {title}
                    </h2>
                    <button className="modal__close" onClick={onCancel} disabled={isDeleting}>
                        <X size={20} />
                    </button>
                </div>

                <div className="modal__body">
                    <div className="alert alert--error">
                        <AlertTriangle size={20} />
                        <div>{message}</div>
                    </div>
                </div>

                <div className="modal__footer">
                    <button
                        type="button"
                        className="btn btn--secondary"
                        onClick={onCancel}
                        disabled={isDeleting}
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        className="btn btn--danger"
                        onClick={onConfirm}
                        disabled={isDeleting}
                    >
                        {isDeleting ? 'Deleting...' : 'Delete'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteConfirmModal;