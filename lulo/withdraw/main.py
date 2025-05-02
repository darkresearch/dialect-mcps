"""
Lulo Withdraw MCP Server
A FastMCP server for withdrawing funds from Lulo using Dialect Blink
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

mcp = FastMCP("Lulo Withdraw MCP")


class WithdrawInput(BaseModel):
    symbol: str = Field(
        description="Symbol of the token to withdraw (e.g., USDC)",
        examples=["USDC", "SOL"],
    )
    amount: float = Field(
        description="Amount of the token to withdraw",
        examples=[100, 1.0, 10.0],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class WithdrawResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=WithdrawInput)
def lulo_withdraw(
    symbol: str, amount: float, tx_sender_pubkey: str
) -> WithdrawResponse:
    """
    Withdraw funds from Lulo via Dialect Blink.

    Args:
        symbol: Symbol of the token to withdraw (e.g., USDC)
        amount: Amount of the token to withdraw
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        WithdrawResponse: Result of the withdraw request
    """
    if not BLINK_CLIENT_KEY:
        return WithdrawResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://lulo.dial.to/api/actions/withdraw/{symbol}/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return WithdrawResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return WithdrawResponse(success=False, error=error_message)
    except Exception as e:
        return WithdrawResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Lulo Withdraw MCP enables withdrawing funds from Lulo via Dialect Blink API.
Provides a simple interface for executing withdrawals of Solana-based tokens.
"""

mcp.prompt_suggestions = [
    "Withdraw 100 USDC from Lulo",
    "Withdraw 1 SOL from my Lulo account",
]

if __name__ == "__main__":
    mcp.run()
