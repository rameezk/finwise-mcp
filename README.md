# Finwise MCP Server

An MCP (Model Context Protocol) server that connects your [Finwise](https://finwiseapp.io) personal finance data to LLMs, enabling natural language queries like:

- "What's my net worth?"
- "How much did I spend on takeaways last month?"
- "Show me all my credit card transactions"
- "What's my budget for groceries?"

## Installation

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "finwise": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rameezk/finwise-mcp", "finwise-mcp"],
      "env": {
        "FINWISE_API_KEY": "your-api-key"
      }
    }
  }
}
```

Restart Claude Desktop (Cmd+Q, then reopen).

### Claude Code

Create `.mcp.json` in your project directory:

```json
{
  "mcpServers": {
    "finwise": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rameezk/finwise-mcp", "finwise-mcp"],
      "env": {
        "FINWISE_API_KEY": "your-api-key"
      }
    }
  }
}
```

Restart Claude Code and approve the MCP server when prompted.

### Using Nix

#### Claude Code

```bash
claude mcp add finwise -- nix run github:rameezk/finwise-mcp
```

#### Manual Configuration

Add to your MCP config:

```json
{
  "mcpServers": {
    "finwise": {
      "command": "nix",
      "args": ["run", "github:rameezk/finwise-mcp"],
      "env": {
        "FINWISE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Getting your API Key

Get your Finwise API key from Settings > API Keys in the [Finwise Dashboard](https://finwiseapp.io).

## Available Tools

### `list_accounts`
List all financial accounts with names, types, currencies, and balances.

**Example:** "What accounts do I have?"

### `list_categories`
List all transaction categories with IDs and names.

**Example:** "What categories do I have?"

### `list_transactions`
List transactions with optional filters and pagination.

**Filters:**
- `from_date` / `to_date` - Date range (YYYY-MM-DD)
- `transaction_types` - Filter by type: `["debit", "credit"]`
- `category_ids` - Filter by category
- `page_number` / `page_size` - Pagination

**Examples:**
- "Show me my transactions from last month"
- "How much did I spend on takeaways?"
- "List all my credit card debits"

### `get_category_budgets`
Get budget totals grouped by category and transaction type.

**Example:** "What's my budget for groceries?"

### `get_net_worth`
Get aggregated net worth over time with historical snapshots.

**Example:** "What's my net worth?"

---

## Development

### Prerequisites

- [Nix](https://nixos.org/) with flakes enabled
- [direnv](https://direnv.net/) (optional, for automatic environment loading)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/rameezk/finwise-mcp.git
   cd finwise-mcp
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your FINWISE_API_KEY
   ```

3. Enter development shell:
   ```bash
   direnv allow  # if using direnv
   # or
   nix develop
   ```

4. Install dependencies:
   ```bash
   uv sync
   ```

### Testing with MCP Inspector

```bash
uv run mcp dev src/finwise_mcp/server.py
```

This opens a web UI where you can test individual tools interactively.

### Running locally for Claude

If developing locally and want to test with Claude, use the full nix path:

```json
{
  "mcpServers": {
    "finwise": {
      "command": "/path/to/.nix-profile/bin/nix",
      "args": ["develop", "/path/to/finwise-mcp", "--command", "uv", "run", "finwise-mcp"],
      "env": {
        "FINWISE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## License

MIT
