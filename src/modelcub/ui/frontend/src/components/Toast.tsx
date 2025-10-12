// src/modelcub/ui/frontend/src/components/Toast.tsx
import React, { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info' | 'warning'

interface ToastData {
    id: string
    message: string
    type: ToastType
    duration: number
}

const Toast: React.FC = () => {
    const [toasts, setToasts] = useState<ToastData[]>([])

    useEffect(() => {
        const handleShowToast = (event: CustomEvent) => {
            const { message, type, duration } = event.detail
            const id = Math.random().toString(36).substring(7)

            const newToast: ToastData = {
                id,
                message,
                type: type || 'info',
                duration: duration || 3000,
            }

            setToasts((prev) => [...prev, newToast])

            // Auto-remove after duration
            setTimeout(() => {
                setToasts((prev) => prev.filter((t) => t.id !== id))
            }, newToast.duration)
        }

        window.addEventListener('show-toast', handleShowToast as EventListener)
        return () => {
            window.removeEventListener('show-toast', handleShowToast as EventListener)
        }
    }, [])

    const removeToast = (id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
    }

    const getIcon = (type: ToastType) => {
        switch (type) {
            case 'success':
                return <CheckCircle size={20} />
            case 'error':
                return <XCircle size={20} />
            case 'warning':
                return <AlertTriangle size={20} />
            case 'info':
            default:
                return <Info size={20} />
        }
    }

    const getStyles = (type: ToastType) => {
        const baseStyles = {
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 'var(--spacing-sm)',
            minWidth: '300px',
            maxWidth: '500px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            animation: 'slideIn 0.3s ease-out',
            position: 'relative' as const,
        }

        const typeStyles = {
            success: {
                backgroundColor: 'var(--color-success)',
                color: 'white',
            },
            error: {
                backgroundColor: 'var(--color-error)',
                color: 'white',
            },
            warning: {
                backgroundColor: 'var(--color-warning)',
                color: 'white',
            },
            info: {
                backgroundColor: 'var(--color-primary)',
                color: 'white',
            },
        }

        return { ...baseStyles, ...typeStyles[type] }
    }

    if (toasts.length === 0) return null

    return (
        <>
            <style>{`
                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `}</style>
            <div
                style={{
                    position: 'fixed',
                    top: 'var(--spacing-lg)',
                    right: 'var(--spacing-lg)',
                    zIndex: 9999,
                }}
            >
                {toasts.map((toast) => (
                    <div key={toast.id} style={getStyles(toast.type)}>
                        <div style={{ flexShrink: 0 }}>{getIcon(toast.type)}</div>
                        <div style={{ flex: 1, fontSize: 'var(--font-size-sm)' }}>
                            {toast.message}
                        </div>
                        <button
                            onClick={() => removeToast(toast.id)}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'inherit',
                                cursor: 'pointer',
                                padding: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                opacity: 0.8,
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
                            onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.8')}
                        >
                            <X size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </>
    )
}

export default Toast