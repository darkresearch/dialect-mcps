"""
Raydium Staking Unstake MCP Server
A FastMCP server for unstaking RAY from Raydium using Dialect Blink
"""

import os
import urllib.parse
from typing import Annotated, Optional

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

load_dotenv()

BLINK_CLIENT_KEY = os.getenv("BLINK_CLIENT_KEY")
BIN_UUID = os.getenv("BIN_UUID", "6874794c-513e-456f-801f-5957a82e068e")

mcp = FastMCP("Raydium Staking Unstake MCP")


class StakingUnstakeInput(BaseModel):
    amount: float = Field(
        description="Amount of RAY to unstake",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class StakingUnstakeResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=StakingUnstakeInput)
def raydium_staking_unstake(amount: float, tx_sender_pubkey: str) -> StakingUnstakeResponse:
    """
    Unstake RAY from Raydium via Dialect Blink.

    Args:
        amount: Amount of RAY to unstake
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        StakingUnstakeResponse: Result of the unstake request
    """
    if not BLINK_CLIENT_KEY:
        return StakingUnstakeResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://raydium.dial.to/staking?action=unstake&amount={amount}"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return StakingUnstakeResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return StakingUnstakeResponse(success=False, error=error_message)
    except Exception as e:
        return StakingUnstakeResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Raydium Staking Unstake MCP enables unstaking RAY tokens from Raydium via Dialect Blink API.
Provides a simple interface for unstaking RAY tokens.
"""

mcp.prompt_suggestions = [
    "Unstake 25 RAY from Raydium",
    "Unstake 100 RAY tokens",
]

if __name__ == "__main__":
    mcp.run()
