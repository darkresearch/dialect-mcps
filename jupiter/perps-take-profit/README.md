# Jupiter Perps Take Profit MCP Server

A FastMCP server for setting take profit strategies on positions in Jupiter Perps DEX via Dialect Blink.

## Features

- Simple MCP interface for setting take profit strategies on perpetual positions
- Support for long and short positions
- Configurable price targets
- Handles Dialect Blink integration transparently
- Easy to configure and deploy

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/darkresearch/dialect-mcps.git
   cd dialect-mcps/jupiter/perps-take-profit
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
fastmcp install main.py --name "Jupiter Perps Take Profit"
```

### Example Requests

The MCP exposes a single `jupiter_perps_take_profit` tool which accepts the following parameters:

- `position_type`: Position type to set take profit for (long or short)
- `paying_token`: Token used to open position (e.g., USDC)
- `perp_token`: Token market for the perpetual (e.g., SOL)
- `price`: Price target at which the take profit strategy will execute
- `tx_sender_pubkey`: Solana account public key of the transaction sender

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLINK_CLIENT_KEY` | Dialect Blink API client key | (Required) |
| `BIN_UUID` | UUID for the _bin parameter | 6874794c-513e-456f-801f-5957a82e068e |

## License

MIT
