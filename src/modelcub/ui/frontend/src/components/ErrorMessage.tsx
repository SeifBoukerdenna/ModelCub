import React from 'react'

interface ErrorMessageProps {
    title?: string
    message: string
    onRetry?: () => void
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
    title = 'Error',
    message,
}) => {
    return (
        <div className="error">
            <div className="error__title">{title}</div>
            <div>{message}</div>
        </div>
    )
}

export default ErrorMessage