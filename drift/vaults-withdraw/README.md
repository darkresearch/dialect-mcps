# Drift Vaults Withdraw MCP Server

A FastMCP server for withdrawing from Drift vaults via Dialect Blink.

## Features

- Simple MCP interface for withdrawing from Drift vaults
- Support for both strategy vaults and insurance fund vaults
- Configurable withdraw amount
- Handles Dialect Blink integration transparently
- Easy to configure and deploy

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/darkresearch/dialect-mcps.git
   cd dialect-mcps/drift/vaults-withdraw
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
fastmcp install main.py --name "Drift Vaults Withdraw"
```

### Example Requests

The MCP exposes a single `drift_vaults_withdraw` tool which accepts the following parameters:

- `vault_type`: Vault type (strategy-vaults or insurance-fund-vaults)
- `vault_id`: Identifier for a specific vault
- `amount`: Amount to be withdrawn from the vault
- `tx_sender_pubkey`: Solana account public key of the transaction sender

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLINK_CLIENT_KEY` | Dialect Blink API client key | (Required) |
| `BIN_UUID` | UUID for the _bin parameter | 6874794c-513e-456f-801f-5957a82e068e |

## License

MIT
