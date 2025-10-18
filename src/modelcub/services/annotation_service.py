"""Annotation management commands."""
import click
import json


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

        result = save_annotation(req)
        click.echo(result.message)
        raise SystemExit(0 if result.success else result.code)

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

        result = get_annotation(req)
        click.echo(result.message)
        raise SystemExit(0 if result.success else result.code)

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

        result = delete_annotation(req)
        click.echo(result.message)
        raise SystemExit(0 if result.success else result.code)

    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@annotate.command()
@click.argument('dataset')
def stats(dataset: str):
    """Get annotation statistics for a dataset."""
    from modelcub.services.annotation_service import get_annotation_stats
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        result = get_annotation_stats(dataset, root)

        if result.success and result.data:
            stats = result.data
            click.echo(f"📊 {dataset}")
            click.echo(f"   Total: {stats['total_images']}")
            click.echo(f"   Labeled: {stats['labeled']}")
            click.echo(f"   Progress: {stats['progress']:.1%}")
            click.echo(f"   Total boxes: {stats['total_boxes']}")
            raise SystemExit(0)
        else:
            click.echo(result.message)
            raise SystemExit(result.code)

    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)


@annotate.command(name='list')
@click.argument('dataset')
def list_annotations(dataset: str):
    """List annotations in a dataset."""
    from modelcub.services.annotation_service import get_annotation, GetAnnotationRequest
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        req = GetAnnotationRequest(
            dataset_name=dataset,
            image_id=None,
            project_path=root
        )

        result = get_annotation(req)

        if result.success and result.data:
            anns = result.data.get('images', [])
            labeled = [a for a in anns if a['num_boxes'] > 0]

            click.echo(f"Labeled images in {dataset}:")
            for ann in labeled:
                click.echo(f"  {ann['image_id']}: {ann['num_boxes']} boxes")
            raise SystemExit(0)
        else:
            click.echo(result.message)
            raise SystemExit(result.code)

    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)