"""
Kamino Withdraw MCP Server
A FastMCP server for withdrawing from Kamino Lending Markets using Dialect Blink
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

mcp = FastMCP("Kamino Withdraw MCP")


class WithdrawInput(BaseModel):
    market: str = Field(
        description="Market identifier (e.g., DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek)",
        examples=["DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek"],
    )
    reserve: str = Field(
        description="Reserve identifier (e.g., Ga4rZytCpq1unD4DbEJ5bkHeUz9g3oh9AAFEi6vSauXp)",
        examples=["Ga4rZytCpq1unD4DbEJ5bkHeUz9g3oh9AAFEi6vSauXp"],
    )
    amount_type: Literal["percentage", "amount"] = Field(
        description="Type of amount value (percentage or absolute amount)",
        examples=["percentage", "amount"],
    )
    amount: float = Field(
        description="Amount to withdraw (percentage or absolute amount)",
        examples=[25, 50, 100],
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
def kamino_withdraw(
    market: str, reserve: str, amount_type: str, amount: float, tx_sender_pubkey: str
) -> WithdrawResponse:
    """
    Withdraw from Kamino Lending Markets via Dialect Blink.

    Args:
        market: Market identifier (e.g., DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek)
        reserve: Reserve identifier (e.g., Ga4rZytCpq1unD4DbEJ5bkHeUz9g3oh9AAFEi6vSauXp)
        amount_type: Type of amount value (percentage or absolute amount)
        amount: Amount to withdraw (percentage or absolute amount)
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        WithdrawResponse: Result of the withdraw request
    """
    if not BLINK_CLIENT_KEY:
        return WithdrawResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://kamino.dial.to/lending/reserve/{market}/{reserve}/withdraw/{amount_type}/{amount}"

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
Kamino Withdraw MCP enables withdrawing from Kamino Lending Markets via Dialect Blink API.
Provides a simple interface for executing withdrawals from Kamino reserves.
"""

mcp.prompt_suggestions = [
    "Withdraw 25% from Kamino reserve",
    "Withdraw from Kamino lending market",
]

if __name__ == "__main__":
    mcp.run()
