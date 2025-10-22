import React, { useEffect } from 'react'
import { useProjectStore } from '@/stores/projectStore'
import { api } from '@/lib/api' // Import the api instance
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Toast from './components/Toast'
import ProjectGuard from './guards/ProjectGuard'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Datasets from './pages/Datasets'
import Models from './pages/Models'
import Settings from './pages/Settings'
import { HotkeysProvider } from './hotkeys/HotkeysProvider'

import { AnnotationView } from './components/AnnotationViewer'
import DatasetViewer from './components/datasets/DatasetViewer'
import JobReview from './pages/JobReview'

const App: React.FC = () => {
    useEffect(() => {
        const loadProjects = async () => {
            useProjectStore.getState().setLoading(true)
            try {
                const projects = await api.listProjects()
                useProjectStore.getState().setProjects(projects)
            } catch (error) {
                useProjectStore.getState().setError('Failed to load projects')
            } finally {
                useProjectStore.getState().setLoading(false)
            }
        }

        loadProjects()
    }, [])

    return (
        <BrowserRouter>
            <HotkeysProvider>
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
                            path="datasets/:name"
                            element={
                                <ProjectGuard>
                                    <DatasetViewer />
                                </ProjectGuard>
                            }
                        />

                        <Route path="/datasets/:name/annotate" element={
                            <ProjectGuard>
                                <AnnotationView />
                            </ProjectGuard>
                        }
                        />

                        <Route path="/jobs/:jobId/review" element={
                            <ProjectGuard>
                                <JobReview />
                            </ProjectGuard>}
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
            </HotkeysProvider>
        </BrowserRouter>
    )
}

export default App