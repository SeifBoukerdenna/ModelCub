import React, { useEffect } from 'react'
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
    ChevronLeft,
    ChevronRight,
} from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import { selectSelectedProject, useProjectStore } from '@/stores/projectStore'

interface NavItem {
    name: string
    href: string
    icon: LucideIcon
}

interface SidebarProps {
    isCollapsed: boolean
    onToggle: (collapsed: boolean) => void
}

const navigation: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Projects', href: '/projects', icon: FolderKanban },
    { name: 'Datasets', href: '/datasets', icon: Database },
    { name: 'Models', href: '/models', icon: Brain },
    { name: 'Settings', href: '/settings', icon: SettingsIcon },
]

const SIDEBAR_STORAGE_KEY = 'modelcub_sidebar_collapsed'

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
    const location = useLocation()
    const selectedProject = useProjectStore(selectSelectedProject)

    // Save collapsed state to localStorage when it changes
    useEffect(() => {
        try {
            localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isCollapsed))
        } catch (e) {
            console.error('Failed to save sidebar state:', e)
        }
    }, [isCollapsed])

    const toggleSidebar = () => {
        onToggle(!isCollapsed)
    }

    return (
        <aside className={`sidebar ${isCollapsed ? 'sidebar--collapsed' : ''}`}>
            {/* Logo & Title */}
            <div className="sidebar__header">
                <div className="sidebar__logo">M</div>
                {!isCollapsed && <h1 className="sidebar__title">ModelCub</h1>}
            </div>

            {/* Collapse Toggle Button */}
            <button
                onClick={toggleSidebar}
                className="sidebar__toggle"
                title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
                {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            </button>

            {/* Navigation */}
            <nav className="sidebar__nav">
                <ul className="sidebar__nav-list">
                    {navigation.map((item) => {
                        const Icon = item.icon
                        const isActive = location.pathname.startsWith(item.href)

                        return (
                            <li key={item.name} className="sidebar__nav-item">
                                <Link
                                    style={{
                                        opacity: !selectedProject ? 0.5 : 1,
                                        pointerEvents: !selectedProject ? 'none' : 'auto'
                                    }}
                                    to={item.href}
                                    className={`sidebar__nav-link ${isActive ? 'sidebar__nav-link--active' : ''
                                        }`}
                                    title={isCollapsed ? item.name : undefined}
                                >
                                    <Icon size={20} className="sidebar__nav-icon" />
                                    {!isCollapsed && <span>{item.name}</span>}
                                </Link>
                            </li>
                        )
                    })}
                </ul>
            </nav>

            {/* Footer */}
            <div className="sidebar__footer">
                {!isCollapsed && (
                    <div className="sidebar__theme">
                        <ThemeToggle />
                    </div>
                )}

                <div className="sidebar__links">
                    <a
                        href="https://github.com/seifboukerdenna/modelcub"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sidebar__link"
                        title="GitHub"
                    >
                        <Github size={18} />
                    </a>
                    <a
                        href="https://docs.modelcub.com"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sidebar__link"
                        title="Documentation"
                    >
                        <Book size={18} />
                    </a>
                </div>

                {!isCollapsed && <div className="sidebar__version">v1.0.0</div>}
            </div >
        </aside >
    )
}

export default Sidebar