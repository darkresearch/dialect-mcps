"""
Meteora Launch Token MCP Server
A FastMCP server for launching tokens on Meteora using Dialect Blink
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

mcp = FastMCP("Meteora Launch Token MCP")


class LaunchTokenInput(BaseModel):
    token_mint: str = Field(
        description="Token mint address to launch",
        examples=["EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
    )
    base_token_mint: str = Field(
        description="Base token mint address (e.g., USDC)",
        examples=["EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"],
    )
    initial_price: float = Field(
        description="Initial price for the token",
        examples=[0.1, 1.0, 10.0],
        gt=0,  # Price must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class LaunchTokenResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=LaunchTokenInput)
def meteora_launch_token(
    token_mint: str, base_token_mint: str, initial_price: float, tx_sender_pubkey: str
) -> LaunchTokenResponse:
    """
    Launch a token on Meteora via Dialect Blink.

    Args:
        token_mint: Token mint address to launch
        base_token_mint: Base token mint address (e.g., USDC)
        initial_price: Initial price for the token
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        LaunchTokenResponse: Result of the token launch request
    """
    if not BLINK_CLIENT_KEY:
        return LaunchTokenResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://meteora.dial.to/api/actions/launch-token?tokenMint={token_mint}&baseTokenMint={base_token_mint}&initialPrice={initial_price}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return LaunchTokenResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return LaunchTokenResponse(success=False, error=error_message)
    except Exception as e:
        return LaunchTokenResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Meteora Launch Token MCP enables launching tokens on Meteora via Dialect Blink API.
Provides a simple interface for creating new token pools on Meteora.
"""

mcp.prompt_suggestions = [
    "Launch my token on Meteora with initial price of 0.1 USDC",
    "Create a new token pool on Meteora",
]

if __name__ == "__main__":
    mcp.run()
