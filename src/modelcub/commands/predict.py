"""
Inference/prediction commands for ModelCub CLI.
"""

import click
from pathlib import Path
from typing import Optional, List


@click.group()
def predict():
    """Run inference on images, videos, or datasets."""
    pass


@predict.command()
@click.argument('image_path')
@click.option('--model', '-m', required=True, help='Model name, run ID, or path')
@click.option('--conf', default=0.25, type=float, help='Confidence threshold (0-1)')
@click.option('--iou', default=0.45, type=float, help='IoU threshold for NMS (0-1)')
@click.option('--device', default='cpu', help='Device (cpu, cuda, cuda:0, mps)')
@click.option('--save-txt/--no-save-txt', default=True, help='Save YOLO labels')
@click.option('--save-img/--no-save-img', default=False, help='Save annotated images')
@click.option('--classes', help='Filter classes (comma-separated IDs)')
@click.option('--output', '-o', help='Custom output directory')
def image(
    image_path: str,
    model: str,
    conf: float,
    iou: float,
    device: str,
    save_txt: bool,
    save_img: bool,
    classes: Optional[str],
    output: Optional[str]
):
    """
    Run inference on a single image.

    Examples:
        modelcub predict image test.jpg --model run-20251027-143022
        modelcub predict image test.jpg --model detector-v1 --conf 0.5
        modelcub predict image test.jpg -m models/best.pt --save-img
    """
    from modelcub.services.inference import InferenceService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = InferenceService(root)

        # Parse classes
        class_list = None
        if classes:
            class_list = [int(c.strip()) for c in classes.split(',')]

        click.echo(f"🔍 Running inference on: {image_path}")
        click.echo(f"   Model: {model}")

        # Create and run inference job
        inference_id = service.create_inference_job(
            model_identifier=model,
            input_type='image',
            input_path=image_path,
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            classes=class_list
        )

        # Progress callback
        def progress(current, total, message):
            if current == 0:
                click.echo(f"   {message}")

        stats = service.run_inference(inference_id, progress_callback=progress)

        click.echo()
        click.echo(f"✅ Inference complete!")
        click.echo(f"   Detections: {stats['total_detections']}")
        click.echo(f"   Time: {stats['avg_inference_time_ms']:.1f}ms")

        job = service.inference_registry.get_inference(inference_id)
        output_path = root / job['output_path']
        click.echo(f"   Results: {output_path}")

    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Inference failed: {e}")
        raise SystemExit(2)


@predict.command()
@click.argument('directory')
@click.option('--model', '-m', required=True, help='Model name, run ID, or path')
@click.option('--conf', default=0.25, type=float, help='Confidence threshold (0-1)')
@click.option('--iou', default=0.45, type=float, help='IoU threshold for NMS (0-1)')
@click.option('--device', default='cpu', help='Device (cpu, cuda, cuda:0, mps)')
@click.option('--batch', default=16, type=int, help='Batch size')
@click.option('--save-txt/--no-save-txt', default=True, help='Save YOLO labels')
@click.option('--save-img/--no-save-img', default=False, help='Save annotated images')
@click.option('--classes', help='Filter classes (comma-separated IDs)')
def images(
    directory: str,
    model: str,
    conf: float,
    iou: float,
    device: str,
    batch: int,
    save_txt: bool,
    save_img: bool,
    classes: Optional[str]
):
    """
    Run inference on a directory of images.

    Examples:
        modelcub predict images test_images/ --model detector-v1
        modelcub predict images test_images/ -m run-xyz --batch 32 --save-img
    """
    from modelcub.services.inference import InferenceService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = InferenceService(root)

        # Parse classes
        class_list = None
        if classes:
            class_list = [int(c.strip()) for c in classes.split(',')]

        click.echo(f"🔍 Running inference on: {directory}")
        click.echo(f"   Model: {model}")

        # Create and run inference job
        inference_id = service.create_inference_job(
            model_identifier=model,
            input_type='images',
            input_path=directory,
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            classes=class_list,
            batch_size=batch
        )

        # Progress with status updates
        import sys

        def progress(current, total, message):
            if current == 100:
                click.echo(f"\r   ✓ {message}          ")
            else:
                click.echo(f"\r   {message}...", nl=False)
                sys.stdout.flush()

        stats = service.run_inference(inference_id, progress_callback=progress)

        click.echo()
        click.echo(f"✅ Inference complete!")
        click.echo(f"   Images: {stats['total_images']}")
        click.echo(f"   Detections: {stats['total_detections']}")
        click.echo(f"   Avg time: {stats['avg_inference_time_ms']:.1f}ms/image")

        if stats['classes_detected']:
            click.echo(f"   Classes: {', '.join(stats['classes_detected'])}")

        job = service.inference_registry.get_inference(inference_id)
        output_path = root / job['output_path']
        click.echo(f"   Results: {output_path}")

    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Inference failed: {e}")
        raise SystemExit(2)


@predict.command()
@click.argument('dataset_name')
@click.option('--model', '-m', required=True, help='Model name, run ID, or path')
@click.option('--split', default='val', type=click.Choice(['train', 'val', 'test']),
              help='Dataset split to predict on')
