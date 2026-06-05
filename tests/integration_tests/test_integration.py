"""Integration tests for IsloSandbox using the langchain-tests suite."""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING

import pytest
from langchain_tests.integration_tests import SandboxIntegrationTests

from langchain_islo import IsloSandbox

if TYPE_CHECKING:
    from collections.abc import Iterator

    from deepagents.backends.protocol import SandboxBackendProtocol


@pytest.mark.requires("islo")
class TestIsloSandboxStandard(SandboxIntegrationTests):
    """Standard integration tests for IsloSandbox.

    These exercise the full contract: execute, ls/read/write/edit/glob/grep,
    plus upload/download when implemented.
    """

    @pytest.fixture(scope="class")
    def sandbox(self) -> Iterator[SandboxBackendProtocol]:
        """Yield a live IsloSandbox for the duration of the test class.

        Requires ISLO_API_KEY in the environment and network access to islo.dev.
        The sandbox is cleaned up after the tests.
        """
        api_key = os.environ.get("ISLO_API_KEY")
        if not api_key:
            pytest.skip("ISLO_API_KEY not set; skipping Islo integration tests")

        try:
            from islo import Islo  # noqa: PLC0415
        except ImportError:
            pytest.skip("islo package not installed")

        client = Islo(api_key=api_key)
        # Create a minimal cheap sandbox for tests
        sb = client.sandboxes.create_sandbox(
            name=None,  # let server assign
            image="docker.io/library/ubuntu:24.04",
            vcpus=1,
            memory_mb=1024,
            disk_gb=8,
        )
        backend: SandboxBackendProtocol = IsloSandbox(
            client=client,
            sandbox=sb,
            api_key=api_key,
        )
        try:
            yield backend
        finally:
            # Best-effort cleanup
            with contextlib.suppress(Exception):
                client.sandboxes.delete_sandbox(sandbox_name=sb.name)
