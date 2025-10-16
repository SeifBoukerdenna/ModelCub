import { useApiSync } from "@/hooks/useApiSync";
import { api, useGetDataset } from "@/lib/api";
import { Dataset } from "@/lib/api/types";
import { ArrowLeft, PencilLine, Play, Settings, AlertCircle } from "lucide-react";
import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ClassManagerModal from "../ClassManagerModal";

const DatasetViewer = () => {
    const { name: name_dataset } = useParams();
    useApiSync();
    const navigate = useNavigate();

    const [images, setImages] = useState<any[]>([]);
    const [page, setPage] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [creatingJob, setCreatingJob] = useState(false);
    const [jobError, setJobError] = useState<string | null>(null);

    const { data: dataset, loading, error, execute: getDataset } = useGetDataset();
    const [classManagerDataset, setClassManagerDataset] = useState<Dataset | null>(null);

    const projectPath = api.getProjectPath();
    const observerRef = useRef<IntersectionObserver | null>(null);
    const loadMoreRef = useRef<HTMLDivElement>(null);

    const PAGE_SIZE = 50;

    const handleClassUpdate = () => {
        getDataset(name_dataset ?? "");
        setClassManagerDataset(null);
    };

    const handleStartAnnotation = async () => {
        if (!name_dataset || creatingJob) return;

        try {
            setCreatingJob(true);
            setJobError(null);

            // Create job
            const job = await api.createJob({
                dataset_name: name_dataset,
                auto_start: true,
            });

            console.log('Created job:', job);

            // Navigate to annotation view with job context
            navigate(`/datasets/${name_dataset}/annotate?job_id=${job.job_id}`);
        } catch (err: any) {
            const errorMessage = err?.message || 'Failed to create annotation job';
            setJobError(errorMessage);
            console.error('Job creation error:', err);

            // Clear error after 5 seconds
            setTimeout(() => setJobError(null), 5000);
        } finally {
            setCreatingJob(false);
        }
    };

    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            // Ignore when typing in inputs/textareas/contentEditable
            const t = e.target as HTMLElement | null;
            const typing = t && (
                t.tagName === 'INPUT' ||
                t.tagName === 'TEXTAREA' ||
                t.isContentEditable
            );
            if (!typing && (e.key === 'a' || e.key === 'A')) {
                handleStartAnnotation();
            }
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [name_dataset, creatingJob]);

    const loadMore = useCallback(async () => {
        if (loading || !hasMore || !name_dataset) return;

        const result = await getDataset(name_dataset, true, undefined, PAGE_SIZE, page * PAGE_SIZE);

        if (result?.image_list) {
            setImages(prev => [...prev, ...(result.image_list ?? [])]);
            setTotalCount(result.total_images || result.image_list.length);
            setHasMore(result.image_list.length === PAGE_SIZE);
            setPage(prev => prev + 1);
        }
    }, [name_dataset, page, loading, hasMore, getDataset]);

    useEffect(() => {
        if (name_dataset) {
            setImages([]);
            setPage(0);
            setHasMore(true);
            getDataset(name_dataset, true, undefined, PAGE_SIZE, 0).then(result => {
                if (result?.image_list) {
                    setImages(result.image_list);
                    setTotalCount(result.total_images || result.image_list.length);
                    setHasMore(result.image_list.length === PAGE_SIZE);
                    setPage(1);
                }
            });
        }
    }, [name_dataset]);

    useEffect(() => {
        if (!loadMoreRef.current) return;

        observerRef.current = new IntersectionObserver(
            entries => {
                if (entries[0]?.isIntersecting && hasMore && !loading) {
                    loadMore();
                }
            },
            { threshold: 0.1 }
        );

        observerRef.current.observe(loadMoreRef.current);

        return () => observerRef.current?.disconnect();
    }, [loadMore, hasMore, loading]);

    if (error) return <div className="error">Error: {error}</div>;

    return (
        <div className="dataset-viewer">
            {/* Job Error Banner */}
            {jobError && (
                <div className="job-error-banner">
                    <AlertCircle size={16} />
                    <span>{jobError}</span>
                </div>
            )}

            <div className="dataset-header">
                <div>
                    <button
                        className="btn btn--sm btn--secondary"
                        onClick={() => navigate('/datasets')}
                        style={{ marginBottom: 'var(--spacing-sm)' }}
                    >
                        <ArrowLeft size={16} />
                        Back to Datasets
                    </button>
                    <h1>{name_dataset}</h1>
                    <p className="dataset-count">
                        {totalCount} images (loaded {images.length})
                    </p>
                </div>

                <div className="annotate-cta">
                    <button
                        className="annotate-cta__button"
                        onClick={handleStartAnnotation}
                        disabled={creatingJob}
                        title="Start annotations"
                    >
                        <Play size={16} />
                        {creatingJob ? 'Creating Job...' : 'Start Annotation'}
                    </button>
                    <div className="annotate-cta__hint">
                        <span className="annotate-cta__icon"><PencilLine size={14} /></span>
                        Hotkey: <kbd>A</kbd>
                    </div>
                </div>

                {dataset?.classes && dataset.classes.length > 0 ? (
                    <div className="classes-panel">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                            <h3 style={{ margin: 0 }}>Classes ({dataset.classes.length})</h3>
                            <button
                                className="btn btn--xs btn--secondary"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setClassManagerDataset(dataset);
                                }}
                                title="Manage classes"
                                style={{
                                    padding: '4px 8px',
                                    fontSize: 'var(--font-size-xs)'
                                }}
                            >
                                <Settings size={12} />
                                Edit
                            </button>
                        </div>
                        <div className="classes-list">
                            {dataset.classes.map((className, idx) => (
                                <span key={idx} className="class-tag">
                                    {className}
                                </span>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="classes-panel">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                            <h3 style={{ margin: 0 }}>No classes yet</h3>
                            <button
                                className="btn btn--xs btn--secondary"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setClassManagerDataset(dataset);
                                }}
                                title="Add classes"
                                style={{
                                    padding: '4px 8px',
                                    fontSize: 'var(--font-size-xs)'
                                }}
                            >
                                <Settings size={12} />
                                Add
                            </button>
                        </div>
                        <p style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
                            Click Add to create classes for this dataset
                        </p>
                    </div>
                )}
            </div>

            {/* Class Manager Modal */}
            {classManagerDataset && (
                <ClassManagerModal
                    isOpen={!!classManagerDataset}
                    onClose={() => setClassManagerDataset(null)}
                    datasetId={classManagerDataset.name}
                    initialClasses={classManagerDataset.classes}
                    onUpdate={handleClassUpdate}
                />
            )}

            <div className="image-grid">
                {images.map((img, idx) => (
                    <ImageCard
                        key={`${img.path}-${idx}`}
                        img={img}
                        datasetName={name_dataset!}
                        projectPath={projectPath}
                    />
                ))}
            </div>

            {hasMore && (
                <div ref={loadMoreRef} className="load-more">
                    {loading ? "Loading..." : ""}
                </div>
            )}
        </div>
    );
};

const ImageCard = ({ img, datasetName, projectPath }: any) => {
    const [isVisible, setIsVisible] = useState(false);
    const imgRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            entries => {
                if (entries[0]?.isIntersecting) {
                    setIsVisible(true);
                    observer.disconnect();
                }
            },
            { rootMargin: '50px' }
        );

        if (imgRef.current) observer.observe(imgRef.current);

        return () => observer.disconnect();
    }, []);

    return (
        <div ref={imgRef} className="image-card">
            <div className="image-container">
                {isVisible ? (
                    <img
                        src={`/api/v1/datasets/${datasetName}/image/${img.path}?project_path=${encodeURIComponent(projectPath || '')}`}
                        alt={img.filename}
                        loading="lazy"
                    />
                ) : (
                    <div className="image-placeholder" />
                )}
            </div>

            <span className={`label-badge ${img.has_labels ? 'labeled' : 'unlabeled'}`}>
                {img.has_labels ? '✓' : '○'}
            </span>

            <div className="image-filename">{img.filename}</div>
        </div>
    );
};

export default DatasetViewer;