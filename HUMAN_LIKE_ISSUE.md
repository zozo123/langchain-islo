# Human-like Issue Text for Deep Agents (copy-paste into the web form)

**Go here and choose the "✨ Feature Request" template:**
https://github.com/langchain-ai/deepagents/issues/new?template=feature-request.yml

Then fill the form with the sections below. Check the boxes manually.

## Submission checklist (check all)
- [x] This is a feature request, not a bug report.
- [x] I searched existing issues and didn't find this feature.
- [x] I checked the docs and README for existing functionality.
- [x] This request applies to this repo (deepagents) and not an external package.

## Area (Required)
- [x] deepagents (SDK)
- [x] cli
- [x] code
- [ ] Other / not sure / general

## Feature description
Hey folks,

I've been using Islo (islo.dev) a lot for running AI coding agents in secure, fast sandboxes — it's been really handy with things like crabbox for agent workflows.

The official Python SDK is solid, and I'd love to bring that same experience into Deep Agents properly. Right now people have to wire it up manually, but it would be awesome if it was a first-class option like Daytona or Modal.

For example, after `pip install langchain-islo`, users could do:

```bash
deepagents-cli --sandbox islo ...
```

or in code:

```python
from islo import Islo
from langchain_islo import IsloSandbox
from deepagents import create_deep_agent

client = Islo()
sb = client.sandboxes.create_sandbox(...)
backend = IsloSandbox(client=client, sandbox=sb)

agent = create_deep_agent(..., backend=backend)
```

This would make it easy for folks already in the LangChain/Deep Agents world to pick Islo when they need good sandbox support.

Thanks for considering it!

## Proposed solution
The heavy lifting is already done in a small standalone package: https://github.com/zozo123/langchain-islo

It provides `IsloSandbox` that subclasses `BaseSandbox` and only implements `execute()` + the fast native `upload_files`/`download_files` using the official `islo` SDK. Everything else (read_file, write_file, ls, grep, etc.) comes for free from the base class.

To wire it into the CLI and SDK, we just need a thin `_IsloProvider` in `deepagents_code/integrations/sandbox_factory.py` (modeled exactly after the Daytona/Runloop ones).

I've got the changes ready in my fork here: https://github.com/zozo123/deepagents/tree/add-islo-sandbox

The corresponding PR is https://github.com/langchain-ai/deepagents/pull/3775 (it's currently closed pending an approved issue, per the process).

## Additional context
- Matches the partner package pattern perfectly (see langchain-daytona etc.).
- Related to the E2B sandbox effort in #1739.
- Package has been tested end-to-end with real Islo sandboxes for exec + file ops.
- All under my personal account (zozo123) as requested — no org forks for the package itself.

Happy to jump on a call or iterate on the implementation if needed. Would appreciate assignment so we can move the PR forward.

(Prepared with help from the agent, but posted by me as a real request.)
