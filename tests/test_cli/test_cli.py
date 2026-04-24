"""Tests for the agentlab CLI commands."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from agent_lab.cli import main
from agent_lab.models.asl import AgenticArchitecture


class TestCLIInit:
    def test_init_creates_project(self, tmp_path: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["init", "my-project", "--output-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "my-project" / "asl.yaml").exists()


class TestCLIValidate:
    def test_validate_valid_spec(self, sample_spec_yaml: Path) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(sample_spec_yaml)])
        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_validate_invalid_spec(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("apiVersion: agent-lab.io/v1alpha1\nkind: AgenticArchitecture\n")
        runner = CliRunner()
        result = runner.invoke(main, ["validate", str(bad)])
        assert result.exit_code == 1


class TestCLIGenerate:
    def test_generate_produces_output(self, sample_spec_yaml: Path, tmp_path: Path) -> None:
        runner = CliRunner()
        out_dir = tmp_path / "output"
        result = runner.invoke(
            main,
            ["generate", str(sample_spec_yaml), "--output-dir", str(out_dir)],
        )
        assert result.exit_code == 0
        assert out_dir.exists()
        # Should have created agent files
        agent_files = list(out_dir.rglob("*.py"))
        assert len(agent_files) > 0
