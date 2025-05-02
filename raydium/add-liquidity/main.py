"""
Raydium Add Liquidity MCP Server
A FastMCP server for adding liquidity to Raydium pools using Dialect Blink
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

mcp = FastMCP("Raydium Add Liquidity MCP")


class AddLiquidityInput(BaseModel):
    pool_id: str = Field(
        description="Pool ID for the Raydium liquidity pool",
        examples=["58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"],
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


class AddLiquidityResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


@mcp.tool(input_model=AddLiquidityInput)
def raydium_add_liquidity(
    pool_id: str, amount_a: float, amount_b: float, tx_sender_pubkey: str
) -> AddLiquidityResponse:
    """
    Add liquidity to a Raydium pool via Dialect Blink.

    Args:
        pool_id: Pool ID for the Raydium liquidity pool
        amount_a: Amount of token A to add
        amount_b: Amount of token B to add
        tx_sender_pubkey: Solana account public key of the transaction sender

    Returns:
        AddLiquidityResponse: Result of the add liquidity request
    """
    if not BLINK_CLIENT_KEY:
        return AddLiquidityResponse(
            success=False, error="Missing BLINK_CLIENT_KEY environment variable"
        )

    try:
        blink_url = f"https://raydium.dial.to/liquidity/add/{pool_id}?amountA={amount_a}&amountB={amount_b}"

        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY,
        }

        data = {"type": "transaction", "account": tx_sender_pubkey}

        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        return AddLiquidityResponse(success=True, result=response.json())

    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"

        return AddLiquidityResponse(success=False, error=error_message)
    except Exception as e:
        return AddLiquidityResponse(success=False, error=f"Unexpected error: {str(e)}")


mcp.description = """
Raydium Add Liquidity MCP enables adding liquidity to Raydium pools via Dialect Blink API.
Provides a simple interface for adding liquidity to Raydium pools.
"""

mcp.prompt_suggestions = [
    "Add liquidity to Raydium pool",
    "Add 100 USDC and 10 SOL to Raydium pool",
]

if __name__ == "__main__":
    mcp.run()
