"""
Drift Vaults Deposit MCP Server
A FastMCP server for depositing in Drift vaults using Dialect Blink
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

mcp = FastMCP("Drift Vaults Deposit MCP")


class VaultsDepositInput(BaseModel):
    vault_type: str = Field(
        description="Vault type (strategy-vaults or insurance-fund-vaults)",
        examples=["strategy-vaults", "insurance-fund-vaults"],
    )
    vault_id: str = Field(
        description="Identifier for a specific vault",
        examples=["FbaXoNjvii97vwqM6m6rgdEarekTJ3ZAdsc1JH5Ym9Gb"],
    )
    amount: float = Field(
        description="Amount to be deposited in the vault",
        examples=[25, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class VaultsDepositResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=VaultsDepositInput)
def drift_vaults_deposit(
    vault_type: str, vault_id: str, amount: float, tx_sender_pubkey: str
) -> VaultsDepositResponse:
    """
    Deposit in a Drift vault via Dialect Blink.

    Args:
        vault_type: Vault type (strategy-vaults or insurance-fund-vaults)
        vault_id: Identifier for a specific vault
        amount: Amount to be deposited in the vault
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        VaultsDepositResponse: Result of the deposit request
    """
    if not BLINK_CLIENT_KEY:
        return VaultsDepositResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = (
            f"https://drift.dial.to/vaults/{vault_type}/{vault_id}?action=deposit&amount={amount}"
        )

        headers = {"Content-Type": "application/json", "X-Blink-Client-Key": BLINK_CLIENT_KEY}

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return VaultsDepositResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return VaultsDepositResponse(success=False, error=error_message)
    except Exception as e:
        return VaultsDepositResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Drift Vaults Deposit MCP enables depositing in Drift vaults via Dialect Blink API.
Provides a simple interface for depositing in strategy vaults or insurance fund vaults.
"""

mcp.prompt_suggestions = [
    "Deposit 25 tokens in Drift strategy vault",
    "Deposit 100 tokens in Drift insurance fund vault",
]

if __name__ == "__main__":
    mcp.run()
