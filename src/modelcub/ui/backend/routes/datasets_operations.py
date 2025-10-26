"""Dataset business logic operations."""
from typing import List, Optional
from pathlib import Path
import logging
import tempfile
import shutil
import zipfile
import tarfile

from fastapi import UploadFile

from modelcub.sdk import Project, Dataset
from ....core.registries import DatasetRegistry
from .datasets_utils import dataset_to_schema
from ...shared.api.schemas import (
    Dataset as DatasetSchema,
    DatasetDetail as DatasetDetailSchema,
    DatasetImages as DatasetImagesSchema,
    ImageInfo,
)

logger = logging.getLogger(__name__)


class DatasetOperations:
    """Handles dataset business logic operations."""

    @staticmethod
    def list_datasets(project: Project) -> List[DatasetSchema]:
        """List all datasets in project."""
        datasets = project.list_datasets()
        return [dataset_to_schema(ds, project.path) for ds in datasets]

    @staticmethod
    def get_dataset_detail(
        project: Project,
        dataset_name: str,
        include_images: bool = False,
        split: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> DatasetDetailSchema:
        """Get detailed dataset information."""
        dataset = project.get_dataset(dataset_name)
        split_counts = dataset.get_split_counts()
        base_schema = dataset_to_schema(dataset, project.path)

        detail = DatasetDetailSchema(
            **base_schema.model_dump(),
            train_images=split_counts.get("train", 0),
            valid_images=split_counts.get("val", 0),
            unlabeled_images=split_counts.get("unlabeled", 0),
        )

        if include_images:
            images, total = DatasetOperations.list_images(
                project, dataset_name, split, limit, offset
            )
            detail.image_list = images
            detail.total_images = total

        return detail

    @staticmethod
    def import_from_path(
        project: Project,
        source: str,
        name: Optional[str],
        classes: Optional[List[str]],
        recursive: bool,
        copy_files: bool
    ) -> DatasetSchema:
        """Import dataset from source path."""
        dataset = project.import_dataset(
            source=source,
            name=name,
            classes=classes,
            recursive=recursive,
            copy=copy_files,
            validate=True,
            force=False
        )
        return dataset_to_schema(dataset, project.path)


    @staticmethod
    def import_from_files(
        project: Project,
        files: List[UploadFile],
        name: Optional[str],
        classes: Optional[str],
        recursive: bool
    ) -> DatasetSchema:
        """Import dataset from uploaded files."""
        import tempfile
        import shutil
        import json
        from pathlib import Path

        temp_dir = Path(tempfile.mkdtemp(prefix="modelcub_upload_"))

        try:
            logger.info(f"Saved {len(files)} files to {temp_dir}")

            for upload_file in files:
                file_path = temp_dir / upload_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(upload_file.file, f)

            class_list = None
            if classes:
                class_list = [c.strip() for c in classes.split(',') if c.strip()]

            # Check if dataset exists
            dataset_exists = False
            if name:
                try:
                    existing_dataset = project.get_dataset(name)
                    dataset_exists = True
                    logger.info(f"Appending to existing dataset: {name}")
                except:
                    pass

            if dataset_exists:
                # Append to existing dataset
                dataset = project.get_dataset(name)
                dataset_dir = dataset.path / "unlabeled" / "images"
                dataset_dir.mkdir(parents=True, exist_ok=True)

                imported_count = 0
                for img_file in temp_dir.rglob("*"):
                    if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                        dest_path = dataset_dir / img_file.name
                        counter = 1
                        while dest_path.exists():
                            dest_path = dataset_dir / f"{img_file.stem}_{counter}{img_file.suffix}"
                            counter += 1
                        shutil.copy2(img_file, dest_path)
                        imported_count += 1

                # Update manifest.json
                manifest_path = dataset.path / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    manifest['images']['total'] += imported_count
                    manifest['images']['unlabeled'] += imported_count
                    with open(manifest_path, 'w') as f:
                        json.dump(manifest, f, indent=2)

                # Update registry
                from ....core.registries import DatasetRegistry
                registry = DatasetRegistry(project.path)
                registry_data = registry._load_registry()
                datasets = registry_data.get('datasets', {})

                for ds_id, ds_info in datasets.items():
                    if ds_info.get('name') == name:
                        ds_info['num_images'] = ds_info.get('num_images', 0) + imported_count
                        ds_info['images']['total'] = ds_info['images'].get('total', 0) + imported_count
                        ds_info['images']['unlabeled'] = ds_info['images'].get('unlabeled', 0) + imported_count
                        break

                registry._save_registry(registry_data)

                # Reload to get updated counts
                dataset = project.get_dataset(name)
                return dataset_to_schema(dataset, project.path)
            else:
                # Create new dataset
                dataset = project.import_dataset(
                    source=str(temp_dir),
                    name=name,
                    classes=class_list,
                    recursive=recursive,
                    copy=True,
                    validate=True,
                    force=False
                )
                return dataset_to_schema(dataset, project.path)

        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


    @staticmethod
    def import_from_archive(
        project: Project,
        file: UploadFile,
        dataset_name: Optional[str]
    ) -> DatasetSchema:
        """Import dataset from archive (zip/tar)."""
        if not file.filename or not file.filename.endswith(('.zip', '.tar.gz', '.tar')):
            raise ValueError("Invalid file type. Only .zip, .tar.gz, and .tar files are supported.")

        temp_dir = Path(tempfile.mkdtemp(prefix="modelcub_upload_"))

        try:
            # Save and extract archive
            archive_path = temp_dir / file.filename
            with open(archive_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)

            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()

            if file.filename.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif file.filename.endswith(('.tar.gz', '.tar')):
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)

            # Handle nested directory structures
            data_dir = extract_dir
            contents = list(extract_dir.iterdir())
            if len(contents) == 1 and contents[0].is_dir():
                data_dir = contents[0]

            # Generate name if needed
            if not dataset_name:
                dataset_name = Path(file.filename).stem.replace('.tar', '')

            # Import via SDK
            dataset = project.import_dataset(
                source=str(data_dir),
                name=dataset_name,
                recursive=True,
                copy=True,
                validate=True,
                force=False
            )

            return dataset_to_schema(dataset, project.path)

        finally:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory: {e}")

    @staticmethod
    def list_images(
        project: Project,
        dataset_name: str,
        split: Optional[str],
        limit: int,
        offset: int
    ) -> tuple[List[ImageInfo], int]:
        """
        List images in dataset with pagination.

        FIX: Adds 'id' field to ImageInfo objects to prevent validation errors.
        """
        from PIL import Image

        dataset = project.get_dataset(dataset_name)
        dataset_path = dataset.path

        if split:
            image_dirs = [dataset_path / split / "images"]
        else:
            image_dirs = [
                dataset_path / s / "images"
                for s in ["train", "val", "test", "unlabeled"]
            ]

        images = []
        for img_dir in image_dirs:
            if not img_dir.exists():
                continue

            split_name = img_dir.parent.name  # Get split name from parent directory
            for img_file in img_dir.glob("*.*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    label_dir = dataset_path / split_name / "labels"
                    label_file = label_dir / f"{img_file.stem}.txt"

                    # Get image dimensions
                    try:
                        with Image.open(img_file) as img:
                            width, height = img.size
                    except Exception:
                        width, height = 0, 0

                    # FIX: Add 'id' field to ImageInfo
                    images.append(ImageInfo(
                        id=img_file.stem,  # ← ADD THIS LINE (uses filename without extension as ID)
                        filename=img_file.name,
                        path=str(img_file.relative_to(dataset_path)),
                        split=split_name,
                        width=width,
                        height=height,
                        size_bytes=img_file.stat().st_size,
                        has_labels=label_file.exists()
                    ))

        total = len(images)
        images = images[offset:offset + limit]
        return images, total

    @staticmethod
    def add_class(project: Project, dataset_id: str, class_name: str) -> List[str]:
        """Add a class to dataset."""
        dataset = project.get_dataset(dataset_id)
        dataset.add_class(class_name)
        return dataset.list_classes()

    @staticmethod
    def remove_class(project: Project, dataset_id: str, class_name: str) -> List[str]:
        """Remove a class from dataset."""
        dataset = project.get_dataset(dataset_id)
        dataset.remove_class(class_name)
        return dataset.list_classes()

    @staticmethod
    def rename_class(
        project: Project,
        dataset_id: str,
        old_name: str,
        new_name: str
    ) -> List[str]:
        """Rename a class in dataset."""
        dataset = project.get_dataset(dataset_id)
        dataset.rename_class(old_name, new_name)
        return dataset.list_classes()

    @staticmethod
    def delete_dataset(project: Project, dataset_id: str) -> None:
        """Delete a dataset."""
        dataset = project.get_dataset(dataset_id)
        dataset.delete(confirm=True)