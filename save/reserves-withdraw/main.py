"""
Save Reserves Withdraw MCP Server
A FastMCP server for withdrawing from Save Protocol reserves using Dialect Blink
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

mcp = FastMCP("Save Reserves Withdraw MCP")


class ReservesWithdrawInput(BaseModel):
    reserve_address: str = Field(
        description="Reserve address identifier",
        examples=["8PbodeaosQP19SjYFx855UMqWxH2HynZLdBXmsrbac36"],
    )
    token_mint: str = Field(
        description="Token mint address",
        examples=["So11111111111111111111111111111111111111112"],
    )
    amount: float = Field(
        description="Amount to be withdrawn",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class ReservesWithdrawResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=ReservesWithdrawInput)
def save_reserves_withdraw(
    reserve_address: str, token_mint: str, amount: float, tx_sender_pubkey: str
) -> ReservesWithdrawResponse:
    """
    Withdraw from Save Protocol reserves via Dialect Blink.

    Args:
        reserve_address: Reserve address identifier
        token_mint: Token mint address
        amount: Amount to be withdrawn
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        ReservesWithdrawResponse: Result of the withdraw request
    """
    if not BLINK_CLIENT_KEY:
        return ReservesWithdrawResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://save.dial.to/reserves?action=withdraw&reserveAddress={reserve_address}&tokenMint={token_mint}&amount={amount}"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return ReservesWithdrawResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return ReservesWithdrawResponse(success=False, error=error_message)
    except Exception as e:
        return ReservesWithdrawResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Save Reserves Withdraw MCP enables withdrawing from Save Protocol reserves via Dialect Blink API.
Provides a simple interface for withdrawing tokens from Save Protocol.
"""

mcp.prompt_suggestions = [
    "Withdraw 25 SOL from Save Protocol",
    "Withdraw 100 tokens from Save Protocol reserve",
]

if __name__ == "__main__":
    mcp.run()
