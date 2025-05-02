# Jupiter DAO MCP Server

A FastMCP server for interacting with Jupiter DAO via Dialect Blink.

## Features

- Simple MCP interface for Jupiter DAO interactions
- Support for voting on proposals
- Support for claiming rewards
- Support for staking tokens
- Handles Dialect Blink integration transparently
- Easy to configure and deploy

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/darkresearch/dialect-mcps.git
   cd dialect-mcps/jupiter/dao
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
fastmcp install main.py --name "Jupiter DAO"
```

### Example Requests

The MCP exposes a single `jupiter_dao` tool which accepts the following parameters:

- `action`: DAO action to perform ("vote", "claim", or "stake")
- `proposal_id`: Proposal ID (required for vote action)
- `vote_type`: Vote type ("for" or "against", required for vote action)
- `amount`: Amount to stake (required for stake action)
- `tx_sender_pubkey`: Solana account public key of the transaction sender

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLINK_CLIENT_KEY` | Dialect Blink API client key | (Required) |
| `BIN_UUID` | UUID for the _bin parameter | 6874794c-513e-456f-801f-5957a82e068e |

## License

MIT
