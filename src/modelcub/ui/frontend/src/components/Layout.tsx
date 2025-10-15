import React, { useState, useCallback, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import ProjectSwitcher from './ProjectSwitcher'
import SelectedProjectIndicator from './SelectedProjectIndicator'
import { useRegisterHotkey } from '@/hooks/useRegisterHotkey'

const SIDEBAR_STORAGE_KEY = 'modelcub_sidebar_collapsed'

const Layout: React.FC = () => {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
        try {
            const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY)
            return stored === 'true'
        } catch {
            return false
        }
    })

    // persist on change (keep your existing behavior)
    useEffect(() => {
        try {
            localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isSidebarCollapsed))
        } catch { }
    }, [isSidebarCollapsed])

    const toggleSidebar = useCallback(() => {
        setIsSidebarCollapsed(prev => !prev)
    }, [])

    // Bind "mod+b" globally (Cmd+B on mac, Ctrl+B on others)
    useRegisterHotkey("mod+b", () => {
        toggleSidebar()
    }, {
        scope: "global",
        preventDefault: true,   // stops browser "bold" in contentEditable contexts
        enableOnForm: false,    // ignore when typing in inputs/textarea by default
        description: "Toggle sidebar",
        priority: 10,
    })

    return (
        <div className="app">
            <Sidebar
                isCollapsed={isSidebarCollapsed}
                onToggle={setIsSidebarCollapsed}
            />
            <main className={`main ${isSidebarCollapsed ? 'main--sidebar-collapsed' : ''}`}>
                <header className="header">
                    <div className="header__left">
                        <ProjectSwitcher />
                        <SelectedProjectIndicator />
                    </div>
                    <div className="header__right">
                        {/* Future: notifications, user menu, etc. */}
                    </div>
                </header>

                <div className="content">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}

export default Layout
