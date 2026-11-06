# ziwei-mcp

**Zi Wei Dou Shu · 紫微斗数 · 紫微斗數 · 자미두수**

[Shunshi.AI](https://shunshi.ai) local calculation core + Model Context Protocol server.
Python 3.11+, MIT. No API key, database connection or hosted LLM is required.

Local natal charts with twelve palaces, stars, brightness and transformations. Two named algorithms: `default` and `zhongzhou`. Core derived from iztro under MIT; see NOTICE. Lunar New Year is the default year boundary. Late 子时 uses the existing engine default (forward day). No solar-time correction: provide the intended date/hour.

## Install and connect

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) from its official source. Add this configuration to an MCP client supporting stdio (Claude Desktop, Cursor, Cline or Codex):

```json
{
  "mcpServers": {
    "shunshi-ziwei": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/shunshi-ai/ziwei-mcp@v0.1.0",
        "shunshi-ziwei-mcp"
      ]
    }
  }
}
```

This uses a tagged GitHub source release, **not a PyPI package**. Dependencies are installed from PyPI by uv; the source tag is pinned. Restart the client after adding the server.

For a local checkout:

```bash
git clone https://github.com/shunshi-ai/ziwei-mcp.git
cd ziwei-mcp
uv sync --locked
uv run shunshi-ziwei-mcp
```

The server speaks JSON-RPC on stdout; it intentionally does not print a welcome message.

## Tools

- `getZiweiChart` — inspect its MCP schema for validated parameters.

Example parameters for `getZiweiChart`:

```json
{
  "date": "1990-03-24",
  "hour": 10,
  "gender": "男"
}
```

Results include a source URL. Computed values and reference text are separate from the calling AI's interpretation; this server does not promise future outcomes.

## Structure and development

`packages/core/src/` contains the reusable core; `src/shunshi_ziwei_mcp/` contains the MCP adapter. Both ship in one wheel, so no unpublished sibling package is needed. The core can be imported without starting MCP. Calculation provenance is documented in [SOURCE.md](SOURCE.md).

```bash
uv sync --locked
uv run pytest -q
uv build
```

Tests include a real stdio MCP client handshake, tool calls, invalid inputs and recovery. Core reference tests are included where available. No production services are contacted.

## Privacy and license

Inputs stay in the local process; there is no product telemetry. Your MCP client's own model provider may receive tool inputs and outputs according to that client's configuration. Standard Python package installation downloads dependencies. Images, where present, are links; opening them is a separate client action.

MIT © 2026 Shunshi.AI. Preserve any upstream copyright in NOTICE.

Website: [https://shunshi.ai](https://shunshi.ai)

## CI template

`docs/github-actions-test.yml` is a ready-to-use GitHub Actions template for Python 3.11–3.13. It is not enabled in this initial release because the publishing credential does not have workflow scope. Tests and installation checks were run locally; enabling hosted CI is a separate step.
