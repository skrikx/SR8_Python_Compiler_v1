from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact

Renderer = Callable[[IntentArtifact], str]


@dataclass(frozen=True)
class TransformTargetSpec:
    target: str
    description: str
    renderer: Renderer
    compatible_profiles: tuple[str, ...]


@dataclass(frozen=True)
class TransformResult:
    derivative: DerivativeArtifact
    target: TransformTargetSpec
