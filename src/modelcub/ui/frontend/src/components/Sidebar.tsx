// src/modelcub/ui/frontend/src/components/Sidebar.tsx
import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    FolderKanban,
    Database,
    Brain,
    Settings as SettingsIcon,
    Github,
    Book,
    LucideIcon,
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'

interface NavItem {
    name: string
    href: string
    icon: LucideIcon
}

const navigation: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Projects', href: '/projects', icon: FolderKanban },
    { name: 'Datasets', href: '/datasets', icon: Database },
    { name: 'Models', href: '/models', icon: Brain },
    { name: 'Settings', href: '/settings', icon: SettingsIcon },
]

const Sidebar: React.FC = () => {
    const location = useLocation()

    return (
        <aside className="sidebar">
            {/* Logo & Title */}
            <div className="sidebar__header">
                <div className="sidebar__logo">M</div>
                <h1 className="sidebar__title">ModelCub</h1>
            </div>

            {/* Navigation */}
            <nav className="sidebar__nav">
                <ul className="sidebar__nav-list">
                    {navigation.map((item) => {
                        const Icon = item.icon
                        const isActive = location.pathname === item.href

                        return (
                            <li key={item.name} className="sidebar__nav-item">
                                <Link
                                    to={item.href}
                                    className={`sidebar__nav-link ${isActive ? 'sidebar__nav-link--active' : ''
                                        }`}
                                >
                                    <Icon size={20} className="sidebar__nav-icon" />
                                    <span>{item.name}</span>
                                </Link>
                            </li>
                        )
                    })}
                </ul>
            </nav>

            {/* Footer */}
            <div className="sidebar__footer">
                <div className="sidebar__theme">
                    <ThemeToggle />
                </div>

                <div className="sidebar__links">
                    <a
                        href="https://github.com/yourusername/modelcub"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sidebar__link"
                        title="GitHub"
                    >
                        <Github size={18} />
                    </a>
                    <a
                        href="https://docs.modelcub.ai"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sidebar__link"
                        title="Documentation"
                    >
                        <Book size={18} />
                    </a>
                </div>

                <div className="sidebar__version">v1.0.0</div>
            </div>
        </aside>
    )
}

export default Sidebar