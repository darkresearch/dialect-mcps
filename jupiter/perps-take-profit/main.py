"""
Jupiter Perps Take Profit MCP Server
A FastMCP server for setting take profit on positions in Jupiter Perps DEX using Dialect Blink
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

mcp = FastMCP("Jupiter Perps Take Profit MCP")


class PerpsTakeProfitInput(BaseModel):
    position_type: Literal["long", "short"] = Field(
        description="Position type to set take profit for (long or short)",
        examples=["long", "short"],
    )
    paying_token: str = Field(
        description="Token used to open position", examples=["USDC"]
    )
    perp_token: str = Field(
        description="Token market for the perpetual", examples=["SOL", "BTC"]
    )
    price: float = Field(
        description="Price target at which the take profit strategy will execute",
        examples=[136, 200, 50000],
        gt=0,  # Price must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class PerpsTakeProfitResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=PerpsTakeProfitInput)
def jupiter_perps_take_profit(
    position_type: str,
    paying_token: str,
    perp_token: str,
    price: float,
    tx_sender_pubkey: str,
) -> PerpsTakeProfitResponse:
    """
    Set a take profit strategy on an existing perps position in Jupiter Perps DEX via Dialect Blink.

    Args:
        position_type: Position type to set take profit for (long or short)
        paying_token: Token used to open position
        perp_token: Token market for the perpetual
        price: Price target at which the take profit strategy will execute
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        PerpsTakeProfitResponse: Result of the take profit request
    """
    if not BLINK_CLIENT_KEY:
        return PerpsTakeProfitResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://jupiter.dial.to/perps/{position_type}/{paying_token}-{perp_token}?action=tp&price={price}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return PerpsTakeProfitResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return PerpsTakeProfitResponse(success=False, error=error_message)
    except Exception as e:
        return PerpsTakeProfitResponse(
            success=False, error=f"Unexpected error: {str(e)}"
        )


mcp.description = """
Jupiter Perps Take Profit MCP enables setting take profit strategies on positions in Jupiter Perps DEX via Dialect Blink API.
Provides a simple interface for creating or editing take profit strategies for long or short positions.
"""

mcp.prompt_suggestions = [
    "Set take profit at $136 for a long position in SOL",
    "Create a take profit strategy at $50,000 for a short position in BTC",
]

if __name__ == "__main__":
    mcp.run()
