"""
Jupiter DAO MCP Server
A FastMCP server for interacting with Jupiter DAO using Dialect Blink
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

mcp = FastMCP("Jupiter DAO MCP")


class DaoInput(BaseModel):
    action: Literal["vote", "claim", "stake"] = Field(
        description="DAO action to perform (vote, claim, or stake)",
        examples=["vote", "claim", "stake"],
    )
    proposal_id: Optional[str] = Field(
        default=None,
        description="Proposal ID (required for vote action)",
        examples=["123", "456"],
    )
    vote_type: Optional[Literal["for", "against"]] = Field(
        default=None,
        description="Vote type (required for vote action)",
        examples=["for", "against"],
    )
    amount: Optional[float] = Field(
        default=None,
        description="Amount to stake (required for stake action)",
        examples=[100, 500, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class DaoResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=DaoInput)
def jupiter_dao(
    action: str,
    proposal_id: Optional[str],
    vote_type: Optional[str],
    amount: Optional[float],
    tx_sender_pubkey: str,
) -> DaoResponse:
    """
    Interact with Jupiter DAO via Dialect Blink.

    Args:
        action: DAO action to perform (vote, claim, or stake)
        proposal_id: Proposal ID (required for vote action)
        vote_type: Vote type (required for vote action)
        amount: Amount to stake (required for stake action)
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        DaoResponse: Result of the DAO request
    """
    if not BLINK_CLIENT_KEY:
        return DaoResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    if action == "vote" and (not proposal_id or not vote_type):
        return DaoResponse(
            success=False,
            error="Proposal ID and vote type are required for vote action",
        )

    if action == "stake" and not amount:
        return DaoResponse(success=False, error="Amount is required for stake action")

    try:
        if action == "vote":
            blink_url = f"https://jupiter.dial.to/dao/vote/{proposal_id}/{vote_type}"
        elif action == "claim":
            blink_url = "https://jupiter.dial.to/dao/claim"
        elif action == "stake":
            blink_url = f"https://jupiter.dial.to/dao/stake/{amount}"
        else:
            return DaoResponse(success=False, error=f"Unsupported action: {action}")

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return DaoResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return DaoResponse(success=False, error=error_message)
    except Exception as e:
        return DaoResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Jupiter DAO MCP enables interacting with Jupiter DAO via Dialect Blink API.
Provides a simple interface for voting on proposals, claiming rewards, and staking tokens.
"""

mcp.prompt_suggestions = [
    "Vote for proposal 123 on Jupiter DAO",
    "Claim my Jupiter DAO rewards",
    "Stake 1000 tokens in Jupiter DAO",
]

if __name__ == "__main__":
    mcp.run()
