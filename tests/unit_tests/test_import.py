"""Unit tests for langchain_islo imports."""


def test_import() -> None:
    """Test that the package can be imported."""
    from langchain_islo import IsloSandbox  # noqa: PLC0415

    assert IsloSandbox is not None


def test_sandbox_is_subclass() -> None:
    """Test IsloSandbox subclasses BaseSandbox."""
    from deepagents.backends.sandbox import BaseSandbox  # noqa: PLC0415

    from langchain_islo import IsloSandbox  # noqa: PLC0415

    assert issubclass(IsloSandbox, BaseSandbox)
