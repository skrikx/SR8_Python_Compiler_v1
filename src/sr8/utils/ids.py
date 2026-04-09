from __future__ import annotations

from sr8.utils.hash import stable_text_hash


def build_source_id(source_hash: str) -> str:
    return f"src_{source_hash[:16]}"


def build_artifact_id(source_hash: str, artifact_version: str, compiler_version: str) -> str:
    digest = stable_text_hash(f"{source_hash}:{artifact_version}:{compiler_version}")
    return f"art_{digest[:20]}"


def build_receipt_id(artifact_id: str, source_hash: str) -> str:
    digest = stable_text_hash(f"{artifact_id}:{source_hash}")
    return f"rcpt_{digest[:20]}"


def build_compile_run_id(
    source_hash: str,
    *,
    stage: str = "compile",
    parent_artifact_id: str | None = None,
) -> str:
    digest = stable_text_hash(f"run:{stage}:{source_hash}:{parent_artifact_id or ''}")
    return f"run_{digest[:20]}"


def build_recompile_artifact_id(
    parent_artifact_id: str,
    source_hash: str,
    artifact_version: str,
    compiler_version: str,
    profile: str,
) -> str:
    digest = stable_text_hash(
        f"recompile:{parent_artifact_id}:{source_hash}:{artifact_version}:{compiler_version}:{profile}"
    )
    return f"art_{digest[:20]}"
