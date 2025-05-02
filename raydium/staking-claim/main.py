"""
Raydium Staking Claim MCP Server
A FastMCP server for claiming rewards from Raydium staking using Dialect Blink
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

mcp = FastMCP("Raydium Staking Claim MCP")


class StakingClaimInput(BaseModel):
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class StakingClaimResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=StakingClaimInput)
def raydium_staking_claim(tx_sender_pubkey: str) -> StakingClaimResponse:
    """
    Claim rewards from Raydium staking via Dialect Blink.

    Args:
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        StakingClaimResponse: Result of the claim request
    """
    if not BLINK_CLIENT_KEY:
        return StakingClaimResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = "https://raydium.dial.to/staking?action=claim"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return StakingClaimResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return StakingClaimResponse(success=False, error=error_message)
    except Exception as e:
        return StakingClaimResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Raydium Staking Claim MCP enables claiming rewards from Raydium staking via Dialect Blink API.
Provides a simple interface for claiming staking rewards.
"""

mcp.prompt_suggestions = [
    "Claim my RAY staking rewards",
    "Claim rewards from Raydium staking",
]

if __name__ == "__main__":
    mcp.run()
