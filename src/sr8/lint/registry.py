from __future__ import annotations

from sr8.lint.rules import LINT_RULES, PredicateRule


def list_lint_rules() -> tuple[PredicateRule, ...]:
    return LINT_RULES
