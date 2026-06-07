# Contributing

Thank you for your interest in contributing to agentic-lab!

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/graphsentinel/agentic-lab.git
cd agentic-lab

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify the installation
pytest
agentlab --help
```

**Requirements:** Python 3.11+

---

## Running Tests

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_models/test_asl.py

# Run with coverage report
pytest --cov=agent_lab --cov-report=term-missing
```

---

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

All checks must pass before a pull request can be merged. The CI pipeline runs these automatically.

---

## Pull Request Process

1. **Fork** the repository and create a feature branch from `main`.
2. **Write tests** for new functionality or bug fixes.
3. **Run the full suite** (`pytest`, `ruff check`, `mypy src/`) locally.
4. **Commit** with clear, descriptive messages.
5. **Open a PR** against `main` with a summary of changes.

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Lint clean (`ruff check src/ tests/`)
- [ ] Type check clean (`mypy src/`)
- [ ] New functionality includes tests
- [ ] ASL YAML examples validate (`agentlab validate examples/<file>.yaml`)

---

## Contributing ASL Examples

If you are contributing a new ASL YAML example:

1. Place it in the `examples/` directory.
2. Validate it with `agentlab validate examples/<your-file>.yaml`.
3. Add a description to [Reference → Examples](reference/examples.md).
4. Reference the appropriate topology page ([Pyramid](topologies/pyramid.md) or [Mesh](topologies/mesh.md)).

---

## Contributing Documentation

Documentation lives in `docs/` and is built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

```bash
# Install docs dependencies
pip install mkdocs-material

# Serve locally (hot reload)
mkdocs serve

# Build static site
mkdocs build
```

When writing docs:

- Use the [documentation guidelines](https://github.com/graphsentinel/agentic-lab/blob/main/.local/agentic_lab_documentation_guidelines.md) as the canonical term reference.
- Label content with `[IMPLEMENTED]`, `[PILOT-VALIDATED]`, `[IN DEVELOPMENT]`, or `[RESEARCH]`.
- Include YAML examples for every concept.
- Cross-reference related pages using relative Markdown links.

---

## Contributing Generator Adapters

To add support for a new agent framework:

1. Create `src/agent_lab/generators/<framework_name>.py`.
2. Implement `GeneratorAdapter` from `base.py`.
3. Register the adapter in `src/agent_lab/generators/registry.py`.
4. Add tests in `tests/test_generators/`.
5. Add `[framework_name]` as an optional extra in `pyproject.toml` if it requires additional dependencies.

See `src/agent_lab/generators/langchain_python.py` for a reference implementation.

---

## Reporting Security Issues

Please **do not open a public issue** for security vulnerabilities.

Use [GitHub Security Advisories](https://github.com/graphsentinel/agentic-lab/security/advisories)
to report vulnerabilities privately. See [SECURITY.md](https://github.com/graphsentinel/agentic-lab/blob/main/SECURITY.md) for the full policy.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://github.com/graphsentinel/agentic-lab/blob/main/CODE_OF_CONDUCT.md).
By participating, you agree to uphold these standards.
