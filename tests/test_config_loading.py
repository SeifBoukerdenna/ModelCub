#!/usr/bin/env python3
"""Quick test to debug config loading."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from modelcub.services.project_service import init_project, InitProjectRequest
from modelcub.core.config import load_config

# Create project
print("Creating project...")
req = InitProjectRequest(path="test-config-debug", name="test-config-debug", force=True)
code, msg = init_project(req)
print(f"Code: {code}")
print(f"Message: {msg}")

# Check if files exist
project_path = Path("test-config-debug").resolve()
print(f"\nProject path: {project_path}")
print(f"Exists: {project_path.exists()}")

config_file = project_path / ".modelcub" / "config.yaml"
print(f"\nConfig file: {config_file}")
print(f"Exists: {config_file.exists()}")

if config_file.exists():
    print(f"\nConfig content:")
    print(config_file.read_text())

    print(f"\nTrying to load config...")
    try:
        config = load_config(project_path)
        if config:
            print(f"✅ Config loaded!")
            print(f"   Name: {config.project.name}")
            print(f"   Device: {config.defaults.device}")
        else:
            print(f"❌ load_config returned None")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()

# Cleanup
import shutil
if project_path.exists():
    shutil.rmtree(project_path)
    print(f"\n✅ Cleaned up test project")