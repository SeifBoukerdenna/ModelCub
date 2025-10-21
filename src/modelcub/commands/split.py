"""
CLI commands for dataset split management.
"""
import click
from pathlib import Path

@click.group()
def split():
    """Manage dataset splits (train/val/test)."""
    pass


@split.command()
@click.argument('dataset_name')
@click.option('--train', '-t', default=70.0, type=float, help='Training percentage (default: 70)')
@click.option('--val', '-v', default=20.0, type=float, help='Validation percentage (default: 20)')
@click.option('--test', default=10.0, type=float, help='Test percentage (default: 10)')
@click.option('--source', default='unlabeled', help='Source split to redistribute (default: unlabeled)')
@click.option('--seed', default=42, type=int, help='Random seed for reproducibility')
@click.option('--no-shuffle', is_flag=True, help='Do not shuffle images before splitting')
def auto(dataset_name: str, train: float, val: float, test: float, source: str, seed: int, no_shuffle: bool):
    """
    Automatically split dataset by percentage.

    Examples:
        modelcub split auto my-dataset --train 70 --val 20 --test 10
        modelcub split auto my-dataset --train 80 --val 10 --test 10 --source unlabeled
    """
    from modelcub.services.split_service import auto_split_by_percentage
    from modelcub.core.paths import project_root

    try:
        root = project_root()

        # Validate percentages
        total = train + val + test
        if abs(total - 100.0) > 0.01:
            click.echo(f"❌ Percentages must sum to 100 (got {total})")
            raise SystemExit(2)

        click.echo(f"\n📊 Auto-splitting dataset: {dataset_name}")
        click.echo(f"   Distribution: {train}% train / {val}% val / {test}% test")
        click.echo(f"   Source: {source} split")
        click.echo(f"   Shuffle: {'Yes' if not no_shuffle else 'No'} (seed={seed})\n")

        result = auto_split_by_percentage(
            project_path=root,
            dataset_name=dataset_name,
            train_pct=train,
            val_pct=val,
            test_pct=test,
            source_split=source,
            shuffle=not no_shuffle,
            seed=seed
        )

        if result.success:
            click.echo(f"✅ {result.message}")

            if "distribution" in result.data:
                dist = result.data["distribution"]
                click.echo(f"\n   Train: {dist['train']} images")
                click.echo(f"   Val:   {dist['val']} images")
                click.echo(f"   Test:  {dist['test']} images")
                click.echo(f"   Total: {dist['total']} images\n")
        else:
            click.echo(f"❌ {result.message}")
            raise SystemExit(2)

    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)


@split.command()
@click.argument('dataset_name')
@click.argument('job_id')
def assign(dataset_name: str, job_id: str):
    """
    Interactively assign images to splits after annotation job.

    Example:
        modelcub split assign my-dataset abc12345
    """
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


@split.command()
@click.argument('dataset_name')
def stats(dataset_name: str):
    """
    Show split statistics for a dataset.

    Example:
        modelcub split stats my-dataset
    """
    from modelcub.sdk import Dataset

    try:
        dataset = Dataset.load(dataset_name)
        counts = dataset.get_split_counts()
        total = sum(counts.values())

        click.echo(f"\n📊 Split Statistics: {dataset_name}\n")

        for split in ['train', 'val', 'test', 'unlabeled']:
            count = counts.get(split, 0)
            pct = (count / total * 100) if total > 0 else 0
            click.echo(f"   {split.capitalize():12} {count:6} images ({pct:5.1f}%)")

        click.echo(f"   {'Total':12} {total:6} images\n")

    except Exception as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)