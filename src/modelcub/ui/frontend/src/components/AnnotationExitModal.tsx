import { X } from "lucide-react";

interface AnnotationExitModalProps {

    onClose: () => void;
    onSuccess: () => void;
}

const AnnotationExitModal = ({ onClose, onSuccess }: AnnotationExitModalProps) => {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" style={{ maxWidth: '600px' }} onClick={(e) => e.stopPropagation()}>

                {/* Header */}
                <div className="modal__header">
                    <h2 className="modal__title">
                        Are you sure you want to exit the annotations
                    </h2>
                    <button
                        className="modal__close"
                        onClick={onClose}
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* CTA */}
                <div className="modal__body">
                    <div className="modal__message">
                        Stay and annotate?
                    </div>
                    <div className="modal__actions" style={{ display: 'flex', justifyContent: 'center' }}>
                        <button
                            className="btn btn--primary"
                            onClick={onClose}
                        >
                            Cancel
                        </button>
                        <button
                            className="btn btn--danger"
                            onClick={onSuccess}
                        >
                            Yes, Exit
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AnnotationExitModal