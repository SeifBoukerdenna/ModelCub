import React from 'react'

interface LoadingProps {
    text?: string
}

const Loading: React.FC<LoadingProps> = ({ text = 'Loading...' }) => {
    return (
        <div className="loading">
            <div className="loading__spinner" />
            <span className="loading__text">{text}</span>
        </div>
    )
}

export default Loading