"""
Raydium Staking MCP Server
A FastMCP server for staking tokens in Raydium using Dialect Blink
"""

import os
import urllib.parse
from typing import Annotated, Literal, Optional

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv()

BLINK_CLIENT_KEY = os.getenv("BLINK_CLIENT_KEY")
BIN_UUID = os.getenv("BIN_UUID", "6874794c-513e-456f-801f-5957a82e068e")

mcp = FastMCP("Raydium Staking MCP")


class StakingInput(BaseModel):
    action: Literal["stake", "unstake"] = Field(
        description="Action to perform (stake or unstake)",
        examples=["stake", "unstake"],
    )
    pool_id: str = Field(
        description="Pool ID for the Raydium staking pool",
        examples=["58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"],
    )
    amount: float = Field(
        description="Amount to stake or unstake",
        examples=[100, 500, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class StakingResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=StakingInput)
def raydium_staking(
    action: str, pool_id: str, amount: float, tx_sender_pubkey: str
) -> StakingResponse:
    """
    Stake or unstake tokens in Raydium via Dialect Blink.

    Args:
        action: Action to perform (stake or unstake)
        pool_id: Pool ID for the Raydium staking pool
        amount: Amount to stake or unstake
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        StakingResponse: Result of the staking request
    """
    if not BLINK_CLIENT_KEY:
        return StakingResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://raydium.dial.to/staking/{action}/{pool_id}/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return StakingResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return StakingResponse(success=False, error=error_message)
    except Exception as e:
        return StakingResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Raydium Staking MCP enables staking and unstaking tokens in Raydium via Dialect Blink API.
Provides a simple interface for staking operations in Raydium pools.
"""

mcp.prompt_suggestions = [
    "Stake 100 tokens in Raydium pool",
    "Unstake 500 tokens from Raydium staking pool",
]

if __name__ == "__main__":
    mcp.run()
