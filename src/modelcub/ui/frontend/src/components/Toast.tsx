import React, { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { toast, Toast as ToastType } from '@/lib/toast'

const Toast: React.FC = () => {
    const [toasts, setToasts] = useState<ToastType[]>([])

    useEffect(() => {
        const unsubscribe = toast.subscribe(setToasts)
        return unsubscribe
    }, [])

    if (toasts.length === 0) return null

    return (
        <div className="toast-container">
            {toasts.map((t) => (
                <div key={t.id} className={`toast toast--${t.type}`}>
                    <div className="toast__content">
                        <span className="toast__message">{t.message}</span>
                        <button
                            className="toast__close"
                            onClick={() => toast.dismiss(t.id)}
                            aria-label="Close"
                        >
                            <X size={16} />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default Toast