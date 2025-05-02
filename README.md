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
  │   ├── dao-claim/
  │   ├── dao-stake/
  │   ├── dao-unstake/
  │   ├── perps-add-collateral/
  │   ├── perps-close/
  │   ├── perps-open/
  │   ├── perps-remove-collateral/
  │   ├── perps-stop-loss/
  │   └── perps-take-profit/
  ├── drift/
  │   ├── perps-open/
  │   ├── perps-close/
  │   ├── vaults-deposit/
  │   └── vaults-withdraw/
  ├── save/
  │   ├── reserves-deposit/
  │   └── reserves-withdraw/
  ├── marginfi/
  │   ├── supply/
  │   └── withdraw/
  └── raydium/
      ├── add-liquidity/
      ├── create-position/
      ├── staking-stake/
      ├── staking-unstake/
      └── staking-claim/
```

Each MCP is an independent FastMCP server for a specific Dialect Solana Blink.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

Each MCP can be installed and run independently. See the README.md in each MCP directory for specific instructions.
