"""Registry for code-generation adapters.

Adapters register themselves by framework name so the CLI can look them up
at generation time based on the ASL spec's `target_framework` field.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_lab.generators.base import GeneratorAdapter


class GeneratorRegistry:
    """Central registry mapping framework names to generator adapters."""

    _adapters: dict[str, type[GeneratorAdapter]] = {}

    @classmethod
    def register(cls, name: str, adapter_cls: type[GeneratorAdapter]) -> None:
        """Register a generator adapter under the given framework name."""
        cls._adapters[name] = adapter_cls

    @classmethod
    def get(cls, name: str) -> type[GeneratorAdapter]:
        """Look up a registered adapter by framework name.

        Raises:
            KeyError: If no adapter is registered for the given name.
        """
        if name not in cls._adapters:
            available = ", ".join(sorted(cls._adapters)) or "(none)"
            raise KeyError(
                f"No generator adapter registered for '{name}'. "
                f"Available adapters: {available}"
            )
        return cls._adapters[name]

    @classmethod
    def available(cls) -> list[str]:
        """Return sorted list of registered adapter names."""
        return sorted(cls._adapters)
