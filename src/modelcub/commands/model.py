"""Model management commands."""
import click
from pathlib import Path


@click.group()
def model():
    """Manage promoted models."""
    pass


@model.command()
@click.argument('run_id')
@click.argument('name')
@click.option('--description', help='Model description')
@click.option('--tags', help='Comma-separated tags')
def promote(run_id: str, name: str, description: str, tags: str):
    """
    Promote a trained model to production.

    Takes the best weights from a training run and promotes them
    to the models registry for production use.

    Examples:
        modelcub model promote run-20251027-143022 detector-v1
        modelcub model promote run-20251027-143022 detector-v2 --description "Improved with new data"
    """
    from modelcub.core.registries import RunRegistry, ModelRegistry
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        run_registry = RunRegistry(root)
        model_registry = ModelRegistry(root)

        # Get run info
        run = run_registry.get_run(run_id)
        if not run:
            click.echo(f"❌ Run not found: {run_id}")
            raise SystemExit(2)

        if run['status'] != 'completed':
            click.echo(f"❌ Run must be completed (current status: {run['status']})")
            raise SystemExit(2)

        # Find best weights
        run_path = root / run['artifacts_path']
        weights_dir = run_path / 'train' / 'weights'
        best_weights = weights_dir / 'best.pt'

        if not best_weights.exists():
            click.echo(f"❌ Best weights not found: {best_weights}")
            raise SystemExit(2)

        click.echo(f"🎯 Promoting model from run: {run_id}")
        click.echo(f"   Name: {name}")
        click.echo(f"   Source: {best_weights}")
        click.echo()

        # Prepare metadata
        metadata = {
            'description': description or '',
            'metrics': run.get('metrics', {}),
            'config': run['config'],
            'dataset_name': run['dataset_name'],
            'dataset_snapshot_id': run['dataset_snapshot_id']
        }

        if tags:
            metadata['tags'] = [t.strip() for t in tags.split(',')]

        # Promote model
        version = model_registry.promote_model(
            name=name,
            run_id=run_id,
            model_path=best_weights,
            metadata=metadata
        )

        click.echo(f"✅ Model promoted successfully!")
        click.echo(f"\n📦 Model: {name}")
        click.echo(f"   Version: {version}")

        if run.get('metrics'):
            metrics = run['metrics']
            click.echo(f"\n📈 Performance:")
            click.echo(f"   mAP50:     {metrics.get('map50', 'N/A')}")
            click.echo(f"   mAP50-95:  {metrics.get('map50_95', 'N/A')}")
            click.echo(f"   Precision: {metrics.get('precision', 'N/A')}")
            click.echo(f"   Recall:    {metrics.get('recall', 'N/A')}")

        click.echo(f"\nUse this model:")
        click.echo(f"  modelcub model info {name}")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to promote model: {e}")
        raise SystemExit(2)


@model.command(name='list')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def list_models(output_json: bool):
    """
    List all promoted models.

    Examples:
        modelcub model list
        modelcub model list --json
    """
    from modelcub.core.registries import ModelRegistry
    from modelcub.core.paths import project_root
    import json

    try:
        root = project_root()
        model_registry = ModelRegistry(root)

        models = model_registry.list_models()

        if output_json:
            click.echo(json.dumps(models, indent=2))
            return

        if not models:
            click.echo("No promoted models found.")
            click.echo("\nPromote a model from a training run:")
            click.echo("  modelcub model promote <run-id> <name>")
            return

        click.echo(f"\n📦 Promoted Models ({len(models)} total)")
        click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Sort by created date (newest first)
        models_sorted = sorted(models, key=lambda m: m.get('created', ''), reverse=True)

        for mdl in models_sorted:
            click.echo(f"\n{click.style(mdl['name'], fg='cyan', bold=True)}")
            click.echo(f"  Version:  {mdl['version']}")
            click.echo(f"  Created:  {mdl['created']}")
            click.echo(f"  Run ID:   {mdl['run_id']}")
            click.echo(f"  Path:     {mdl['path']}")

            metadata = mdl.get('metadata', {})

            if metadata.get('description'):
                click.echo(f"  Desc:     {metadata['description']}")

            if metadata.get('tags'):
                tags = ', '.join(metadata['tags'])
                click.echo(f"  Tags:     {tags}")

            # Show metrics if available
            metrics = metadata.get('metrics', {})
            if metrics:
                click.echo(f"  mAP50:    {metrics.get('map50', 'N/A')}")

        click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to list models: {e}")
        raise SystemExit(2)


