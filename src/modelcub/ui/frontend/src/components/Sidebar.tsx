import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    FolderKanban,
    Database,
    Brain,
    ExternalLink,
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
]

const Sidebar: React.FC = () => {
    const location = useLocation()

    return (
        <>
            <aside className="sidebar">
                <div className="sidebar__header">
                    <div className="sidebar__logo">M</div>
                    <h1 className="sidebar__title">ModelCub</h1>
                </div>

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
                                        {item.name}
                                    </Link>
                                </li>
                            )
                        })}
                    </ul>
                </nav>

                <div className="sidebar__footer">
                    <div style={{ marginBottom: 'var(--spacing-md)' }}>
                        <ThemeToggle />
                    </div>

                    <div className="sidebar__links">
                        <a
                            href="https://docs.modelcub.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="sidebar__link"
                            title="Documentation"
                        >
                            <Book size={16} />
                            <span>Docs</span>
                            <ExternalLink size={12} className="sidebar__link-icon" />
                        </a>
                        <a
                            href="https://github.com/seifboukerdenna/modelcub"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="sidebar__link"
                            title="GitHub Repository"
                        >
                            <Github size={16} />
                            <span>GitHub</span>
                            <ExternalLink size={12} className="sidebar__link-icon" />
                        </a>
                    </div>
                    <p className="sidebar__footer-text">ModelCub v1.0.0</p>
                </div>
            </aside>
        </>
    )
}

export default Sidebar