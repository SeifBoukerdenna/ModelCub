import React, { useState, useCallback, useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import ProjectSwitcher from './ProjectSwitcher'
import SelectedProjectIndicator from './SelectedProjectIndicator'
import { useRegisterHotkey } from '@/hooks/useRegisterHotkey'

const SIDEBAR_STORAGE_KEY = 'modelcub_sidebar_collapsed'
const ROOT_TIP_DISMISS_KEY = 'modelcub_root_tip_dismissed'

const Layout: React.FC = () => {
    const { pathname } = useLocation()

    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
        try {
            const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY)
            return stored === 'true'
        } catch {
            return false
        }
    })

    useEffect(() => {
        try {
            localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isSidebarCollapsed))
        } catch { }
    }, [isSidebarCollapsed])

    const toggleSidebar = useCallback(() => {
        setIsSidebarCollapsed(prev => !prev)
    }, [])

    useRegisterHotkey(
        'mod+b',
        () => { toggleSidebar() },
        { scope: 'global', preventDefault: true, enableOnForm: false, description: 'Toggle sidebar', priority: 10 }
    )

    // Show the tip only on the Projects page (path starts with /projects) and if not dismissed
    const [rootTipDismissed, setRootTipDismissed] = useState<boolean>(() => {
        try {
            return localStorage.getItem(ROOT_TIP_DISMISS_KEY) === 'true'
        } catch {
            return false
        }
    })
    const showRootTip = pathname.startsWith('/projects') && !rootTipDismissed

    const dismissRootTip = () => {
        setRootTipDismissed(true)
        try { localStorage.setItem(ROOT_TIP_DISMISS_KEY, 'true') } catch { }
    }

    return (
        <div className="app">
            <Sidebar isCollapsed={isSidebarCollapsed} onToggle={setIsSidebarCollapsed} />
            <main className={`main ${isSidebarCollapsed ? 'main--sidebar-collapsed' : ''}`}>
                <header className="header">
                    <div className="header__left">
                        <ProjectSwitcher />
                        <SelectedProjectIndicator />
                    </div>

                    <div className="header__right">
                        {showRootTip && (
                            <div
                                className="help-chip"
                                role="note"
                                aria-label="Project not found help"
                                title="Project not found? Make sure you start ModelCub UI at the root of your projects."
                            >
                                <span className="help-chip__icon" aria-hidden>ℹ️</span>
                                <span className="help-chip__text">
                                    Project not found? <strong>Make sure you start modelcub UI at the root of your projects</strong>.
                                </span>
                                <button
                                    className="help-chip__close"
                                    type="button"
                                    aria-label="Dismiss tip"
                                    onClick={dismissRootTip}
                                >
                                    ×
                                </button>
                            </div>
                        )}
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
