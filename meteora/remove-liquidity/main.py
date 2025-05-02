"""
Meteora Remove Liquidity MCP Server
A FastMCP server for removing liquidity from Meteora DLMM pools using Dialect Blink
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

mcp = FastMCP("Meteora Remove Liquidity MCP")


class RemoveLiquidityInput(BaseModel):
    dlmm_pool: str = Field(
        description="DLMM Pool ID (e.g., 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6)",
        examples=["5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6"],
    )
    amount: float = Field(
        description="Percentage of liquidity to be removed (e.g., 50 for 50%)",
        examples=[25, 50, 100],
        gt=0,  # Amount must be greater than 0
        le=100,  # Amount must be less than or equal to 100 (percentage)
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class RemoveLiquidityResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=RemoveLiquidityInput)
def meteora_remove_liquidity(
    dlmm_pool: str, amount: float, tx_sender_pubkey: str
) -> RemoveLiquidityResponse:
    """
    Remove liquidity from a Meteora DLMM pool via Dialect Blink.

    Args:
        dlmm_pool: DLMM Pool ID (e.g., 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6)
        amount: Percentage of liquidity to be removed (e.g., 50 for 50%)
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        RemoveLiquidityResponse: Result of the remove liquidity request
    """
    if not BLINK_CLIENT_KEY:
        return RemoveLiquidityResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://meteora.dial.to/api/actions/dlmm/{dlmm_pool}?action=remove-liquidity&amount={amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return RemoveLiquidityResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return RemoveLiquidityResponse(success=False, error=error_message)
    except Exception as e:
        return RemoveLiquidityResponse(
            success=False, error=f"Unexpected error: {str(e)}"
        )


mcp.description = """
Meteora Remove Liquidity MCP enables removing liquidity from Meteora DLMM pools via Dialect Blink API.
Provides a simple interface for executing liquidity removals from DLMM pools.
"""

mcp.prompt_suggestions = [
    "Remove 50% of my liquidity from Meteora DLMM pool",
    "Remove liquidity from Meteora pool 5rCf1DM8LjKTw4YqhnoLcngyZYeNnQqztScTogYHAS6",
]

if __name__ == "__main__":
    mcp.run()
