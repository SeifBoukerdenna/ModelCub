import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

const Layout: React.FC = () => {
    return (
        <div className="layout">
            <Sidebar />
            <main className="layout__main">
                <Outlet />
            </main>
        </div>
    )
}

export default Layout