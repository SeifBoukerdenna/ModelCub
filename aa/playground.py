"""
ModelCub SDK Playground

Quick experimentation and testing with your project's SDK.
Run with: python playground.py
"""
from modelcub import Project, Dataset
from pathlib import Path

# Auto-load current project
project = Project.load()
print(f"📦 Project: {{project.name}}")
print(f"📍 Path: {{project.path}}")
print()

# ========== Helper Functions ==========

def list_datasets():
    """Show all datasets in this project."""
    datasets = project.list_datasets()
    if not datasets:
        print("  No datasets yet")
        return []

    for ds in datasets:
        print(f"  - {{ds.name}} (v{{ds.version}}): {{ds.num_images}} images, {{len(ds.classes)}} classes")
    return datasets


def list_runs():
    """Show all training runs."""
    runs = project.list_runs()
    if not runs:
        print("  No training runs yet")
        return []

    for run in runs:
        print(f"  - {{run.name}}: {{run.status}}")
    return runs


def load_dataset(name: str):
    """Load a dataset by name."""
    dataset = project.get_dataset(name)
    print(f"\nLoaded: {{dataset.name}}")
    print(f"  Images: {{dataset.num_images}}")
    print(f"  Classes: {{', '.join(dataset.classes)}}")
    return dataset


# ========== Quick Overview ==========

if __name__ == "__main__":
    print("📊 Datasets:")
    datasets = list_datasets()

    print("\n🏃 Training Runs:")
    runs = list_runs()

    print("\n" + "="*50)
    print("Add your experiments below:")
    print("="*50)

    # ========== Your Experiments Here ==========

    # Example: Load and inspect a dataset
    # dataset = load_dataset("my-dataset-v1")
    # print(f"First image: {{dataset.image_paths[0]}}")

    # Example: Get dataset statistics
    # stats = dataset.get_stats()
    # print(f"Class distribution: {{stats.class_distribution}}")

    # Example: Load a training run
    # run = project.get_run("my-run-20241010")
    # print(f"Best mAP50: {{run.results.best_map50}}")
    # print(f"Training time: {{run.results.training_time}}")

    # Example: Create a new dataset programmatically
    # new_dataset = project.create_dataset(
    #     name="test-dataset",
    #     source="/path/to/images",
    #     format="yolo"
    # )

    pass  # Your code here
