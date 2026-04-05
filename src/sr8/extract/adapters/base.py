from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sr8.extract.signals import ExtractedDimensions
from sr8.models.extraction_trace import ExtractionTrace

if TYPE_CHECKING:
    from sr8.models.compile_config import CompileConfig


class ExtractionAdapter(ABC):
    name: str

    @abstractmethod
    def extract(
        self,
        normalized_source: str,
        config: CompileConfig | None = None,
    ) -> tuple[ExtractedDimensions, ExtractionTrace]:
        raise NotImplementedError
