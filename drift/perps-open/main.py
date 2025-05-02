"""
Drift Perps Open MCP Server
A FastMCP server for opening positions in Drift Perps DEX using Dialect Blink
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

mcp = FastMCP("Drift Perps Open MCP")


class PerpsOpenInput(BaseModel):
    perp_token: str = Field(
        description="Token market for the perpetual",
        examples=["SOL"],
    )
    position_type: str = Field(
        description="Specifies which position is to be opened",
        examples=["long", "short"],
    )
    paying_token: str = Field(
        description="Token to be used to open position",
        examples=["USDC"],
    )
    amount: float = Field(
        description="Amount to be deposited",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    leverage: float = Field(
        description="Leverage multiplier to be used",
        examples=[10, 20, 50],
        gt=0,  # Leverage must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class PerpsOpenResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=PerpsOpenInput)
def drift_perps_open(
    perp_token: str,
    position_type: str,
    paying_token: str,
    amount: float,
    leverage: float,
    tx_sender_pubkey: str,
) -> PerpsOpenResponse:
    """
    Open a perps position in Drift Perps DEX via Dialect Blink.

    Args:
        perp_token: Token market for the perpetual (e.g., SOL)
        position_type: Specifies which position is to be opened (e.g., long, short)
        paying_token: Token to be used to open position (e.g., USDC)
        amount: Amount to be deposited
        leverage: Leverage multiplier to be used
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        PerpsOpenResponse: Result of the open position request
    """
    if not BLINK_CLIENT_KEY:
        return PerpsOpenResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://drift.dial.to/perps/{perp_token}-PERP/open?positionType={position_type}&payingToken={paying_token}&amount={amount}&leverage={leverage}"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return PerpsOpenResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return PerpsOpenResponse(success=False, error=error_message)
    except Exception as e:
        return PerpsOpenResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Drift Perps Open MCP enables opening positions in Drift Perps DEX via Dialect Blink API.
Provides a simple interface for opening long or short positions with specified leverage.
"""

mcp.prompt_suggestions = [
    "Open a long SOL position with 10x leverage using 25 USDC",
    "Open a short SOL position with 20x leverage using 100 USDC",
]

if __name__ == "__main__":
    mcp.run()
