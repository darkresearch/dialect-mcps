# Dialect MCPs

A collection of MCP servers for various Dialect Solana Blinks.

## Structure

The repository is organized by organization and MCP:

```
dialect-mcps/
  ├── lulo/
  │   ├── deposit/
  │   └── withdraw/
  ├── kamino/
  │   ├── deposit/
  │   └── withdraw/
  ├── meteora/
  │   ├── add-liquidity/
  │   ├── remove-liquidity/
  │   └── launch-token/
  ├── jupiter/
  │   ├── swap/
  │   ├── perps/
  │   └── dao/
  ├── drift/
  │   ├── perps/
  │   └── vaults/
  ├── save/
  │   └── reserves/
  ├── marginfi/
  │   ├── supply/
  │   └── withdraw/
  └── raydium/
      ├── add-liquidity/
      ├── create-position/
      └── staking/
```

Each MCP is an independent FastMCP server for a specific Dialect Solana Blink.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

Each MCP can be installed and run independently. See the README.md in each MCP directory for specific instructions.
