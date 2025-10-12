import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Toast from './components/Toast'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Datasets from './pages/Datasets'
import Models from './pages/Models'

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <Toast />
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="projects" element={<Projects />} />
                    <Route path="datasets" element={<Datasets />} />
                    <Route path="models" element={<Models />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App