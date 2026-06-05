"""Top level import smoke test (mirrors daytona partner layout)."""

from langchain_islo import IsloSandbox


def test_top_level_import() -> None:
    assert IsloSandbox is not None
