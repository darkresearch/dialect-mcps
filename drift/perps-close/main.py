"""
Drift Perps Close MCP Server
A FastMCP server for closing positions in Drift Perps DEX using Dialect Blink
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

mcp = FastMCP("Drift Perps Close MCP")


class PerpsCloseInput(BaseModel):
    perp_token: str = Field(
        description="Token market for the perpetual",
        examples=["SOL"],
    )
    amount: float = Field(
        description="Amount to close",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class PerpsCloseResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=PerpsCloseInput)
def drift_perps_close(perp_token: str, amount: float, tx_sender_pubkey: str) -> PerpsCloseResponse:
    """
    Close a perps position in Drift Perps DEX via Dialect Blink.

    Args:
        perp_token: Token market for the perpetual (e.g., SOL)
        amount: Amount to close
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        PerpsCloseResponse: Result of the close position request
    """
    if not BLINK_CLIENT_KEY:
        return PerpsCloseResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://drift.dial.to/perps/{perp_token}-PERP/close?amount={amount}"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return PerpsCloseResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return PerpsCloseResponse(success=False, error=error_message)
    except Exception as e:
        return PerpsCloseResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Drift Perps Close MCP enables closing positions in Drift Perps DEX via Dialect Blink API.
Provides a simple interface for closing any open position (long or short).
"""

mcp.prompt_suggestions = [
    "Close my SOL position with 25 units",
    "Close my SOL position with 100 units",
]

if __name__ == "__main__":
    mcp.run()
