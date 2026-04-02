from __future__ import annotations

from sr8.extract.adapters.base import ExtractionAdapter
from sr8.extract.adapters.model_assisted import ModelAssistedExtractionAdapter
from sr8.extract.adapters.rule_based import RuleBasedExtractionAdapter

EXTRACTION_ADAPTERS: dict[str, ExtractionAdapter] = {
    "rule_based": RuleBasedExtractionAdapter(),
    "model_assisted": ModelAssistedExtractionAdapter(),
}


def get_extraction_adapter(name: str = "rule_based") -> ExtractionAdapter:
    key = name.strip().lower()
    if key not in EXTRACTION_ADAPTERS:
        expected = ", ".join(EXTRACTION_ADAPTERS)
        msg = f"Unknown extraction adapter '{name}'. Expected one of: {expected}."
        raise ValueError(msg)
    return EXTRACTION_ADAPTERS[key]


def list_extraction_adapters() -> tuple[str, ...]:
    return tuple(EXTRACTION_ADAPTERS.keys())
