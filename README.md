# publicsafetyapi-mcp

<!-- Links this package to its entry in the official MCP registry -->
mcp-name: dev.publicsafetyapi/publicsafetyapi-mcp

MCP server for [publicsafetyapi.dev](https://publicsafetyapi.dev) — US police stations, fire departments, EMS bases, and hospitals for AI agents.

Expose public safety facility lookups as tools to any MCP-compatible AI assistant (Claude, Cursor, Copilot, etc.). Built on federal HIFLD, USFA, and CMS data — public domain, commercially usable.

## Installation

```bash
pip install publicsafetyapi-mcp
```

Or run directly with `uvx` (no install needed):

```bash
uvx publicsafetyapi-mcp
```

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "publicsafetyapi": {
      "command": "uvx",
      "args": ["publicsafetyapi-mcp"],
      "env": {
        "PUBLICSAFETYAPI_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Cursor / other MCP clients

```json
{
  "mcpServers": {
    "publicsafetyapi": {
      "command": "uvx",
      "args": ["publicsafetyapi-mcp"],
      "env": {
        "PUBLICSAFETYAPI_KEY": "your_api_key_here"
      }
    }
  }
}
```

Get a free API key at [publicsafetyapi.dev](https://publicsafetyapi.dev) — 500 requests/month, no credit card.

## Available Tools

| Tool | Description |
|------|-------------|
| `find_stations_near_address` | Find the nearest facilities to a US street address |
| `find_stations_near_coordinates` | Same, but from a lat/lng (skips geocoding) |
| `get_station` | Full record for one facility by ID |
| `list_stations` | List/search facilities by type, state, name, or ZIP |
| `get_jurisdiction` | Which city and county contain a location |
| `get_state_summary` | Facility counts by type for a state |

Facility types: `fire`, `police`, `ems`, `hospital`.

## Examples

Once configured, you can ask your AI assistant:

> "What's the closest fire station to 350 Fifth Ave, New York?"

> "How many hospitals are in Montana, and which have trauma centers?"

> "I'm building an emergency-response app — find every police and fire station within 5 miles of downtown Austin."

The assistant calls the matching tool and gets structured JSON back — addresses, phone numbers, coordinates, and for hospitals, beds, trauma level, and ownership.

## Links

- **Website:** [publicsafetyapi.dev](https://publicsafetyapi.dev)
- **PyPI:** [pypi.org/project/publicsafetyapi-mcp](https://pypi.org/project/publicsafetyapi-mcp)
- **REST API docs:** [publicsafetyapi.dev/docs](https://publicsafetyapi.dev/docs)

## License

MIT
