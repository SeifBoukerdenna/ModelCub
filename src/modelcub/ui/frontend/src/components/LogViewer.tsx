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

        // Epoch training progress
        const epochMatch = line.match(/\[K\s+(\d+\/\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+):\s*(\d+%)/);
        if (epochMatch) {
            const [, epoch, gpu_mem, box_loss, cls_loss, dfl_loss, instances, size, progress] = epochMatch;

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

        // Training time info
        const timeMatch = line.match(/━+\s+\d+\/\d+\s+[\d.]+it\/s\s+([\d.]+s)/);
        if (timeMatch && currentEpoch) {
            currentEpoch.time = timeMatch[1];
        }

        // Validation results
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
                            color: 'var(--color-success)',
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
                        color: 'var(--color-primary-600)',
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
                        borderRadius: 'var(--border-radius-sm)',
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
                                    backgroundColor: 'var(--color-background)',
                                    borderRadius: 'var(--border-radius-sm)',
                                    fontSize: '11px',
                                    border: '1px solid var(--color-border)'
                                }}>
                                    <div style={{ fontWeight: 600, color: 'var(--color-primary-600)' }}>{epoch.epoch}</div>
                                    <div style={{ color: 'var(--color-text-primary)' }}>{epoch.gpu_mem}</div>
                                    <div style={{ color: 'var(--color-warning)' }}>{epoch.box_loss}</div>
                                    <div style={{ color: 'var(--color-warning)' }}>{epoch.cls_loss}</div>
                                    <div style={{ color: 'var(--color-warning)' }}>{epoch.dfl_loss}</div>
                                    <div style={{ color: 'var(--color-text-primary)' }}>{epoch.instances}</div>
                                    <div style={{ color: 'var(--color-text-primary)' }}>{epoch.time || '-'}</div>
                                </div>

                                {/* Validation metrics for this epoch */}
                                {validation && (
                                    <div style={{
                                        marginTop: '4px',
                                        padding: '6px 8px',
                                        backgroundColor: 'var(--color-success-50)',
                                        borderLeft: '3px solid var(--color-success)',
                                        borderRadius: 'var(--border-radius-sm)',
                                        fontSize: '11px',
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(4, 1fr)',
                                        gap: '8px'
                                    }}>
                                        <div>
                                            <span style={{ color: 'var(--color-success-700)' }}>mAP50: </span>
                                            <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                                {(parseFloat(validation.data.map50 || '0') * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div>
                                            <span style={{ color: 'var(--color-success-700)' }}>mAP50-95: </span>
                                            <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                                {(parseFloat(validation.data.map50_95 || '0') * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div>
                                            <span style={{ color: 'var(--color-success-700)' }}>Precision: </span>
                                            <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                                {(parseFloat(validation.data.precision || '0') * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <div>
                                            <span style={{ color: 'var(--color-success-700)' }}>Recall: </span>
                                            <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>
                                                {(parseFloat(validation.data.recall || '0') * 100).toFixed(1)}%
                                            </span>
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