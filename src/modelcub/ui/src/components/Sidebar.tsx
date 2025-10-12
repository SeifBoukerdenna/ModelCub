import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FolderKanban, Database, Brain, LucideIcon } from 'lucide-react'

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
                <p className="sidebar__footer-text">ModelCub v1.0.0</p>
            </div>
        </aside>
    )
}

export default Sidebar