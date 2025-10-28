"""Dashboard API endpoint for aggregated project statistics."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import statistics

from ..dependencies import ProjectRequired
from modelcub.core.registries import ModelRegistry

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def format_duration(ms: int | None) -> str:
    """Format milliseconds into human-readable duration."""
    if ms is None:
        return "N/A"
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    if hours > 0:
        return f"{hours}h {minutes % 60}m"
    elif minutes > 0:
        return f"{minutes}m {seconds % 60}s"
    return f"{seconds}s"


@router.get("")
def get_dashboard_data(project: ProjectRequired) -> Dict[str, Any]:
    """Get aggregated dashboard data."""
    try:
        datasets_count = len(project.datasets.list())

        try:
            model_registry = ModelRegistry(project.path)
            models_count = len(model_registry.list_models())
        except:
            models_count = 0

        all_runs = project.training.list_runs()

        status_counts = {
            'pending': 0, 'running': 0, 'completed': 0,
            'failed': 0, 'cancelled': 0
        }

        for run in all_runs:
            status = run.get('status', 'pending')
            if status in status_counts:
                status_counts[status] += 1

        recent_runs = sorted(all_runs, key=lambda x: x.get('created', ''), reverse=True)[:10]

        completed_runs = [r for r in all_runs if r.get('status') == 'completed']
        map50_values = [
            r.get('metrics', {}).get('map50')
            for r in completed_runs
            if r.get('metrics', {}).get('map50') is not None
        ]

        average_map50 = statistics.mean(map50_values) if map50_values else None
        success_rate = len(completed_runs) / len(all_runs) if all_runs else 0.0
        total_training_time = sum(r.get('duration_ms', 0) or 0 for r in completed_runs)

        best_run = None
        if map50_values:
            best = max(completed_runs, key=lambda x: x.get('metrics', {}).get('map50', 0))
            best_run = {
                'id': best['id'],
                'map50': best['metrics']['map50'],
                'datasetName': best.get('dataset_name', 'unknown'),
                'model': best.get('config', {}).get('model', 'unknown')
            }

        performance_over_time = [
            {
                'runId': r['id'][:12] + '...',
                'runIdFull': r['id'],
                'created': r.get('created', ''),
                'map50': r.get('metrics', {}).get('map50', 0),
                'map50_95': r.get('metrics', {}).get('map50_95', 0),
            }
            for r in completed_runs
            if r.get('metrics', {}).get('map50') is not None
        ]
        performance_over_time.sort(key=lambda x: x['created'])

        formatted_runs = [
            {
                'id': r['id'],
                'datasetName': r.get('dataset_name', 'unknown'),
                'model': r.get('config', {}).get('model', 'unknown'),
                'status': r.get('status', 'pending'),
                'metrics': r.get('metrics', {}),
                'config': r.get('config', {}),
                'created': r.get('created', ''),
                'duration_ms': r.get('duration_ms'),
                'duration_formatted': format_duration(r.get('duration_ms'))
            }
            for r in recent_runs
        ]

        return {
            'summary': {
                'datasets': {'count': datasets_count, 'lastModified': None},
                'models': {'count': models_count, 'latestVersion': None},
                'trainingRuns': {'total': len(all_runs), **status_counts}
            },
            'recentRuns': formatted_runs,
            'metrics': {
                'averageMap50': average_map50,
                'successRate': success_rate,
                'totalTrainingTime': total_training_time,
                'totalTrainingTimeFormatted': format_duration(total_training_time),
                'bestRun': best_run
            },
            'chartData': {
                'performanceOverTime': performance_over_time,
                'statusDistribution': status_counts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")


@router.get("/stats/quick")
def get_quick_stats(project: ProjectRequired) -> Dict[str, Any]:
    """Get quick stats for dashboard cards."""
    try:
        datasets_count = len(project.datasets.list())

        try:
            model_registry = ModelRegistry(project.path)
            models_count = len(model_registry.list_models())
        except:
            models_count = 0

        all_runs = project.training.list_runs()
        running_count = sum(1 for r in all_runs if r.get('status') == 'running')
        completed_count = sum(1 for r in all_runs if r.get('status') == 'completed')

        return {
            'datasets': datasets_count,
            'models': models_count,
            'totalRuns': len(all_runs),
            'runningRuns': running_count,
            'completedRuns': completed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quick stats: {str(e)}")