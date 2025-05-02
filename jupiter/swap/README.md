# Jupiter MCP Server

A FastMCP server for performing token swaps on Jupiter DEX via Dialect Blink.

## Features

- Simple MCP interface for Jupiter swaps
- Supports any token pair available on Jupiter
- Handles Dialect Blink integration transparently
- Easy to configure and deploy

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-org/jupiter-mcp.git
   cd jupiter-mcp
   ```

2. Install dependencies using uv:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Create a `.env` file with your Dialect Blink API key:
   ```bash
   echo "BLINK_CLIENT_KEY=your_blink_client_key" > .env
   echo "BIN_UUID=6874794c-513e-456f-801f-5957a82e068e" >> .env
   ```

## Usage

### Running the MCP Server

You can run the server directly:

```bash
python jupiter_mcp.py
```

Or use FastMCP's dev mode for testing:

```bash
fastmcp dev jupiter_mcp.py
```

### Installing in Claude Desktop

To make the MCP available in Claude Desktop:

```bash
fastmcp install jupiter_mcp.py --name "Jupiter Swap"
```

### Example Requests

The MCP exposes a single `jupiter_swap` tool which accepts the following parameters:

- `token_in`: Input token symbol (e.g., "SOL")
- `token_out`: Output token symbol (e.g., "DARK") 
- `amount`: Amount of token_in to swap (e.g., 0.1)
- `tx_sender_pubkey`: Solana account public key of the transaction sender

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLINK_CLIENT_KEY` | Dialect Blink API client key | (Required) |
| `BIN_UUID` | UUID for the _bin parameter | 6874794c-513e-456f-801f-5957a82e068e |

## Development

To install development dependencies:

```bash
uv pip install -e ".[dev]"
```

## License

MIT 