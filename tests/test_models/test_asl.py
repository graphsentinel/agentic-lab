"""Tests for the root ASL model and YAML round-tripping."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_lab.models.asl import (
    AgenticArchitecture,
    ArchitectureTemplate,
    TargetDeployment,
)


class TestAgenticArchitecture:
    def test_sample_spec_is_valid(self, sample_spec: AgenticArchitecture) -> None:
        assert sample_spec.metadata.name == "test-architecture"
        assert sample_spec.spec.architecture_template == ArchitectureTemplate.CENTRALIZED

    def test_yaml_round_trip(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        path = tmp_path / "round_trip.yaml"
        sample_spec.to_yaml(path)
        loaded = AgenticArchitecture.from_yaml(path)
        assert loaded.metadata.name == sample_spec.metadata.name
        assert loaded.spec.architecture_template == sample_spec.spec.architecture_template
        assert len(loaded.spec.layers.strategic) == 1
        assert len(loaded.spec.layers.tactical) == 1
        assert len(loaded.spec.layers.execution) == 2

    def test_layer_counts(self, sample_spec: AgenticArchitecture) -> None:
        layers = sample_spec.spec.layers
        assert len(layers.strategic) == 1
        assert len(layers.tactical) == 1
        assert len(layers.execution) == 2

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "bad.yaml"
        bad_path.write_text("apiVersion: agent-lab.io/v1alpha1\nkind: AgenticArchitecture\n")
        with pytest.raises(Exception):
            AgenticArchitecture.from_yaml(bad_path)

    def test_default_deployment_is_kubernetes(
        self, sample_spec: AgenticArchitecture
    ) -> None:
        assert sample_spec.spec.target_deployment == TargetDeployment.KUBERNETES
