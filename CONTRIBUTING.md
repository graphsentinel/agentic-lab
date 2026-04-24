# Contributing to AGENT-LAB

Thank you for your interest in contributing to AGENT-LAB! This document
provides guidelines for contributing to the project.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/graphsentinel/agent-lab.git
cd agent-lab

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify the installation
pytest
agentlab --help
```

**Requirements:** Python 3.11+

## Running Tests

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_models/test_asl.py

# Run with coverage
pytest --cov=agent_lab --cov-report=term-missing
```

## Code Quality

We use **ruff** for linting/formatting and **mypy** for type checking.

```bash
# Lint
ruff check src/ tests/

# Format check (dry run)
ruff format --check src/ tests/

# Auto-format
ruff format src/ tests/

# Type check
mypy src/
```

All checks must pass before a pull request can be merged. The CI pipeline runs
these automatically.

## Pull Request Process

1. **Fork** the repository and create a feature branch from `main`.
2. **Write tests** for new functionality or bug fixes.
3. **Run the full suite** (`pytest`, `ruff check`, `mypy src/`) locally.
4. **Commit** with clear, descriptive messages.
5. **Open a PR** against `main` with a summary of changes.

### PR checklist

- [ ] Tests pass (`pytest`)
- [ ] Lint clean (`ruff check src/ tests/`)
- [ ] Type check clean (`mypy src/`)
- [ ] New functionality includes tests
- [ ] ASL YAML examples validate (`agentlab validate examples/<file>.yaml`)

## Contributing ASL Examples

If you're contributing a new ASL YAML example:

1. Place it in the `examples/` directory.
2. Follow the existing naming convention: `<template>_<domain>.yaml`.
3. Include a header comment block explaining the architecture decision,
   hierarchy, and any domain-specific considerations.
4. Add a corresponding test file in `tests/test_models/` that validates the
   YAML loads, round-trips, and key structural properties.
5. Ensure all agents reference tools from the shared `spec.layers.tools`
   catalogue.

## Contributing Generator Adapters

New framework adapters (e.g., CrewAI, AutoGen) should:

1. Subclass `GeneratorAdapter` from `agent_lab.generators.base`.
2. Implement `generate()`, `generate_dockerfile()`, and
   `generate_k8s_manifests()`.
3. Self-register in the `GeneratorRegistry` at module import time.
4. Include tests in `tests/test_generators/`.

## Reporting Issues

Use [GitHub Issues](https://github.com/graphsentinel/agent-lab/issues) to report bugs
or request features. For security vulnerabilities, see `SECURITY.md`.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the
Apache License 2.0.
