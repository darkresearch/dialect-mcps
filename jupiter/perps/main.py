"""
Jupiter Perps MCP Server
A FastMCP server for interacting with Jupiter Perpetuals using Dialect Blink
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

mcp = FastMCP("Jupiter Perps MCP")


class PerpsInput(BaseModel):
    market: str = Field(
        description="Market identifier (e.g., SOL-PERP)",
        examples=["SOL-PERP", "BTC-PERP"],
    )
    side: Literal["long", "short"] = Field(
        description="Position side (long or short)", examples=["long", "short"]
    )
    size: float = Field(
        description="Size of the position in USD",
        examples=[100, 500, 1000],
        gt=0,  # Size must be greater than 0
    )
    leverage: float = Field(
        description="Leverage to use (e.g., 5 for 5x)",
        examples=[1, 5, 10],
        ge=1,  # Leverage must be at least 1
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class PerpsResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=PerpsInput)
def jupiter_perps(
    market: str, side: str, size: float, leverage: float, tx_sender_pubkey: str
) -> PerpsResponse:
    """
    Open a perpetual position on Jupiter via Dialect Blink.

    Args:
        market: Market identifier (e.g., SOL-PERP)
        side: Position side (long or short)
        size: Size of the position in USD
        leverage: Leverage to use (e.g., 5 for 5x)
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        PerpsResponse: Result of the perps request
    """
    if not BLINK_CLIENT_KEY:
        return PerpsResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://jupiter.dial.to/perps/{market}/{side}?size={size}&leverage={leverage}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return PerpsResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return PerpsResponse(success=False, error=error_message)
    except Exception as e:
        return PerpsResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Jupiter Perps MCP enables opening perpetual positions on Jupiter via Dialect Blink API.
Provides a simple interface for executing perpetual trades on Jupiter.
"""

mcp.prompt_suggestions = [
    "Open a 5x long position on SOL-PERP with 100 USD",
    "Create a short position on BTC-PERP with 10x leverage",
]

if __name__ == "__main__":
    mcp.run()
