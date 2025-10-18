"""
ModelCub CLI - Main entry point.
"""
import click
from modelcub.commands import project, dataset, annotation, job, ui_cmd


@click.group()
@click.version_option(version="0.0.2", prog_name="modelcub")
def cli():
    """ModelCub - Complete computer vision platform."""
    pass


# Register command groups
cli.add_command(project.project)
cli.add_command(dataset.dataset)
cli.add_command(annotation.annotate)
cli.add_command(job.job)
cli.add_command(ui_cmd.ui)


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n❌ Interrupted by user")
        raise SystemExit(130)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()