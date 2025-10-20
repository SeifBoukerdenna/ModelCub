"""Dataset utility functions."""
from pathlib import Path
import logging

from ...shared.api.schemas import Dataset as DatasetSchema, DatasetSchemaDetailed

logger = logging.getLogger(__name__)


def calculate_directory_size(path: Path) -> tuple[int, str]:
    """Calculate total size of directory."""
    total_size = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
    except Exception as e:
        logger.warning(f"Failed to calculate size for {path}: {e}")

    size_display = total_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_display < 1024:
            return total_size, f"{size_display:.1f} {unit}"
        size_display /= 1024
    return total_size, f"{size_display:.1f} TB"


def dataset_to_schema(dataset, project_path: str) -> DatasetSchemaDetailed:
    """Convert SDK Dataset to API schema."""
    info = dataset.info()
    size_bytes, size_formatted = calculate_directory_size(info.path)
    print(f"size_bytes & size_format are {size_bytes} and {size_formatted}")
    return DatasetSchemaDetailed(
        name=info.name,
        id=info.id,
        status=info.status,
        images=info.images,
        classes=info.classes,
        path=str(info.path),
        created=info.created,
        source=info.source,
        size_bytes=size_bytes,
        size_formatted=size_formatted,
    )