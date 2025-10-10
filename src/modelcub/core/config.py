"""
ModelCub configuration management.

Handles .modelcub/config.yaml with full project settings.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ProjectConfig:
    """Project metadata configuration."""
    name: str = "unnamed"
    created: str = ""
    version: str = "1.0.0"


@dataclass
class DefaultsConfig:
    """Default training/inference settings."""
    device: str = "cuda"  # cuda, cpu, mps
    batch_size: int = 16
    image_size: int = 640
    workers: int = 8
    format: str = "yolo"


@dataclass
class PathsConfig:
    """Project directory paths."""
    data: str = "data"
    runs: str = "runs"
    reports: str = "reports"


@dataclass
class Config:
    """Complete ModelCub project configuration."""
    project: ProjectConfig
    defaults: DefaultsConfig
    paths: PathsConfig

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "project": asdict(self.project),
            "defaults": asdict(self.defaults),
            "paths": asdict(self.paths)
        }

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        """Load from dictionary."""
        project_data = data.get("project", {})
        defaults_data = data.get("defaults", {})
        paths_data = data.get("paths", {})

        return cls(
            project=ProjectConfig(**project_data) if project_data else ProjectConfig(),
            defaults=DefaultsConfig(**defaults_data) if defaults_data else DefaultsConfig(),
            paths=PathsConfig(**paths_data) if paths_data else PathsConfig()
        )

    def to_yaml_string(self) -> str:
        """Convert to YAML format (without PyYAML dependency)."""
        lines = []

        lines.append("# ModelCub Project Configuration")
        lines.append("project:")
        lines.append(f"  name: \"{self.project.name}\"")
        lines.append(f"  created: \"{self.project.created}\"")
        lines.append(f"  version: \"{self.project.version}\"")
        lines.append("")

        lines.append("defaults:")
        lines.append(f"  device: \"{self.defaults.device}\"")
        lines.append(f"  batch_size: {self.defaults.batch_size}")
        lines.append(f"  image_size: {self.defaults.image_size}")
        lines.append(f"  workers: {self.defaults.workers}")
        lines.append(f"  format: \"{self.defaults.format}\"")
        lines.append("")

        lines.append("paths:")
        lines.append(f"  data: \"{self.paths.data}\"")
        lines.append(f"  runs: \"{self.paths.runs}\"")
        lines.append(f"  reports: \"{self.paths.reports}\"")
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_yaml_string(cls, content: str) -> Config:
        """Parse YAML string (simple parser without PyYAML)."""
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]

        data = {"project": {}, "defaults": {}, "paths": {}}
        current_section = None

        for line in lines:
            if line.endswith(":") and not line.startswith(" "):
                section_name = line[:-1].strip()
                if section_name in data:
                    current_section = section_name
            elif ":" in line and current_section:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"').strip("'")

                    if value.isdigit():
                        value = int(value)
                    elif value.lower() in ("true", "false"):
                        value = value.lower() == "true"
                    elif value.replace(".", "", 1).isdigit():
                        try:
                            value = float(value)
                        except:
                            pass

                    if current_section and key:
                        data[current_section][key] = value

        return cls.from_dict(data)


def load_config(project_root: Path) -> Optional[Config]:
    """Load config from .modelcub/config.yaml."""
    config_path = project_root / ".modelcub" / "config.yaml"
    if not config_path.exists():
        return None

    content = config_path.read_text(encoding="utf-8")
    return Config.from_yaml_string(content)


def save_config(project_root: Path, config: Config) -> None:
    """Save config to .modelcub/config.yaml."""
    config_path = project_root / ".modelcub" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config.to_yaml_string(), encoding="utf-8")


def create_default_config(name: str) -> Config:
    """Create default configuration for a new project."""
    return Config(
        project=ProjectConfig(
            name=name,
            created=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            version="1.0.0"
        ),
        defaults=DefaultsConfig(),
        paths=PathsConfig()
    )