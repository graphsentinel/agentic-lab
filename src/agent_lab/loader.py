"""YAML loading and multi-document support for ASL specs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agent_lab.models.asl import AgenticArchitecture


def load_spec(path: str | Path) -> AgenticArchitecture:
    """Load and validate a single ASL YAML document.

    Args:
        path: Path to the YAML file.

    Returns:
        Validated AgenticArchitecture model.

    Raises:
        pydantic.ValidationError: If the YAML does not conform to the ASL schema.
        FileNotFoundError: If the file does not exist.
    """
    return AgenticArchitecture.from_yaml(path)


def load_all_specs(path: str | Path) -> list[AgenticArchitecture]:
    """Load all YAML documents from a multi-document ASL file.

    Supports YAML files with multiple `---` separated documents.
    """
    specs: list[AgenticArchitecture] = []
    with open(path) as f:
        for doc in yaml.safe_load_all(f):
            if doc is not None:
                specs.append(AgenticArchitecture.model_validate(doc))
    return specs


def validate_spec_data(data: dict[str, Any]) -> AgenticArchitecture:
    """Validate a raw dict against the ASL schema.

    Useful when the YAML has already been parsed (e.g. from an API request).
    """
    return AgenticArchitecture.model_validate(data)
