import React from 'react';

interface EpochData {
    epoch: string;
    gpu_mem?: string;
    box_loss?: string;
    cls_loss?: string;
    dfl_loss?: string;
    instances?: string;
    size?: string;
    time?: string;
}

interface ValidationData {
    map50?: string;
    map50_95?: string;
    precision?: string;
    recall?: string;
}

const parseTrainingLogs = (logs: string[]) => {
    const epochs: EpochData[] = [];
    const validations: { epoch: string; data: ValidationData }[] = [];
    const important: string[] = [];

    let currentEpoch: EpochData | null = null;

    for (const line of logs) {
        // Skip empty lines
        if (!line.trim()) continue;

        // Epoch training progress (e.g., "      Epoch   GPU_mem  box_loss  cls_loss  dfl_loss  Instances       Size")
        // and data lines like " [K         3/5        0G     2.516     3.565     3.004         16        640: 0%"
        const epochMatch = line.match(/\[K\s+(\d+\/\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+):\s*(\d+%)/);
        if (epochMatch) {
            const [, epoch, gpu_mem, box_loss, cls_loss, dfl_loss, instances, size, progress] = epochMatch;

            // Only add complete epochs (100%)
            if (progress === '100%' && epoch) {
                currentEpoch = {
                    epoch,
                    gpu_mem,
                    box_loss,
                    cls_loss,
                    dfl_loss,
                    instances,
                    size
                };
                epochs.push(currentEpoch);
            }
        }

        // Training time info (e.g., "━━━━━━━━━━━━━━━━ 1/1 0.31it/s 3.6s")
        const timeMatch = line.match(/━+\s+\d+\/\d+\s+[\d.]+it\/s\s+([\d.]+s)/);
        if (timeMatch && currentEpoch) {
            currentEpoch.time = timeMatch[1];
        }

        // Validation results (e.g., "                 all         2         2    0.0101         1     0.111    0.0305")
        const valMatch = line.match(/all\s+\d+\s+\d+\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)/);
        if (valMatch && currentEpoch) {
            const [, box_p, r, map50, map50_95] = valMatch;
            validations.push({
                epoch: currentEpoch.epoch,
                data: {
                    precision: box_p,
                    recall: r,
                    map50,
                    map50_95
                }
            });
        }

        // Important milestones
        if (line.includes('Starting training') ||
            line.includes('epochs completed') ||
            line.includes('Results saved to') ||
            line.includes('Optimizer stripped') ||
            line.includes('Validating')) {
            important.push(line.trim());
        }
    }

    return { epochs, validations, important };
};

const LogViewer: React.FC<{ logs: string[] }> = ({ logs }) => {
    const { epochs, validations, important } = parseTrainingLogs(logs);

    return (
        <div>
            {/* Important Messages */}
            {important.length > 0 && (
                <div style={{ marginBottom: 'var(--spacing-md)', paddingBottom: 'var(--spacing-md)', borderBottom: '1px solid var(--color-border)' }}>
                    {important.map((msg, idx) => (
                        <div key={idx} style={{
                            color: '#10b981',
                            marginBottom: '4px',
                            fontSize: '11px'
                        }}>
                            ✓ {msg}
                        </div>
                    ))}
                </div>
            )}

            {/* Epoch Progress */}
            {epochs.length > 0 ? (
                <div>
                    <div style={{
                        fontWeight: 600,
                        marginBottom: 'var(--spacing-sm)',
                        color: '#3b82f6',
                        fontSize: '13px'
                    }}>
                        Training Progress
                    </div>

                    {/* Header */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '60px 50px 70px 70px 70px 70px 50px',
                        gap: '8px',
                        padding: '8px',
                        backgroundColor: 'var(--color-surface)',
                        borderRadius: '4px',
                        marginBottom: '4px',
                        fontWeight: 600,
                        fontSize: '10px',
                        color: 'var(--color-text-secondary)',
                        border: '1px solid var(--color-border)'
                    }}>
                        <div>Epoch</div>
                        <div>GPU</div>
                        <div>Box Loss</div>
                        <div>Cls Loss</div>
                        <div>DFL Loss</div>
                        <div>Instances</div>
                        <div>Time</div>
                    </div>

                    {/* Data Rows */}
                    {epochs.map((epoch, idx) => {
                        const validation = validations.find(v => v.epoch === epoch.epoch);
                        return (
                            <div key={idx} style={{ marginBottom: '8px' }}>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: '60px 50px 70px 70px 70px 70px 50px',
                                    gap: '8px',
                                    padding: '8px',
                                    backgroundColor: 'var(--color-bg)',
                                    borderRadius: '4px',
                                    fontSize: '11px',
                                    border: '1px solid var(--color-border)'
                                }}>
                                    <div style={{ fontWeight: 600, color: '#3b82f6' }}>{epoch.epoch}</div>
                                    <div>{epoch.gpu_mem}</div>
                                    <div style={{ color: '#f59e0b' }}>{epoch.box_loss}</div>
                                    <div style={{ color: '#f59e0b' }}>{epoch.cls_loss}</div>
                                    <div style={{ color: '#f59e0b' }}>{epoch.dfl_loss}</div>
                                    <div>{epoch.instances}</div>
                                    <div>{epoch.time || '-'}</div>
                                </div>

                                {/* Validation metrics for this epoch */}
                                {validation && (
                                    <div style={{
                                        marginTop: '4px',
                                        padding: '6px 8px',
                                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                        borderLeft: '3px solid #10b981',
                                        borderRadius: '4px',
                                        fontSize: '11px',
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(4, 1fr)',
                                        gap: '8px'
                                    }}>
                                        <div>
                                            <span style={{ color: '#059669' }}>mAP50: </span>
                                            <span style={{ fontWeight: 600, color: '#10b981' }}>{(parseFloat(validation.data.map50 || '0') * 100).toFixed(1)}%</span>
                                        </div>
                                        <div>
                                            <span style={{ color: '#059669' }}>mAP50-95: </span>
                                            <span style={{ fontWeight: 600, color: '#10b981' }}>{(parseFloat(validation.data.map50_95 || '0') * 100).toFixed(1)}%</span>
                                        </div>
                                        <div>
                                            <span style={{ color: '#059669' }}>Precision: </span>
                                            <span style={{ fontWeight: 600, color: '#10b981' }}>{(parseFloat(validation.data.precision || '0') * 100).toFixed(1)}%</span>
                                        </div>
                                        <div>
                                            <span style={{ color: '#059669' }}>Recall: </span>
                                            <span style={{ fontWeight: 600, color: '#10b981' }}>{(parseFloat(validation.data.recall || '0') * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: 'var(--spacing-md)' }}>
                    No training data yet. Logs will appear once training starts.
                </div>
            )}
        </div>
    );
};

export default LogViewer;