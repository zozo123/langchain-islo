# langchain-islo

[![PyPI - Version](https://img.shields.io/pypi/v/langchain-islo?label=%20)](https://pypi.org/project/langchain-islo/#history) [![PyPI - License](https://img.shields.io/pypi/l/langchain-islo)](https://opensource.org/licenses/MIT) [![PyPI - Downloads](https://img.shields.io/pepy/dt/langchain-islo)](https://pypistats.org/packages/langchain-islo)

Islo sandbox integration for Deep Agents.

Looking for the JS/TS version? Check out the Islo SDK or LangChain.js partners when available.

## Quick Install

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

## 🤔 What is this?

Islo sandbox integration for Deep Agents. Islo provides fast, persistent, agent-optimized cloud sandboxes purpose-built for AI coding agents.

See https://islo.dev and the [Islo docs](https://docs.islo.dev) for signup, authentication (ISLO_API_KEY), and platform details.

## 📕 Releases & Versioning

See our [Releases](https://docs.langchain.com/oss/python/release-policy) and [Versioning](https://docs.langchain.com/oss/python/versioning) policies.

## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see the [Contributing Guide](https://docs.langchain.com/oss/python/contributing/overview).

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

## CLI support (deepagents-code / dcode)

Once published and the provider is wired in deepagents-code (similar to the E2B / langchain-e2b flow), you will be able to do:

```bash
uvx deepagents-cli --sandbox islo ...
# or inside the TUI: /install islo
```

See the E2B sandbox backend issue in langchain-ai/deepagents for the pattern.

## License

MIT

## Integration Status

- Package: https://github.com/zozo123/langchain-islo
- Support PR / Issue in deepagents (LangChain ecosystem): https://github.com/langchain-ai/deepagents/issues/3776 and https://github.com/langchain-ai/deepagents/pull/3775

