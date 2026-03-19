from __future__ import annotations

from sr8.models.base import SR8Model


class SchemaVersion(SR8Model):
    canonical_schema: str = "1.0.0"
    derivative_schema: str = "1.0.0"
