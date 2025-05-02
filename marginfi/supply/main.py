"""
MarginFi Supply MCP Server
A FastMCP server for supplying assets to MarginFi using Dialect Blink
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

mcp = FastMCP("MarginFi Supply MCP")


class SupplyInput(BaseModel):
    token: str = Field(
        description="Token symbol to supply (e.g., USDC)", examples=["USDC", "SOL"]
    )
    amount: float = Field(
        description="Amount to supply",
        examples=[100, 500, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class SupplyResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=SupplyInput)
def marginfi_supply(token: str, amount: float, tx_sender_pubkey: str) -> SupplyResponse:
    """
    Supply assets to MarginFi via Dialect Blink.

    Args:
        token: Token symbol to supply (e.g., USDC)
        amount: Amount to supply
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        SupplyResponse: Result of the supply request
    """
    if not BLINK_CLIENT_KEY:
        return SupplyResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://marginfi.dial.to/supply/{token}/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return SupplyResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return SupplyResponse(success=False, error=error_message)
    except Exception as e:
        return SupplyResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
MarginFi Supply MCP enables supplying assets to MarginFi via Dialect Blink API.
Provides a simple interface for supplying tokens to MarginFi lending pools.
"""

mcp.prompt_suggestions = [
    "Supply 100 USDC to MarginFi",
    "Supply 1 SOL to MarginFi lending pool",
]

if __name__ == "__main__":
    mcp.run()
