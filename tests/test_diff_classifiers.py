from sr8.diff.classifiers import classify_change, classify_impact


def test_diff_classifiers_detect_added_removed_modified() -> None:
    assert classify_change([], ["a"]) == "added"
    assert classify_change(["a"], []) == "removed"
    assert classify_change(["a"], ["b"]) == "modified"
    assert classify_change(["a", "b"], ["b", "a"]) == "unchanged"


def test_diff_classifier_impact_levels() -> None:
    assert classify_impact("scope", "modified") == "high"
    assert classify_impact("objective", "modified") == "medium"
    assert classify_impact("metadata", "modified") == "low"
