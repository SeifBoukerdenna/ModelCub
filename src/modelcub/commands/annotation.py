"""Annotation management commands."""
import click
import json
from pathlib import Path


@click.group()
def annotate():
    """Manage image annotations."""
    pass


@annotate.command()
@click.option('--dataset', '-d', required=True, help='Dataset name')
@click.option('--image', '-i', required=True, help='Image ID')
@click.option('--boxes', '-b', required=True, help='Boxes as JSON: [{"class_id":0,"x":0.5,"y":0.5,"w":0.2,"h":0.3},...]')
def save(dataset: str, image: str, boxes: str):
    """Save annotation for an image."""
    from modelcub.services.annotation_service import save_annotation, SaveAnnotationRequest, BoundingBox
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        boxes_data = json.loads(boxes)

        bbox_list = [
            BoundingBox(
                class_id=b['class_id'],
                x=b['x'],
                y=b['y'],
                w=b['w'],
                h=b['h']
            )
            for b in boxes_data
        ]

        req = SaveAnnotationRequest(
            dataset_name=dataset,
            image_id=image,
            boxes=bbox_list,
            project_path=root
        )

        code, msg = save_annotation(req)
        click.echo(msg)
        raise SystemExit(code)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON format: {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@annotate.command()
@click.option('--dataset', '-d', required=True, help='Dataset name')
@click.option('--image', '-i', help='Image ID (omit to get all)')
def get(dataset: str, image: str):
    """Get annotation(s) for image(s)."""
    from modelcub.services.annotation_service import get_annotation, GetAnnotationRequest
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        req = GetAnnotationRequest(
            dataset_name=dataset,
            image_id=image,
            project_path=root
        )

        code, msg = get_annotation(req)
        click.echo(msg)
        raise SystemExit(code)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@annotate.command()
@click.option('--dataset', '-d', required=True, help='Dataset name')
@click.option('--image', '-i', required=True, help='Image ID')
@click.option('--box-index', '-b', type=int, required=True, help='Box index to delete')
def delete(dataset: str, image: str, box_index: int):
    """Delete a specific box from an annotation."""
    from modelcub.services.annotation_service import delete_annotation, DeleteAnnotationRequest
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        req = DeleteAnnotationRequest(
            dataset_name=dataset,
            image_id=image,
            box_index=box_index,
            project_path=root
        )

        code, msg = delete_annotation(req)
        click.echo(msg)
        raise SystemExit(code)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@annotate.command()
@click.argument('dataset')
def stats(dataset: str):
    """Get annotation statistics for a dataset."""
    from modelcub.sdk import Project

    try:
        project = Project.load()
        ds = project.get_dataset(dataset)
        stats_data = ds.annotation_stats()

        click.echo(f"📊 {dataset}")
        click.echo(f"   Total: {stats_data['total_images']}")
        click.echo(f"   Labeled: {stats_data['labeled']}")
        click.echo(f"   Progress: {stats_data['progress']:.1%}")
        click.echo(f"   Total boxes: {stats_data['total_boxes']}")
        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)


@annotate.command(name='list')
@click.argument('dataset')
def list_annotations(dataset: str):
    """List annotations in a dataset."""
    from modelcub.sdk import Project

    try:
        project = Project.load()
        ds = project.get_dataset(dataset)
        anns = ds.get_annotations()
        labeled = [a for a in anns if a['num_boxes'] > 0]

        click.echo(f"Labeled images in {dataset}:")
        for ann in labeled:
            click.echo(f"  {ann['image_id']}: {ann['num_boxes']} boxes")
        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)


@annotate.command()
@click.argument('job_id')
def review(job_id: str):
    """Review completed job and assign images to splits."""
    from modelcub.sdk import Project
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.services.split_service import batch_move_to_splits

    try:
        project = Project.load()
        manager = AnnotationJobManager(project.path)

        # Get review data
        review_data = manager.get_job_review_data(job_id)

        click.echo(f"\n📋 Job Review: {job_id}")
        click.echo(f"   Dataset: {review_data['dataset_name']}")
        click.echo(f"   Completed: {review_data['total_completed']} images\n")

        if not review_data['items']:
            click.echo("No completed annotations to review")
            return

        # Interactive assignment
        assignments = []

        for item in review_data['items']:
            click.echo(f"Image: {item['image_id']} ({item['num_boxes']} boxes)")
            split = click.prompt(
                "  Assign to split",
                type=click.Choice(['train', 'val', 'test', 'skip']),
                default='train'
            )

            if split != 'skip':
                assignments.append({
                    "image_id": item['image_id'],
                    "split": split
                })

        if not assignments:
            click.echo("\n❌ No assignments made")
            return

        # Batch move
        click.echo(f"\n🔄 Moving {len(assignments)} images...")
        result = batch_move_to_splits(
            project.path,
            review_data['dataset_name'],
            assignments
        )

        if result.success:
            click.echo(f"✅ {result.message}")
            if result.data['failed']:
                click.echo(f"⚠️  Failed: {len(result.data['failed'])}")
        else:
            click.echo(f"❌ {result.message}")

    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)