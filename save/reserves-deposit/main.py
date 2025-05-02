"""
Save Reserves Deposit MCP Server
A FastMCP server for depositing into Save Protocol reserves using Dialect Blink
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

mcp = FastMCP("Save Reserves Deposit MCP")


class ReservesDepositInput(BaseModel):
    reserve_address: str = Field(
        description="Reserve address identifier",
        examples=["8PbodeaosQP19SjYFx855UMqWxH2HynZLdBXmsrbac36"],
    )
    token_mint: str = Field(
        description="Token mint address",
        examples=["So11111111111111111111111111111111111111112"],
    )
    amount: float = Field(
        description="Amount to be deposited",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class ReservesDepositResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=ReservesDepositInput)
def save_reserves_deposit(
    reserve_address: str, token_mint: str, amount: float, tx_sender_pubkey: str
) -> ReservesDepositResponse:
    """
    Deposit into Save Protocol reserves via Dialect Blink.

    Args:
        reserve_address: Reserve address identifier
        token_mint: Token mint address
        amount: Amount to be deposited
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        ReservesDepositResponse: Result of the deposit request
    """
    if not BLINK_CLIENT_KEY:
        return ReservesDepositResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://save.dial.to/reserves?action=deposit&reserveAddress={reserve_address}&tokenMint={token_mint}&amount={amount}"

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return ReservesDepositResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return ReservesDepositResponse(success=False, error=error_message)
    except Exception as e:
        return ReservesDepositResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Save Reserves Deposit MCP enables depositing into Save Protocol reserves via Dialect Blink API.
Provides a simple interface for depositing tokens into Save Protocol.
"""

mcp.prompt_suggestions = [
    "Deposit 25 SOL into Save Protocol",
    "Deposit 100 tokens into Save Protocol reserve",
]

if __name__ == "__main__":
    mcp.run()