@model.command()
@click.argument('name')
def info(name: str):
    """
    Show detailed information about a promoted model.

    Examples:
        modelcub model info detector-v1
    """
    from modelcub.core.registries import ModelRegistry
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        model_registry = ModelRegistry(root)

        mdl = model_registry.get_model(name)
        if not mdl:
            click.echo(f"❌ Model not found: {name}")
            raise SystemExit(2)

        click.echo(f"\n📦 Model: {click.style(name, fg='cyan', bold=True)}")
        click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo(f"Version:       {mdl['version']}")
        click.echo(f"Created:       {mdl['created']}")
        click.echo(f"Source Run:    {mdl['run_id']}")
        click.echo(f"Model Path:    {mdl['path']}")

        metadata = mdl.get('metadata', {})

        if metadata.get('description'):
            click.echo(f"\n📝 Description:")
            click.echo(f"   {metadata['description']}")

        if metadata.get('tags'):
            click.echo(f"\n🏷️  Tags:")
            for tag in metadata['tags']:
                click.echo(f"   • {tag}")

        # Training configuration
        config = metadata.get('config', {})
        if config:
            click.echo(f"\n⚙️  Training Configuration:")
            click.echo(f"   Model:      {config.get('model', 'N/A')}")
            click.echo(f"   Epochs:     {config.get('epochs', 'N/A')}")
            click.echo(f"   Batch:      {config.get('batch', 'N/A')}")
            click.echo(f"   Image Size: {config.get('imgsz', 'N/A')}")
            click.echo(f"   Device:     {config.get('device', 'N/A')}")

        # Dataset info
        if metadata.get('dataset_name'):
            click.echo(f"\n📊 Dataset:")
            click.echo(f"   Name:       {metadata['dataset_name']}")
            if metadata.get('dataset_snapshot_id'):
                click.echo(f"   Snapshot:   {metadata['dataset_snapshot_id']}")

        # Performance metrics
        metrics = metadata.get('metrics', {})
        if metrics:
            click.echo(f"\n📈 Performance Metrics:")
            click.echo(f"   mAP50:      {metrics.get('map50', 'N/A')}")
            click.echo(f"   mAP50-95:   {metrics.get('map50_95', 'N/A')}")
            click.echo(f"   Precision:  {metrics.get('precision', 'N/A')}")
            click.echo(f"   Recall:     {metrics.get('recall', 'N/A')}")
            if 'best_epoch' in metrics:
                click.echo(f"   Best Epoch: {metrics['best_epoch']}")

        click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to get model info: {e}")
        raise SystemExit(2)


@model.command()
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Confirm deletion without prompting')
def delete(name: str, yes: bool):
    """
    Delete a promoted model.

    Examples:
        modelcub model delete detector-v1
        modelcub model delete detector-v1 --yes
    """
    from modelcub.core.registries import ModelRegistry
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        model_registry = ModelRegistry(root)

        # Check if model exists
        mdl = model_registry.get_model(name)
        if not mdl:
            click.echo(f"❌ Model not found: {name}")
            raise SystemExit(2)

        # Confirm deletion
        if not yes:
            click.echo(f"⚠️  About to delete model: {name}")
            click.echo(f"   Version: {mdl['version']}")
            click.echo(f"   Path:    {mdl['path']}")
            click.echo()

            if not click.confirm("Are you sure?"):
                click.echo("Cancelled.")
                return

        # Delete model
        model_registry.remove_model(name)

        click.echo(f"✅ Model deleted: {name}")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to delete model: {e}")
        raise SystemExit(2)