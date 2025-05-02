# Raydium Create Position MCP Server

A FastMCP server for creating positions in Raydium concentrated liquidity pools via Dialect Blink.

## Features

- Simple MCP interface for Raydium concentrated liquidity positions
- Support for custom price ranges
- Handles Dialect Blink integration transparently
- Easy to configure and deploy

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/darkresearch/dialect-mcps.git
   cd dialect-mcps/raydium/create-position
   ```

2. Install dependencies using uv:
   ```bash
   uv venv
   uv pip install -e .
   ```

3. Create a `.env` file with your Dialect Blink API key:
   ```bash
   echo "BLINK_CLIENT_KEY=your_blink_client_key" > .env
   ```

## Usage

### Running the MCP Server

You can run the server directly:

```bash
python main.py
```

Or use FastMCP's dev mode for testing:

```bash
fastmcp dev main.py
```

### Installing in Claude Desktop

To make the MCP available in Claude Desktop:

```bash
fastmcp install main.py --name "Raydium Create Position"
```

### Example Requests

The MCP exposes a single `raydium_create_position` tool which accepts the following parameters:

- `pool_id`: Pool ID for the Raydium concentrated liquidity pool
- `price_lower`: Lower price bound for the position
- `price_upper`: Upper price bound for the position
- `amount_a`: Amount of token A to add
- `amount_b`: Amount of token B to add
- `tx_sender_pubkey`: Solana account public key of the transaction sender

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLINK_CLIENT_KEY` | Dialect Blink API client key | (Required) |
| `BIN_UUID` | UUID for the _bin parameter | 6874794c-513e-456f-801f-5957a82e068e |

## License

MIT
