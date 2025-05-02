"""
Jupiter Perps Add Collateral MCP Server
A FastMCP server for adding collateral to positions in Jupiter Perps DEX using Dialect Blink
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

mcp = FastMCP("Jupiter Perps Add Collateral MCP")


class PerpsAddCollateralInput(BaseModel):
    position_type: Literal["long", "short"] = Field(
        description="Position type to add collateral to (long or short)",
        examples=["long", "short"],
    )
    paying_token: str = Field(
        description="Token used to open position", examples=["USDC"]
    )
    perp_token: str = Field(
        description="Token market for the perpetual", examples=["SOL", "BTC"]
    )
    amount: float = Field(
        description="Amount of collateral to add",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class PerpsAddCollateralResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=PerpsAddCollateralInput)
def jupiter_perps_add_collateral(
    position_type: str,
    paying_token: str,
    perp_token: str,
    amount: float,
    tx_sender_pubkey: str,
) -> PerpsAddCollateralResponse:
    """
    Add collateral to an existing perps position in Jupiter Perps DEX via Dialect Blink.

    Args:
        position_type: Position type to add collateral to (long or short)
        paying_token: Token used to open position
        perp_token: Token market for the perpetual
        amount: Amount of collateral to add
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        PerpsAddCollateralResponse: Result of the add collateral request
    """
    if not BLINK_CLIENT_KEY:
        return PerpsAddCollateralResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://jupiter.dial.to/perps/{position_type}/{paying_token}-{perp_token}?action=add-collateral&amount={amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return PerpsAddCollateralResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return PerpsAddCollateralResponse(success=False, error=error_message)
    except Exception as e:
        return PerpsAddCollateralResponse(
            success=False, error=f"Unexpected error: {str(e)}"
        )


mcp.description = """
Jupiter Perps Add Collateral MCP enables adding collateral to positions in Jupiter Perps DEX via Dialect Blink API.
Provides a simple interface for adding collateral to long or short positions.
"""

mcp.prompt_suggestions = [
    "Add 25 USDC collateral to a long position in SOL",
    "Add 100 USDC collateral to a short position in BTC",
]

if __name__ == "__main__":
    mcp.run()
