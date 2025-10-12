// src/modelcub/ui/frontend/src/components/Layout.tsx
import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import ProjectSwitcher from './ProjectSwitcher'
import SelectedProjectIndicator from './SelectedProjectIndicator'

const Layout: React.FC = () => {
    return (
        <div className="app">
            <Sidebar />
            <main className="main">
                {/* Clean, spacious header */}
                <header className="header">
                    <div className="header__left">
                        <ProjectSwitcher />
                        <SelectedProjectIndicator />
                    </div>
                    <div className="header__right">
                        {/* Future: notifications, user menu, etc. */}
                    </div>
                </header>

                {/* Page Content */}
                <div className="content">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}

export default Layout