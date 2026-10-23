# langchain-islo (first prototype)

> **Superseded.** This was the first prototype (June 2026) of an Islo sandbox backend for LangChain Deep Agents. The published package is developed at [islo-labs/langchain-islo](https://github.com/islo-labs/langchain-islo) (`pip install langchain-islo`). This repository is archived for reference.

Islo ([islo.dev](https://islo.dev), the author's employer) provides cloud sandboxes; this backend runs Deep Agents tool calls inside one. By [Yossi Eliaz](https://yossieliaz.netlify.app/).

## Quick install

```bash
pip install langchain-islo
```

```python
from islo import Islo
from langchain_islo import IsloSandbox

client = Islo()
sandbox = client.sandboxes.create_sandbox(
    name="langchain-demo",
    image="docker.io/library/ubuntu:24.04",
    vcpus=2,
    memory_mb=4096,
)
backend = IsloSandbox(client=client, sandbox=sandbox)

result = backend.execute("python --version")
print(result.output)

# Clean up when done
client.sandboxes.delete_sandbox(sandbox_name=sandbox.name)
```

## Usage with Deep Agents

```python
from islo import Islo
from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_islo import IsloSandbox

client = Islo()
sandbox = client.sandboxes.create_sandbox(
    name="agent-workspace",
    vcpus=4,
    memory_mb=8192,
)
backend = IsloSandbox(client=client, sandbox=sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-6"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)

try:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a small Python package and run pytest",
                }
            ]
        }
    )
finally:
    client.sandboxes.delete_sandbox(sandbox_name=sandbox.name)
```

## File operations (upload / download)

Use the native fast paths:

```python
backend.upload_files(
    [
        ("/src/main.py", b"print('hi from islo')\n"),
        ("/requirements.txt", b"requests\n"),
    ]
)

files = backend.download_files(["/src/main.py"])
print(files[0].content)
```

## License

MIT

## Upstream proposal

An upstream proposal to add this backend to Deep Agents ([langchain-ai/deepagents#3775](https://github.com/langchain-ai/deepagents/pull/3775), [#3776](https://github.com/langchain-ai/deepagents/issues/3776)) was closed without merge.
