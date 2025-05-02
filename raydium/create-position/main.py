"""
Raydium Create Position MCP Server
A FastMCP server for creating positions in Raydium concentrated liquidity pools using Dialect Blink
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

mcp = FastMCP("Raydium Create Position MCP")


class CreatePositionInput(BaseModel):
    pool_id: str = Field(
        description="Pool ID for the Raydium concentrated liquidity pool",
        examples=["58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"],
    )
    price_lower: float = Field(
        description="Lower price bound for the position",
        examples=[10, 100, 1000],
        gt=0,  # Price must be greater than 0
    )
    price_upper: float = Field(
        description="Upper price bound for the position",
        examples=[20, 200, 2000],
        gt=0,  # Price must be greater than 0
    )
    amount_a: float = Field(
        description="Amount of token A to add",
        examples=[10, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    amount_b: float = Field(
        description="Amount of token B to add",
        examples=[10, 100, 1000],
        gt=0,  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"],
    )


class CreatePositionResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=CreatePositionInput)
def raydium_create_position(
    pool_id: str,
    price_lower: float,
    price_upper: float,
    amount_a: float,
    amount_b: float,
    tx_sender_pubkey: str,
) -> CreatePositionResponse:
    """
    Create a position in a Raydium concentrated liquidity pool via Dialect Blink.

    Args:
        pool_id: Pool ID for the Raydium concentrated liquidity pool
        price_lower: Lower price bound for the position
        price_upper: Upper price bound for the position
        amount_a: Amount of token A to add
        amount_b: Amount of token B to add
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        CreatePositionResponse: Result of the create position request
    """
    if not BLINK_CLIENT_KEY:
        return CreatePositionResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    if price_lower >= price_upper:
        return CreatePositionResponse(
            success=False, error="Lower price bound must be less than upper price bound"
        )

    try:
        blink_url = f"https://raydium.dial.to/clmm/create-position/{pool_id}?priceLower={price_lower}&priceUpper={price_upper}&amountA={amount_a}&amountB={amount_b}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return CreatePositionResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return CreatePositionResponse(success=False, error=error_message)
    except Exception as e:
        return CreatePositionResponse(
            success=False, error=f"Unexpected error: {str(e)}"
        )


mcp.description = """
Raydium Create Position MCP enables creating positions in Raydium concentrated liquidity pools via Dialect Blink API.
Provides a simple interface for creating concentrated liquidity positions with custom price ranges.
"""

mcp.prompt_suggestions = [
    "Create a position in Raydium concentrated liquidity pool",
    "Create a position with price range 10-20 USDC for SOL-USDC pool",
]

if __name__ == "__main__":
    mcp.run()
