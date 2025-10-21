import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";

interface ReviewItem {
    image_id: string;
    image_path: string;
    num_boxes: number;
    current_split: string;
}

export default function JobReview() {
    const { jobId } = useParams<{ jobId: string }>();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [datasetName, setDatasetName] = useState("");
    const [items, setItems] = useState<ReviewItem[]>([]);
    const [assignments, setAssignments] = useState<Record<string, string>>({});
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadReviewData();
    }, [jobId]);

    const loadReviewData = async () => {
        if (!jobId) return;

        try {
            const data = await api.getJobReview(jobId);
            setDatasetName(data.dataset_name);
            setItems(data.items);

            const defaultAssignments: Record<string, string> = {};
            data.items.forEach(item => {
                defaultAssignments[item.image_id] = "train";
            });
            setAssignments(defaultAssignments);
        } catch (error) {
            console.error("Failed to load review data:", error);
        } finally {
            setLoading(false);
        }
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

    if (loading) return <div style={{ padding: "2rem" }}>Loading...</div>;

    return (
        <div style={{ padding: "2rem", maxWidth: "72rem", margin: "0 auto" }}>
            <div style={{ marginBottom: "1.5rem" }}>
                <h1 style={{ fontSize: "1.875rem", fontWeight: "bold", marginBottom: "0.5rem" }}>
                    Review Annotations
                </h1>
                <p style={{ color: "#6b7280" }}>
                    Dataset: {datasetName} • {items.length} images
                </p>
            </div>

            <div style={{ marginBottom: "1.5rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <span style={{ fontSize: "0.875rem", color: "#6b7280" }}>Bulk assign:</span>
                <button
                    className="button-secondary"
                    onClick={() => {
                        const newAssignments: Record<string, string> = {};
                        items.forEach(item => { newAssignments[item.image_id] = "train"; });
                        setAssignments(newAssignments);
                    }}
                >
                    All → Train
                </button>
                <button
                    className="button-secondary"
                    onClick={() => {
                        const newAssignments: Record<string, string> = {};
                        items.forEach(item => { newAssignments[item.image_id] = "val"; });
                        setAssignments(newAssignments);
                    }}
                >
                    All → Val
                </button>
                <button
                    className="button-secondary"
                    onClick={() => {
                        const newAssignments: Record<string, string> = {};
                        items.forEach(item => { newAssignments[item.image_id] = "test"; });
                        setAssignments(newAssignments);
                    }}
                >
                    All → Test
                </button>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
                {items.map((item) => (
                    <div
                        key={item.image_id}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "1rem",
                            padding: "1rem",
                            border: "1px solid #e5e7eb",
                            borderRadius: "0.5rem",
                            marginBottom: "0.75rem"
                        }}
                    >
                        <img
                            src={`/api/v1/datasets/${datasetName}/image/${item.image_path}?project_path=${encodeURIComponent(
                                api.getProjectPath() || ""
                            )}`}
                            alt={item.image_id}
                            style={{
                                width: "5rem",
                                height: "5rem",
                                objectFit: "cover",
                                borderRadius: "0.25rem"
                            }}
                        />

                        <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: "500" }}>{item.image_id}</div>
                            <div style={{ fontSize: "0.875rem", color: "#6b7280" }}>
                                {item.num_boxes} annotation{item.num_boxes !== 1 ? "s" : ""}
                            </div>
                        </div>

                        <select
                            value={assignments[item.image_id]}
                            onChange={(e) => setAssignments(prev => ({
                                ...prev,
                                [item.image_id]: e.target.value
                            }))}
                            style={{
                                width: "8rem",
                                padding: "0.5rem",
                                border: "1px solid #d1d5db",
                                borderRadius: "0.375rem",
                                backgroundColor: "white"
                            }}
                        >
                            <option value="train">Train</option>
                            <option value="val">Val</option>
                            <option value="test">Test</option>
                        </select>
                    </div>
                ))}
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
                <button className="button-secondary" onClick={() => navigate(-1)}>
                    Cancel
                </button>
                <button className="button-primary" onClick={handleSubmit} disabled={submitting}>
                    {submitting ? "Assigning..." : "Assign Splits"}
                </button>
            </div>
        </div>
    );
}