@click.option('--conf', default=0.25, type=float, help='Confidence threshold (0-1)')
@click.option('--iou', default=0.45, type=float, help='IoU threshold for NMS (0-1)')
@click.option('--device', default='cpu', help='Device (cpu, cuda, cuda:0, mps)')
@click.option('--batch', default=16, type=int, help='Batch size')
@click.option('--save-txt/--no-save-txt', default=True, help='Save YOLO labels')
@click.option('--save-img/--no-save-img', default=False, help='Save annotated images')
def dataset(
    dataset_name: str,
    model: str,
    split: str,
    conf: float,
    iou: float,
    device: str,
    batch: int,
    save_txt: bool,
    save_img: bool
):
    """
    Run inference on a dataset split.

    Useful for validation or testing a model on labeled data.

    Examples:
        modelcub predict dataset my-dataset --model detector-v1
        modelcub predict dataset my-dataset --split test -m run-xyz
    """
    from modelcub.services.inference import InferenceService
    from modelcub.core.paths import project_root
    from modelcub.core.registries import DatasetRegistry

    try:
        root = project_root()
        service = InferenceService(root)

        # Validate dataset exists
        dataset_registry = DatasetRegistry(root)
        if not dataset_registry.exists(dataset_name):
            click.echo(f"❌ Dataset not found: {dataset_name}")
            raise SystemExit(2)

        # Get dataset path
        dataset_path = root / "data" / "datasets" / dataset_name

        click.echo(f"🔍 Running inference on dataset: {dataset_name}")
        click.echo(f"   Split: {split}")
        click.echo(f"   Model: {model}")

        # Create and run inference job
        inference_id = service.create_inference_job(
            model_identifier=model,
            input_type='dataset',
            input_path=str(dataset_path),
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            batch_size=batch
        )

        # Progress updates
        import sys

        def progress(current, total, message):
            if current == 100:
                click.echo(f"\r   ✓ {message}          ")
            else:
                click.echo(f"\r   {message}...", nl=False)
                sys.stdout.flush()

        stats = service.run_inference(inference_id, progress_callback=progress)

        click.echo()
        click.echo(f"✅ Inference complete!")
        click.echo(f"   Images: {stats['total_images']}")
        click.echo(f"   Detections: {stats['total_detections']}")
        click.echo(f"   Avg time: {stats['avg_inference_time_ms']:.1f}ms/image")

        if stats['classes_detected']:
            click.echo(f"   Classes: {', '.join(stats['classes_detected'])}")

        job = service.inference_registry.get_inference(inference_id)
        output_path = root / job['output_path']
        click.echo(f"   Results: {output_path}")

    except FileNotFoundError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Inference failed: {e}")
        raise SystemExit(2)


@predict.command('list')
@click.option('--status', type=click.Choice(['pending', 'running', 'completed', 'failed']),
              help='Filter by status')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def list_inferences(status: Optional[str], json_output: bool):
    """
    List inference jobs.

    Examples:
        modelcub predict list
        modelcub predict list --status completed
        modelcub predict list --json
    """
    from modelcub.services.inference import InferenceService
    from modelcub.core.paths import project_root
    import json

    try:
        root = project_root()
        service = InferenceService(root)

        jobs = service.list_inferences(status=status)

        if json_output:
            click.echo(json.dumps(jobs, indent=2))
            return

        if not jobs:
            click.echo("No inference jobs found.")
            return

        click.echo(f"Found {len(jobs)} inference job(s):\n")

        for job in jobs:
            status_icon = {
                'pending': '⏳',
                'running': '▶️',
                'completed': '✅',
                'failed': '❌'
            }.get(job['status'], '❓')

            click.echo(f"{status_icon} {job['id']}")
            click.echo(f"   Status: {job['status']}")
            click.echo(f"   Model: {job['model_source']}")
            click.echo(f"   Input: {job['input_path']} ({job['input_type']})")

            if job.get('stats'):
                stats = job['stats']
                click.echo(f"   Images: {stats['total_images']}, Detections: {stats['total_detections']}")

            click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to list inferences: {e}")
        raise SystemExit(2)


@predict.command('get')
@click.argument('inference_id')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def get_inference(inference_id: str, json_output: bool):
    """
    Get inference job details and results.

    Examples:
        modelcub predict get inf-20251027-152030
        modelcub predict get inf-20251027-152030 --json
    """
    from modelcub.services.inference import InferenceService
    from modelcub.core.paths import project_root
    import json

    try:
        root = project_root()
        service = InferenceService(root)

        result = service.get_results(inference_id)

        if not result:
            click.echo(f"❌ Inference job not found: {inference_id}")
            raise SystemExit(2)

        job = result['job']

        if json_output:
            click.echo(json.dumps(result, indent=2))
            return

        # Display job info
        status_icon = {
            'pending': '⏳',
            'running': '▶️',
            'completed': '✅',
            'failed': '❌'
        }.get(job['status'], '❓')

        click.echo(f"{status_icon} Inference Job: {inference_id}\n")
        click.echo(f"Status: {job['status']}")
        click.echo(f"Created: {job['created']}")
        click.echo(f"Model: {job['model_source']}")
        click.echo(f"Input: {job['input_path']} ({job['input_type']})")
        click.echo(f"Output: {job['output_path']}")

        click.echo(f"\nConfig:")
        config = job['config']
        click.echo(f"  Confidence: {config['conf_threshold']}")
        click.echo(f"  IoU: {config['iou_threshold']}")
        click.echo(f"  Device: {config['device']}")
        click.echo(f"  Save labels: {config['save_txt']}")
        click.echo(f"  Save images: {config['save_img']}")

        if job.get('stats'):
            click.echo(f"\nResults:")
            stats = job['stats']
            click.echo(f"  Images: {stats['total_images']}")
            click.echo(f"  Detections: {stats['total_detections']}")
            click.echo(f"  Avg time: {stats['avg_inference_time_ms']:.1f}ms/image")

            if stats.get('classes_detected'):
                click.echo(f"  Classes: {', '.join(stats['classes_detected'])}")

        if job.get('error'):
            click.echo(f"\n❌ Error: {job['error']}")

    except Exception as e:
        click.echo(f"❌ Failed to get inference details: {e}")
        raise SystemExit(2)