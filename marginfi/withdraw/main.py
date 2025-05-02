"""
MarginFi Withdraw MCP Server
A FastMCP server for withdrawing assets from MarginFi using Dialect Blink
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

mcp = FastMCP("MarginFi Withdraw MCP")


class WithdrawInput(BaseModel):
    token: str = Field(
        description="Token symbol to withdraw (e.g., USDC)", examples=["USDC", "SOL"]
    )
    amount: float = Field(
        description="Amount to withdraw",
        examples=[100, 500, 1000],
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
def marginfi_withdraw(
    token: str, amount: float, tx_sender_pubkey: str
) -> WithdrawResponse:
    """
    Withdraw assets from MarginFi via Dialect Blink.

    Args:
        token: Token symbol to withdraw (e.g., USDC)
        amount: Amount to withdraw
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        WithdrawResponse: Result of the withdraw request
    """
    if not BLINK_CLIENT_KEY:
        return WithdrawResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://marginfi.dial.to/withdraw/{token}/{amount}"

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
MarginFi Withdraw MCP enables withdrawing assets from MarginFi via Dialect Blink API.
Provides a simple interface for withdrawing tokens from MarginFi lending pools.
"""

mcp.prompt_suggestions = [
    "Withdraw 100 USDC from MarginFi",
    "Withdraw 1 SOL from MarginFi lending pool",
]

if __name__ == "__main__":
    mcp.run()
