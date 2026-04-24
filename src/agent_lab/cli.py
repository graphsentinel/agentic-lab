"""AGENT-LAB CLI — agentlab init | validate | generate.

Entry point for the command-line interface that drives both Phase 1
(declarative specification) and Phase 2 (code/container generation).
"""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agent_lab import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="agentlab")
def main() -> None:
    """AGENT-LAB: Declarative agentic workflow architecture and code generation."""


# ---------------------------------------------------------------------------
# agentlab init
# ---------------------------------------------------------------------------


@main.command()
@click.argument("name")
@click.option(
    "--template",
    type=click.Choice(["centralized", "distributed"]),
    default="centralized",
    help="Architecture template (centralized/pyramid or distributed/mesh).",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default=".",
    help="Directory to create the project in.",
)
def init(name: str, template: str, output_dir: str) -> None:
    """Scaffold a new ASL project with a starter YAML spec."""
    from agent_lab.models.asl import (
        API_VERSION,
        KIND,
        AgenticArchitecture,
        ArchitectureTemplate,
        GenerationConfig,
        LayersConfig,
        Metadata,
        SpecConfig,
    )
    from agent_lab.protocols.base import ProtocolsConfig
    from agent_lab.security.governance import SecurityConfig

    out = Path(output_dir) / name
    out.mkdir(parents=True, exist_ok=True)

    arch = AgenticArchitecture(
        apiVersion=API_VERSION,
        kind=KIND,
        metadata=Metadata(name=name),
        spec=SpecConfig(
            architecture_template=ArchitectureTemplate(template),
            protocols=ProtocolsConfig(),
            security=SecurityConfig(),
            layers=LayersConfig(),
            generation=GenerationConfig(),
        ),
    )
    spec_path = out / "asl.yaml"
    arch.to_yaml(spec_path)
    console.print(f"[green]Created project '{name}' at {out}[/green]")
    console.print(f"  Spec file: {spec_path}")


# ---------------------------------------------------------------------------
# agentlab validate
# ---------------------------------------------------------------------------


@main.command()
@click.argument("spec_file", type=click.Path(exists=True))
def validate(spec_file: str) -> None:
    """Validate an ASL YAML specification file."""
    from pydantic import ValidationError

    from agent_lab.models.asl import AgenticArchitecture

    try:
        arch = AgenticArchitecture.from_yaml(spec_file)
    except ValidationError as exc:
        console.print("[red]Validation FAILED[/red]")
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            console.print(f"  [yellow]{loc}[/yellow]: {err['msg']}")
        raise SystemExit(1)

    console.print(f"[green]Validation PASSED[/green] — {arch.metadata.name}")

    table = Table(title="Architecture Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Template", arch.spec.architecture_template.value)
    table.add_row("Deployment", arch.spec.target_deployment.value)
    table.add_row("Tools", str(len(arch.spec.layers.tools)))
    table.add_row("Strategic agents", str(len(arch.spec.layers.strategic)))
    table.add_row("Tactical agents", str(len(arch.spec.layers.tactical)))
    table.add_row("Execution agents", str(len(arch.spec.layers.execution)))
    table.add_row("PII scrubbing", arch.spec.security.pii_scrubbing.value)
    console.print(table)


# ---------------------------------------------------------------------------
# agentlab generate
# ---------------------------------------------------------------------------


@main.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("--output-dir", type=click.Path(), default=None, help="Override output directory.")
def generate(spec_file: str, output_dir: str | None) -> None:
    """Generate code, Dockerfiles, and K8s manifests from an ASL spec."""
    from agent_lab.generators.registry import GeneratorRegistry
    from agent_lab.models.asl import AgenticArchitecture

    # Ensure built-in adapters are registered
    import agent_lab.generators.langchain_python  # noqa: F401
    import agent_lab.generators.native_python  # noqa: F401

    arch = AgenticArchitecture.from_yaml(spec_file)
    target = arch.spec.generation.target_framework
    out = Path(output_dir or arch.spec.generation.output_dir)

    try:
        adapter_cls = GeneratorRegistry.get(target)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    adapter = adapter_cls()
    console.print(f"[blue]Generating code with adapter: {adapter.name}[/blue]")

    files = adapter.generate(arch, out)
    for f in files:
        console.print(f"  [green]+[/green] {f}")

    if arch.spec.generation.containerize:
        df = adapter.generate_dockerfile(arch, out)
        console.print(f"  [green]+[/green] {df}")

    if arch.spec.generation.k8s_manifests:
        manifests = adapter.generate_k8s_manifests(arch, out)
        for m in manifests:
            console.print(f"  [green]+[/green] {m}")

    console.print(f"\n[green]Generation complete.[/green] Output: {out}")
