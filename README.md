# AI News Bot
Receive weekly notifications about news on a specific topic : it can be a customer, a technology, a country, ...

This AI News Bot leverage the following technologies :
- [N8N](https://n8n.io/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Fast MCP and Python for the MCP Server](https://gofastmcp.com/getting-started/welcome)
- [APIs for the Webex messaging](https://developer.webex.com/messaging/docs/api/v1/messages/create-a-message)
- [RSS for the Google news](https://news.google.com/rss)

## What to expect ?
<img width="324" height="533" alt="image" src="https://github.com/user-attachments/assets/49f4c002-143f-44ea-9e38-10ea8d236824" />


## How it works ?
<img width="802" height="365" alt="image" src="https://github.com/user-attachments/assets/7bc4b3d7-f1f4-42a2-a18b-1052bcca0349" />


## Prequisites
- LLM API key (Mistral AI, Gemini, ...)
- Webex Bot : https://developer.webex.com/messaging/docs/bots
- N8N deployed, either cloud or on-prem

## Get started

Install uv (recommended Python package manager)
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies and set up environment
```
uv venv && source .venv/bin/activate
uv pip install -r pyproject.toml
```

Run the basic MCP server This uses the Tavily API to expose a simple web_search tool.
```
uv run mcp_server.py
```

The MCP server will be available at:
```
http://localhost:3000/mcp/
```

[Then import the N8N workflow on N8N
](https://docs.n8n.io/courses/level-one/chapter-6/),

The N8N node needs to have access to the MCP server URL (http://localhost:3000/mcp/),

If you are using the N8N Cloud, and using an on-prem MCP server, [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) can be an option to expose securely your MCP servers with HTTPS
