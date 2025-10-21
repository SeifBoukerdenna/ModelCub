import { useEffect, useState } from 'react';
import {
    FolderOpen,
    Plus,
    RefreshCw,
    Trash2,
    Settings as SettingsIcon,
    CheckCircle,
    Calendar
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import {
    useListProjects,
    useCreateProject,
    useDeleteProject,
    type Project
} from '@/lib/api';
import { useProjectStore, selectSelectedProject } from '@/stores/projectStore';
import { toast } from '@/lib/toast';

// Components
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import CreateProjectModal from '@/components/CreateProjectModal';
import DeleteConfirmModal from '@/components/DeleteConfirmModal';

const Projects = () => {
    const navigate = useNavigate();
    const selectedProject = useProjectStore(selectSelectedProject);
    const setProjects = useProjectStore((state) => state.setProjects);
    const setSelectedProject = useProjectStore((state) => state.setSelectedProject);

    // NEW: Use API hooks
    const {
        data: projects,
        loading,
        error,
        execute: loadProjects
    } = useListProjects();

    const {
        loading: creating,
        execute: createProject
    } = useCreateProject();

    const {
        loading: deleting,
        execute: deleteProject
    } = useDeleteProject();

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

    // Load projects on mount
    useEffect(() => {
        loadProjects();
    }, []);

    // Sync projects to Zustand store
    useEffect(() => {
        if (projects) {
            setProjects(projects);
        }
    }, [projects, setProjects]);

    // Handle create project
    const handleCreateProject = async (name: string, path?: string) => {
        const result = await createProject({ name, path: path || undefined, force: false });

        if (result) {
            setShowCreateModal(false);
            toast.success(`Project "${name}" created successfully`);
            loadProjects();

            // Auto-select new project
            if (result.path) {
                setSelectedProject(result.path);
            }
        }
    };

    const handleDeleteProject = async () => {
        if (!projectToDelete) return;

        try {
            await deleteProject(projectToDelete.path, true);

            toast.success(`Project "${projectToDelete.name}" deleted`);

            // Deselect if deleted
            if (selectedProject?.path === projectToDelete.path) {
                setSelectedProject(null);
            }

            // Close modal FIRST
            setProjectToDelete(null);

            // Then reload
            await loadProjects();
        } catch (err) {
            toast.error(err instanceof Error ? err.message : 'Failed to delete project');
        }
    };

    // Handle select project
    const handleSelectProject = (project: Project) => {
        setSelectedProject(project.path);
        toast.success(`Switched to project: ${project.name}`);
    };

    // Loading state
    if (loading && !projects) {
        return <Loading message="Loading projects..." />;
    }

    // Error state
    if (error && !projects) {
        return (
            <div>
                <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                    <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700 }}>Projects</h1>
                </div>
                <ErrorMessage message={error} />
                <button
                    onClick={() => loadProjects()}
                    className="btn btn--secondary"
                    style={{ marginTop: 'var(--spacing-md)' }}
                >
                    <RefreshCw size={18} />
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 'var(--spacing-xs)'
                }}>
                    <div>
                        <h1 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>
                            Projects
                        </h1>
                        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
                            Manage your ModelCub projects
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                        <button
                            className="btn btn--secondary"
                            onClick={() => loadProjects()}
                            disabled={loading}
                        >
                            <RefreshCw size={18} className={loading ? 'spinner' : ''} />
                            Refresh
                        </button>
                        <button
                            className="btn btn--primary"
                            onClick={() => setShowCreateModal(true)}
                        >
                            <Plus size={18} />
                            New Project
                        </button>
                    </div>
                </div>
            </div>

            {/* Projects Grid */}
            {!projects || projects.length === 0 ? (
                <div className="empty-state">
                    <FolderOpen size={48} className="empty-state__icon" />
                    <h3 className="empty-state__title">No projects yet</h3>
                    <p className="empty-state__description">
                        Create your first ModelCub project to get started
                    </p>
                    <button
                        className="btn btn--primary"
                        style={{ marginTop: 'var(--spacing-lg)' }}
                        onClick={() => setShowCreateModal(true)}
                    >
                        <Plus size={20} />
                        Create Project
                    </button>
                </div>
            ) : (
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
                    gap: 'var(--spacing-lg)'
                }}>
                    {projects.map((project: Project) => (
                        <ProjectCard
                            key={project.path}
                            project={project}
                            isSelected={selectedProject?.path === project.path}
                            onSelect={() => handleSelectProject(project)}
                            onDelete={() => setProjectToDelete(project)}
                            onSettings={() => navigate('/settings')}
                        />
                    ))}
                </div>
            )}

            {/* Create Modal */}
            <CreateProjectModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onSubmit={handleCreateProject}
                isCreating={creating}
            />

            {/* Delete Confirmation Modal */}
            {projectToDelete && <DeleteConfirmModal
                title="Delete Project"
                message={
                    <>
                        Are you sure you want to delete <strong>{projectToDelete?.name}</strong>?
                        <br />
                        <span style={{ color: 'var(--color-error)' }}>
                            This action cannot be undone.
                        </span>
                    </>
                }
                onConfirm={handleDeleteProject}
                onCancel={() => setProjectToDelete(null)}
                isDeleting={deleting}
            />}
        </div>
    );
};

