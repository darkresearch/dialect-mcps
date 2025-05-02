"""
Meteora Add Liquidity MCP Server
A FastMCP server for adding liquidity to Meteora DLMM pools using Dialect Blink
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

mcp = FastMCP("Meteora Add Liquidity MCP")


class AddLiquidityInput(BaseModel):
    dlmm_pool: str = Field(
        description="DLMM Pool ID (e.g., 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6)",
        examples=["5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6"],
    )
    amount: float = Field(
        description="Amount of the base mint token to be deposited",
        examples=[5, 10, 100],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class AddLiquidityResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=AddLiquidityInput)
def meteora_add_liquidity(
    dlmm_pool: str, amount: float, tx_sender_pubkey: str
) -> AddLiquidityResponse:
    """
    Add liquidity to a Meteora DLMM pool via Dialect Blink.

    Args:
        dlmm_pool: DLMM Pool ID (e.g., 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6)
        amount: Amount of the base mint token to be deposited
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        AddLiquidityResponse: Result of the add liquidity request
    """
    if not BLINK_CLIENT_KEY:
        return AddLiquidityResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://meteora.dial.to/api/actions/dlmm/{dlmm_pool}/add-liquidity/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return AddLiquidityResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return AddLiquidityResponse(success=False, error=error_message)
    except Exception as e:
        return AddLiquidityResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Meteora Add Liquidity MCP enables adding liquidity to Meteora DLMM pools via Dialect Blink API.
Provides a simple interface for executing liquidity additions to DLMM pools.
"""

mcp.prompt_suggestions = [
    "Add 5 tokens of liquidity to Meteora DLMM pool",
    "Add liquidity to Meteora pool 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6",
]

if __name__ == "__main__":
    mcp.run()
