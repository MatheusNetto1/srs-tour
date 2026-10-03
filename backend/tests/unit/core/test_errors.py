import math

from app.core.errors import _json_safe


def test_json_safe_replaces_non_finite_floats_with_text() -> None:
    errors = [
        {"loc": ["body", "value"], "input": math.nan},
        {"loc": ["body", "other"], "input": [math.inf, -math.inf, 1.5]},
    ]

    assert _json_safe(errors) == [
        {"loc": ["body", "value"], "input": "nan"},
        {"loc": ["body", "other"], "input": ["inf", "-inf", 1.5]},
    ]


def test_json_safe_keeps_regular_values_untouched() -> None:
    errors = [{"loc": ["body", "name"], "input": "x", "ctx": {"min_length": 1}}]

    assert _json_safe(errors) == errors
