"""
Save Reserves MCP Server
A FastMCP server for interacting with Save Reserves using Dialect Blink
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

mcp = FastMCP("Save Reserves MCP")


class ReservesInput(BaseModel):
    action: Literal["deposit", "withdraw"] = Field(
        description="Action to perform (deposit or withdraw)",
        examples=["deposit", "withdraw"],
    )
    token: str = Field(
        description="Token symbol (e.g., USDC)", examples=["USDC", "SOL"]
    )
    amount: float = Field(
        description="Amount to deposit or withdraw",
        examples=[100, 500, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class ReservesResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=ReservesInput)
def save_reserves(
    action: str, token: str, amount: float, tx_sender_pubkey: str
) -> ReservesResponse:
    """
    Interact with Save Reserves via Dialect Blink.

    Args:
        action: Action to perform (deposit or withdraw)
        token: Token symbol (e.g., USDC)
        amount: Amount to deposit or withdraw
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        ReservesResponse: Result of the reserves request
    """
    if not BLINK_CLIENT_KEY:
        return ReservesResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://save.dial.to/reserves/{token}/{action}/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return ReservesResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return ReservesResponse(success=False, error=error_message)
    except Exception as e:
        return ReservesResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Save Reserves MCP enables interacting with Save Reserves via Dialect Blink API.
Provides a simple interface for depositing and withdrawing from Save Reserves.
"""

mcp.prompt_suggestions = [
    "Deposit 100 USDC to Save Reserves",
    "Withdraw 500 USDC from Save Reserves",
]

if __name__ == "__main__":
    mcp.run()