// Project Card Component
interface ProjectCardProps {
    project: Project;
    isSelected: boolean;
    onSelect: () => void;
    onDelete: () => void;
    onSettings: () => void;
}

const ProjectCard = ({
    project,
    isSelected,
    onSelect,
    onDelete,
    onSettings
}: ProjectCardProps) => {
    return (
        <div
            className={`card ${isSelected ? 'card--selected' : ''}`}
            style={{
                position: 'relative',
                border: isSelected ? '2px solid var(--color-primary-500)' : undefined,
                cursor: 'pointer',
            }}
            onClick={onSelect}
        >
            {/* Selected Badge */}
            {isSelected && (
                <div style={{
                    position: 'absolute',
                    top: 'var(--spacing-sm)',
                    right: 'var(--spacing-sm)',
                    backgroundColor: 'var(--color-primary-500)',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: 'var(--border-radius-sm)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                }}>
                    <CheckCircle size={12} />
                    Active
                </div>
            )}

            {/* Card Header */}
            <div className="card__header" style={{ paddingTop: isSelected ? 'var(--spacing-xl)' : undefined }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <FolderOpen size={20} style={{ color: 'var(--color-primary-500)' }} />
                    <h3 className="card__title">{project.name}</h3>
                </div>
            </div>

            {/* Card Body */}
            <div className="card__body">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                    {/* Path */}
                    <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
                        <strong>Path:</strong>
                        <div
                            style={{
                                fontFamily: 'var(--font-family-mono)',
                                backgroundColor: 'var(--color-surface)',
                                padding: 'var(--spacing-xs)',
                                borderRadius: 'var(--border-radius-sm)',
                                marginTop: '4px',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                            }}
                            title={project.path}
                        >
                            {project.path}
                        </div>
                    </div>

                    {/* Metadata */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: 'var(--spacing-sm)',
                        fontSize: 'var(--font-size-sm)',
                        paddingTop: 'var(--spacing-xs)',
                        borderTop: '1px solid var(--color-border)'
                    }}>
                        <div>
                            <div style={{ color: 'var(--color-text-secondary)' }}>Version</div>
                            <div style={{ fontWeight: 500 }}>{project.version}</div>
                        </div>
                        <div>
                            <div style={{ color: 'var(--color-text-secondary)' }}>
                                <Calendar size={12} style={{ verticalAlign: 'middle' }} /> Created
                            </div>
                            <div style={{ fontWeight: 500 }}>
                                {new Date(project.created).toLocaleDateString()}
                            </div>
                        </div>
                    </div>

                    {/* Config Info */}
                    <div style={{
                        fontSize: 'var(--font-size-xs)',
                        color: 'var(--color-text-secondary)',
                        paddingTop: 'var(--spacing-xs)',
                        borderTop: '1px solid var(--color-border)'
                    }}>
                        Device: <strong>{project.config.device}</strong> •
                        Batch: <strong>{project.config.batch_size}</strong> •
                        Image: <strong>{project.config.image_size}</strong>
                    </div>
                </div>
            </div>

            {/* Card Footer */}
            <div className="card__footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <button
                    className="btn btn--text btn--sm"
                    onClick={(e) => {
                        e.stopPropagation();
                        onSettings();
                    }}
                >
                    <SettingsIcon size={16} />
                    Settings
                </button>
                <button
                    className="btn btn--text btn--sm"
                    style={{ color: 'var(--color-error)' }}
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete();
                    }}
                >
                    <Trash2 size={16} />
                    Delete
                </button>
            </div>
        </div>
    );
};

export default Projects;