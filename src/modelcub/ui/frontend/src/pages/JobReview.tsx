import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Package, TrendingUp, Target, CheckCircle2, ArrowLeft, Database } from "lucide-react";
import { api } from "@/lib/api";


interface ReviewItem {
    image_id: string;
    image_path: string;
    num_boxes: number;
    current_split: string;
}

interface SplitStats {
    train: number;
    val: number;
    test: number;
}

export default function JobReview() {
    const { jobId } = useParams<{ jobId: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [datasetName, setDatasetName] = useState("");
    const [items, setItems] = useState<ReviewItem[]>([]);
    const [assignments, setAssignments] = useState<Record<string, string>>({});
    const [submitting, setSubmitting] = useState(false);

    const [splitStats, setSplitStats] = useState<SplitStats>({ train: 0, val: 0, test: 0 });
    const [totalBoxes, setTotalBoxes] = useState(0);

    useEffect(() => {
        loadReviewData();
    }, [jobId]);

    useEffect(() => {
        // Calculate split statistics whenever assignments change
        const stats: SplitStats = { train: 0, val: 0, test: 0 };
        let boxes = 0;

        items.forEach(item => {
            const split = assignments[item.image_id] || item.current_split || "train";
            stats[split as keyof SplitStats]++;
            boxes += item.num_boxes;
        });

        setSplitStats(stats);
        setTotalBoxes(boxes);
    }, [assignments, items]);

    const loadReviewData = async () => {
        if (!jobId) return;

        try {
            const data = await api.getJobReview(jobId);
            setDatasetName(data.dataset_name);
            setItems(data.items);

            const defaultAssignments: Record<string, string> = {};
            data.items.forEach(item => {
                defaultAssignments[item.image_id] = item.current_split || "train";
            });
            setAssignments(defaultAssignments);
        } catch (error) {
            console.error("Failed to load review data:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleBulkAssign = (split: string) => {
        const newAssignments: Record<string, string> = {};
        items.forEach(item => {
            newAssignments[item.image_id] = split;
        });
        setAssignments(newAssignments);
    };

    const handleAutoSplit = () => {
        const shuffled = [...items].sort(() => Math.random() - 0.5);
        const trainCount = Math.floor(shuffled.length * 0.7);
        const valCount = Math.floor(shuffled.length * 0.2);

        const newAssignments: Record<string, string> = {};
        shuffled.forEach((item, idx) => {
            if (idx < trainCount) {
                newAssignments[item.image_id] = "train";
            } else if (idx < trainCount + valCount) {
                newAssignments[item.image_id] = "val";
            } else {
                newAssignments[item.image_id] = "test";
            }
        });
        setAssignments(newAssignments);
    };

    const handleSubmit = async () => {
        if (!jobId) return;

        setSubmitting(true);
        try {
            const assignmentList = Object.entries(assignments).map(
                ([image_id, split]) => ({ image_id, split })
            );

            const result = await api.assignSplits(jobId, assignmentList);
            alert(`✅ Assigned ${result.success.length} images successfully!`);
            navigate(`/datasets/${datasetName}`);
        } catch (error) {
            console.error("Failed to assign splits:", error);
            alert("Failed to assign splits");
        } finally {
            setSubmitting(false);
        }
    };

    const getPercentage = (count: number) => {
        return items.length > 0 ? Math.round((count / items.length) * 100) : 0;
    };

    if (loading) {
        return (
            <div className="review-container">
                <div className="review-loading">
                    <div className="review-loading__spinner"></div>
                    <p className="review-loading__text">Loading annotations...</p>
                </div>
            </div>
        );
    }

    if (items.length === 0) {
        return (
            <div className="review-container">
                <div className="review-empty">
                    <Package size={64} />
                    <h2 className="review-empty__title">No Annotations to Review</h2>
                    <p className="review-empty__description">
                        Complete some annotations first before reviewing.
                    </p>
                    <button
                        className="btn btn--primary"
                        onClick={() => navigate(`/datasets/${datasetName}`)}
                        style={{ marginTop: "var(--spacing-md)" }}
                    >
                        Back to Dataset
                    </button>
                </div>
            </div>
        );
    }

    const avgBoxesPerImage = items.length > 0 ? (totalBoxes / items.length).toFixed(1) : 0;

    return (
        <div className="review-container">
            {/* Header */}
            <div className="review-header">
                <h1 className="review-header__title">Review & Assign Splits</h1>
                <p className="review-header__subtitle">
                    <Database size={16} />
                    <span>{datasetName}</span>
                    <span className="review-header__separator">•</span>
                    <span>{items.length} images</span>
                    <span className="review-header__separator">•</span>
                    <span>{totalBoxes} annotations</span>
                </p>
            </div>

            {/* Overview Metrics */}
            <div className="metrics-overview">
                <div className="metric-card metric-card--primary">
                    <div className="metric-card__icon">
                        <Package size={24} />
                    </div>
                    <div className="metric-card__content">
                        <div className="metric-card__value">{items.length}</div>
                        <div className="metric-card__label">Total Images</div>
                    </div>
                </div>

                <div className="metric-card metric-card--success">
                    <div className="metric-card__icon">
                        <Target size={24} />
                    </div>
                    <div className="metric-card__content">
                        <div className="metric-card__value">{totalBoxes}</div>
                        <div className="metric-card__label">Total Annotations</div>
                    </div>
                </div>

                <div className="metric-card metric-card--info">
                    <div className="metric-card__icon">
                        <TrendingUp size={24} />
                    </div>
                    <div className="metric-card__content">
                        <div className="metric-card__value">{avgBoxesPerImage}</div>
                        <div className="metric-card__label">Avg per Image</div>
                    </div>
                </div>

                <div className="metric-card metric-card--accent">
                    <div className="metric-card__icon">
                        <CheckCircle2 size={24} />
                    </div>
                    <div className="metric-card__content">
                        <div className="metric-card__value">100%</div>
                        <div className="metric-card__label">Completion</div>
                    </div>
                </div>
            </div>

            {/* Split Distribution */}
            <div className="split-section">
                <h2 className="split-section__title">Split Distribution</h2>

                <div className="split-cards">
                    <div className="split-card split-card--train">
                        <div className="split-card__header">
                            <h3>Training Set</h3>
                            <div className="split-card__badge">{getPercentage(splitStats.train)}%</div>
                        </div>
                        <div className="split-card__value">{splitStats.train}</div>
                        <div className="split-card__label">images</div>
                        <div className="split-card__bar">
                            <div
                                className="split-card__progress split-card__progress--train"
                                style={{ width: `${getPercentage(splitStats.train)}%` }}
                            />
                        </div>
                    </div>

                    <div className="split-card split-card--val">
                        <div className="split-card__header">
                            <h3>Validation Set</h3>
                            <div className="split-card__badge">{getPercentage(splitStats.val)}%</div>
                        </div>
                        <div className="split-card__value">{splitStats.val}</div>
                        <div className="split-card__label">images</div>
                        <div className="split-card__bar">
                            <div
                                className="split-card__progress split-card__progress--val"
                                style={{ width: `${getPercentage(splitStats.val)}%` }}
                            />
                        </div>
                    </div>

                    <div className="split-card split-card--test">
                        <div className="split-card__header">
                            <h3>Test Set</h3>
                            <div className="split-card__badge">{getPercentage(splitStats.test)}%</div>
                        </div>
                        <div className="split-card__value">{splitStats.test}</div>
                        <div className="split-card__label">images</div>
                        <div className="split-card__bar">
                            <div
                                className="split-card__progress split-card__progress--test"
                                style={{ width: `${getPercentage(splitStats.test)}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Bulk Actions */}
            <div className="bulk-actions-section">
                <h3 className="bulk-actions-section__title">Quick Assign</h3>
                <div className="bulk-actions">
                    <button className="bulk-btn bulk-btn--train" onClick={() => handleBulkAssign("train")}>
                        All → Train
                    </button>
                    <button className="bulk-btn bulk-btn--val" onClick={() => handleBulkAssign("val")}>
                        All → Val
                    </button>
                    <button className="bulk-btn bulk-btn--test" onClick={() => handleBulkAssign("test")}>
                        All → Test
                    </button>
                    <button className="bulk-btn bulk-btn--auto" onClick={handleAutoSplit}>
                        Auto Split (70/20/10)
                    </button>
                </div>
            </div>

            {/* Action Bar */}
            <div className="review-actions">
                <div className="review-actions__info">
                    Ready to assign {items.length} image{items.length !== 1 ? "s" : ""}
                </div>
                <div className="review-actions__buttons">
                    <button
                        className="btn btn--secondary"
                        onClick={() => navigate(-1)}
                        disabled={submitting}
                    >
                        <ArrowLeft size={16} />
                        Cancel
                    </button>
                    <button
                        className="btn btn--primary"
                        onClick={handleSubmit}
                        disabled={submitting}
                    >
                        {submitting ? "Assigning..." : "Confirm & Assign Splits"}
                    </button>
                </div>
            </div>
        </div>
    );
}