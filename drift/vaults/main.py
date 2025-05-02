"""
Drift Vaults MCP Server
A FastMCP server for interacting with Drift Vaults using Dialect Blink
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

mcp = FastMCP("Drift Vaults MCP")


class VaultsInput(BaseModel):
    action: Literal["deposit", "withdraw"] = Field(
        description="Action to perform (deposit or withdraw)",
        examples=["deposit", "withdraw"],
    )
    vault_id: str = Field(
        description="Vault identifier",
        examples=["DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek"],
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


class VaultsResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=VaultsInput)
def drift_vaults(
    action: str, vault_id: str, amount: float, tx_sender_pubkey: str
) -> VaultsResponse:
    """
    Interact with Drift Vaults via Dialect Blink.

    Args:
        action: Action to perform (deposit or withdraw)
        vault_id: Vault identifier
        amount: Amount to deposit or withdraw
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        VaultsResponse: Result of the vaults request
    """
    if not BLINK_CLIENT_KEY:
        return VaultsResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://drift.dial.to/vaults/{vault_id}/{action}/{amount}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return VaultsResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return VaultsResponse(success=False, error=error_message)
    except Exception as e:
        return VaultsResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Drift Vaults MCP enables interacting with Drift Vaults via Dialect Blink API.
Provides a simple interface for depositing and withdrawing from Drift Vaults.
"""

mcp.prompt_suggestions = [
    "Deposit 100 USDC to Drift Vault",
    "Withdraw 500 USDC from Drift Vault",
]

if __name__ == "__main__":
    mcp.run()
