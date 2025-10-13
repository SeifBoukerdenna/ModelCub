import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Toast from './components/Toast'
import ProjectGuard from './guards/ProjectGuard'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Datasets from './pages/Datasets'
import Models from './pages/Models'
import Settings from './pages/Settings'

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <Toast />
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Navigate to="/dashboard" replace />} />

                    {/* Protected routes - require project selection */}
                    <Route
                        path="dashboard"
                        element={
                            <ProjectGuard>
                                <Dashboard />
                            </ProjectGuard>
                        }
                    />
                    <Route
                        path="datasets"
                        element={
                            <ProjectGuard>
                                <Datasets />
                            </ProjectGuard>
                        }
                    />
                    <Route
                        path="models"
                        element={
                            <ProjectGuard>
                                <Models />
                            </ProjectGuard>
                        }
                    />
                    <Route
                        path="settings"
                        element={
                            <ProjectGuard>
                                <Settings />
                            </ProjectGuard>
                        }
                    />

                    {/* Public routes - no guard needed */}
                    <Route path="projects" element={<Projects />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App