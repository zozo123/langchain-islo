"""Islo sandbox backend implementation for Deep Agents."""

from __future__ import annotations

import os
from typing import cast

import httpx
from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox
from islo import Islo
from islo.custom.auth import exchange_access_key
from islo.custom.exec import exec_and_wait_sync
from islo.types.sandbox_response import SandboxResponse

# HTTP status constants to avoid PLR2004 magic values
_HTTP_OK_MIN = 200
_HTTP_OK_MAX = 300
_HTTP_NOT_FOUND = 404

# Type for the sandbox argument: either a response object from create or its name
IsloSandboxArg = SandboxResponse | str


class IsloSandbox(BaseSandbox):
    """Islo sandbox implementation conforming to SandboxBackendProtocol.

    This implementation inherits all file operation methods from BaseSandbox
    (via execute) and implements execute(), upload_files(), download_files()
    using Islo's native APIs for correctness and performance.

    Example:
        from islo import Islo
        from langchain_islo import IsloSandbox

        client = Islo()
        sandbox = client.sandboxes.create_sandbox(
            name="my-agent-sandbox",
            image="docker.io/library/ubuntu:24.04",
            vcpus=2,
            memory_mb=4096,
        )
        backend = IsloSandbox(client=client, sandbox=sandbox)
        result = backend.execute("python --version")
        print(result.output)
    """

    def __init__(
        self,
        *,
        client: Islo | None = None,
        sandbox: IsloSandboxArg,
        api_key: str | None = None,
        timeout: int = 30 * 60,
    ) -> None:
        """Create a backend wrapping an existing Islo sandbox.

        Args:
            client: An Islo() client instance. If None, one is created (will
                read ISLO_API_KEY from environment).
            sandbox: Either a SandboxResponse returned by create_sandbox(),
                or the sandbox name (str) for an existing sandbox.
            api_key: Optional explicit ISLO_API_KEY. Used for direct file
                transfer calls (upload/download) which require a bearer token.
                Falls back to the key used by client or ISLO_API_KEY env.
            timeout: Default command timeout in seconds.
        """
        self._client = client or Islo()
        if isinstance(sandbox, str):
            self._sandbox_name = sandbox
        else:
            self._sandbox_name = sandbox.name
        self._default_timeout = timeout

        # Capture API key for direct compute-plane file transfers (upload/download).
        self._api_key: str | None = api_key
        if self._api_key is None:
            # Islo client stores it internally in some cases; fall back to env.
            # The client creation already resolved from env if not passed.
            self._api_key = os.environ.get("ISLO_API_KEY")

    @property
    def id(self) -> str:
        """Return the Islo sandbox name (used as stable identifier)."""
        return self._sandbox_name

    def execute(
        self,
        command: str,
        *,
        timeout: int | None = None,
    ) -> ExecuteResponse:
        """Execute a shell command inside the sandbox.

        Uses Islo exec + polling for completion.
        """
        effective_timeout = timeout if timeout is not None else self._default_timeout
        result = exec_and_wait_sync(
            self._client,
            self._sandbox_name,
            ["bash", "-c", command],
            timeout=float(effective_timeout),
        )
        output = result.stdout or ""
        if result.stderr and result.stderr.strip():
            sep = "\n" if output else ""
            output += f"{sep}<stderr>{result.stderr.strip()}</stderr>"
        return ExecuteResponse(
            output=output,
            exit_code=result.exit_code,
            truncated=result.timed_out,
        )

    def _get_bearer_token(self) -> str:
        """Exchange (or refresh) for a short-lived session JWT for compute APIs."""
        key = self._api_key
        if not key:
            msg = (
                "IsloSandbox requires an ISLO_API_KEY (via api_key= kwarg, "
                "ISLO_API_KEY env, or passed when constructing the Islo client) "
                "for upload_files/download_files. Set the env var or pass api_key."
            )
            raise RuntimeError(msg)
        # Access environment via the (private) wrapper; this is the supported
        # way to obtain the control/compute URLs from a live Islo client.
        env = getattr(self._client, "_client_wrapper", None)
        env = getattr(env, "get_environment", lambda: None)() if env else None
        base_url = (
            getattr(env, "control", None)
            or os.environ.get("ISLO_BASE_URL")
            or "https://api.islo.dev"
        )
        data = exchange_access_key(base_url, key)
        token = data.get("session_token") or data.get("session_jwt")
        if not token:
            err_msg = "Failed to obtain session token from Islo auth exchange"
            raise RuntimeError(err_msg)
        return cast("str", token)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Upload files into the sandbox using Islo compute-plane /files endpoint."""
        responses: list[FileUploadResponse] = []
        if not files:
            return responses

        try:
            token = self._get_bearer_token()
        except Exception as exc:  # noqa: BLE001
            for path, _ in files:
                responses.append(
                    FileUploadResponse(path=path, error=f"auth_error: {exc}")
                )
            return responses

        # Access environment via the (private) wrapper (see note in _get_bearer_token).
        env = getattr(self._client, "_client_wrapper", None)
        env = getattr(env, "get_environment", lambda: None)() if env else None
        base = (
            getattr(env, "compute", None)
            or os.environ.get("ISLO_COMPUTE_URL")
            or "https://ca.compute.islo.dev"
        )
        headers = {"Authorization": f"Bearer {token}"}

        with httpx.Client(timeout=120.0) as http:
            for path, content in files:
                if not path.startswith("/"):
                    responses.append(
                        FileUploadResponse(path=path, error="invalid_path")
                    )
                    continue
                fname = path.rsplit("/", 1)[-1] or "upload.bin"
                try:
                    resp = http.post(
                        f"{base}/sandboxes/{self._sandbox_name}/files",
                        params={"path": path},
                        headers=headers,
                        files={"file": (fname, content)},
                    )
                    if _HTTP_OK_MIN <= resp.status_code < _HTTP_OK_MAX:
                        responses.append(FileUploadResponse(path=path, error=None))
                    else:
                        err: str | None = "upload_failed"
                        try:
                            body = resp.json()
                            err = str(body.get("detail") or body.get("error") or err)
                        except Exception:  # noqa: S110, BLE001
                            pass
                        responses.append(FileUploadResponse(path=path, error=err))
                except Exception as exc:  # noqa: BLE001
                    responses.append(
                        FileUploadResponse(path=path, error=str(exc)[:200])
                    )

        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Download files from the sandbox using Islo compute-plane /files endpoint."""
        responses: list[FileDownloadResponse] = []
        if not paths:
            return responses

        try:
            token = self._get_bearer_token()
        except Exception as exc:  # noqa: BLE001
            responses.extend(
                FileDownloadResponse(
                    path=path, content=None, error=f"auth_error: {exc}"
                )
                for path in paths
            )
            return responses

        # Access environment via the (private) wrapper (see note in _get_bearer_token).
        env = getattr(self._client, "_client_wrapper", None)
        env = getattr(env, "get_environment", lambda: None)() if env else None
        base = (
            getattr(env, "compute", None)
            or os.environ.get("ISLO_COMPUTE_URL")
            or "https://ca.compute.islo.dev"
        )
        headers = {"Authorization": f"Bearer {token}"}

        with httpx.Client(timeout=120.0) as http:
            for path in paths:
                if not path.startswith("/"):
                    responses.append(
                        FileDownloadResponse(
                            path=path, content=None, error="invalid_path"
                        )
                    )
                    continue
                try:
                    with http.stream(
                        "GET",
                        f"{base}/sandboxes/{self._sandbox_name}/files",
                        params={"path": path},
                        headers=headers,
                    ) as resp:
                        if _HTTP_OK_MIN <= resp.status_code < _HTTP_OK_MAX:
                            content = b"".join(resp.iter_bytes())
                            responses.append(
                                FileDownloadResponse(
                                    path=path, content=content, error=None
                                )
                            )
                        else:
                            err: str | None = "file_not_found"
                            try:
                                body = resp.json()
                                err = str(
                                    body.get("detail") or body.get("error") or err
                                )
                            except Exception:  # noqa: S110, BLE001
                                pass
                            responses.append(
                                FileDownloadResponse(path=path, content=None, error=err)
                            )
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == _HTTP_NOT_FOUND:
                        responses.append(
                            FileDownloadResponse(
                                path=path, content=None, error="file_not_found"
                            )
                        )
                    else:
                        responses.append(
                            FileDownloadResponse(
                                path=path, content=None, error=str(exc)[:200]
                            )
                        )
                except Exception as exc:  # noqa: BLE001
                    responses.append(
                        FileDownloadResponse(
                            path=path, content=None, error=str(exc)[:200]
                        )
                    )

        return responses
