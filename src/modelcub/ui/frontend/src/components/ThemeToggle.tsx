import React from 'react'
import { Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

const ThemeToggle: React.FC = () => {
    const { theme, toggleTheme } = useTheme()

    const getIcon = () => {
        switch (theme) {
            case 'light':
                return <Sun size={16} />
            case 'dark':
                return <Moon size={16} />
            case 'system':
                return <Monitor size={16} />
        }
    }

    const getLabel = () => {
        switch (theme) {
            case 'light':
                return 'Light'
            case 'dark':
                return 'Dark'
            case 'system':
                return 'System'
        }
    }

    return (
        <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Theme: ${getLabel()} (click to cycle)`}
            aria-label="Toggle theme"
        >
            <span className="theme-toggle__icon">{getIcon()}</span>
            <span className="theme-toggle__label">{getLabel()}</span>
        </button>
    )
}

export default ThemeToggle