import pytest

from scripts.run_pipeline import pipeline_exit_code


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("SUCCESS", 0),
        ("PARTIAL_SUCCESS", 0),
        ("FAILED", 1),
    ],
)
def test_pipeline_exit_code(status: str, expected: int) -> None:
    assert pipeline_exit_code(status) == expected


def test_unknown_pipeline_status_fails_safely() -> None:
    with pytest.raises(ValueError, match="Unknown pipeline status"):
        pipeline_exit_code("UNKNOWN")
