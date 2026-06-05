# langchain-islo: Islo Sandbox Backend for Deep Agents

This adds first-class support for [Islo](https://islo.dev) sandboxes in the Deep Agents / LangChain ecosystem, exactly mirroring the Daytona (and Modal/Runloop) partner package pattern.

## What was created

- Tiny focused package `langchain-islo` (published intent: `pip install langchain-islo`)
- `IsloSandbox` subclassing `BaseSandbox` from `deepagents.backends.sandbox`
- Only `execute()` + `upload_files()` + `download_files()` + `id` implemented (the rest comes for free from the base class via clever execute scripts)
- Full sync + (via base) async paths
- Native fast file transfer using Islo compute-plane `/files` + `/files-archive` (with bearer from API key exchange)
- pyproject.toml, tests (unit + standard integration via langchain-tests), README, typing marker
- Follows https://docs.langchain.com/oss/python/contributing/integrations-langchain and the daytona reference in https://github.com/langchain-ai/deepagents/tree/main/libs/partners/daytona

## Usage (after `pip install langchain-islo`)

```python
from islo import Islo
from langchain_islo import IsloSandbox
from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic

client = Islo()  # reads ISLO_API_KEY
sandbox = client.sandboxes.create_sandbox(
    name="my-agent-box",
    image="docker.io/library/ubuntu:24.04",
    vcpus=2, memory_mb=4096,
)
backend = IsloSandbox(client=client, sandbox=sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-6"),
    system_prompt="You are a coding agent with a secure Islo sandbox.",
    backend=backend,
)
...
# later
client.sandboxes.delete_sandbox(sandbox_name=sandbox.name)
```

Also works directly for file ops and `backend.execute(...)`.

## CLI / Deep Agents Code

Once this is published + a small wiring PR lands in `deepagents-code` (see the E2B pattern in issue #1739), users get:

```bash
uvx deepagents-cli --sandbox islo ...
# and inside TUI: /install islo
```

## Repo & Publishing

- Recommended home: https://github.com/islo-labs/langchain-islo (or langchain-ai if they prefer to adopt)
- Follow the exact publish steps in the contrib guide.
- Only docs PR needed back to langchain-ai/docs after PyPI release (under integrations/sandboxes or deepagents/sandboxes).

## End-to-end verification performed

- Created fresh Islo sandbox via official `islo` Python SDK + API key obtained from `islo api-key create`
- Exercised `IsloSandbox` against live sandbox:
  - `execute("echo ... && python -c ...")`
  - `upload_files([(path, bytes)])`
  - `download_files([path])` returning correct bytes + error shapes
- Unit tests + ruff clean + format clean
- Structure matches daytona 1:1 (tiny package, inherits fs from BaseSandbox)

## Next for Islo team / Deep Agents

1. Publish to PyPI as `langchain-islo`
2. Open the equivalent of E2B #1739 (or reference this) in langchain-ai/deepagents for:
   - Adding `_IsloProvider` (and entry in `_PROVIDER_TO_WORKING_DIR`, verify_sandbox_deps, etc.) in `libs/code/deepagents_code/integrations/sandbox_factory.py`
   - Updating docs + CLI help text
3. (Optional) Add `langchain-islo` to any "available sandboxes" tables / co-marketing

This is the highest-leverage integration point for Islo in the 2026 LangChain coding agents push.

---

**Files in this skeleton (ready to `git init && git add . && ...`):**

See the checked-in `langchain_islo/`, `pyproject.toml`, `tests/`, `README.md`, `LICENSE`.

Tested on macOS with the live Islo platform (free tier account via browser OAuth flow triggered from `islo login` + Peekaboo-capable automation context).
