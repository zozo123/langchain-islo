# Ready-to-use content for the Feature Request form
# Go to: https://github.com/langchain-ai/deepagents/issues/new?template=feature-request.yml
# Fill the checkboxes and paste the text into the textareas exactly as below.

## Checkboxes (check these):
- [x] This is a feature request, not a bug report.
- [x] I searched existing issues and didn't find this feature.
- [x] I checked the docs and README for existing functionality.
- [x] This request applies to this repo (deepagents) and not an external package.

## Area checkboxes (check these):
- [x] deepagents (SDK)
- [x] cli
- [x] code
- [ ] Other / not sure / general   (or check if needed)

## Feature description (required textarea):
Islo (https://islo.dev) is a production-grade sandbox platform for AI coding agents. It is already integrated in tools like crabbox and has official SDKs (Python, Go, TS).

We want to add first-class Islo support to Deep Agents / deepagents-code / dcode, so users can do:

```bash
pip install langchain-islo
# then
deepagents-cli --sandbox islo ...
```

or programmatically:

```python
from islo import Islo
from langchain_islo import IsloSandbox
from deepagents import create_deep_agent

client = Islo()
sb = client.sandboxes.create_sandbox(...)
backend = IsloSandbox(client=client, sandbox=sb)

agent = create_deep_agent(..., backend=backend)
```

This matches the partner sandbox pattern (Daytona, Modal, Runloop, AgentCore, etc.).

## Proposed solution (optional textarea):
- Publish `langchain-islo` as the standalone integration package (ready: https://github.com/zozo123/langchain-islo)
- Add a thin `_IsloProvider` in `deepagents_code/integrations/sandbox_factory.py` (and update docs/references)
- This enables the `--sandbox islo` flag and dynamic import of the provider when the package is installed.

The implementation of `IsloSandbox` (which only needs to implement `execute` + optional fast `upload_files`/`download_files`, inheriting the rest from `BaseSandbox`) lives in the separate package, per the LangChain integration guidelines.

**Implementation approach:**
The provider follows the established pattern:
- Resolve `ISLO_API_KEY` (with DEEPAGENTS_CODE_ prefix support via resolve_env_var)
- Create `Islo()` client
- In `get_or_create`: create sandbox (or support id in future), poll for ready using exec, return `IsloSandbox(client=..., sandbox=...)`
- `delete` calls the SDK delete
- Added to `_PROVIDER_TO_WORKING_DIR` as `/workspace`
- Added to verify deps and import map as `("langchain_islo", "islo")`

No changes to core deepagents or BaseSandbox needed.

This is a small, isolated addition.

## Additional context (optional textarea):
- Follows the exact structure and code patterns from `langchain-daytona` and other partners.
- See the E2B sandbox backend issue #1739 for the model ticket/process.
- Companion package has been tested end-to-end with the official `islo` Python SDK for create, exec, file ops, etc.
- Wiring changes are ready in this fork/branch: https://github.com/zozo123/deepagents/tree/add-islo-sandbox (PR #3775)

Please assign me (zozo123 / Yossi Eliaz) so the linked PR can be reopened and reviewed.
