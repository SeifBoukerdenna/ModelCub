import React from 'react'

interface LoadingProps {
    message?: string
}

const Loading: React.FC<LoadingProps> = ({ message = 'Loading...' }) => {
    return (
        <div className="loading">
            <div className="loading__spinner" />
            <span className="loading__text">{message}</span>
        </div>
    )
}

export default Loading