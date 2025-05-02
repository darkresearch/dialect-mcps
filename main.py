#!/usr/bin/env python3
"""
Jupiter MCP Server
A FastMCP server for performing Jupiter swaps using Dialect Blink
"""

import os
import urllib.parse
from typing import Annotated, Literal, Optional

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Get required environment variables
BLINK_CLIENT_KEY = os.getenv("BLINK_CLIENT_KEY")
BIN_UUID = os.getenv("BIN_UUID", "6874794c-513e-456f-801f-5957a82e068e")

# Initialize FastMCP server
mcp = FastMCP("Jupiter Swap MCP")

# Define input model
class SwapInput(BaseModel):
    token_in: str = Field(
        description="Input token symbol (e.g., SOL)",
        examples=["SOL", "USDC"]
    )
    token_out: str = Field(
        description="Output token symbol (e.g., DARK)",
        examples=["DARK", "SOL"]
    )
    amount: float = Field(
        description="Amount of token_in to swap",
        examples=[0.1, 1.0, 10.0],
        gt=0  # Amount must be greater than 0
    )
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"]
    )

# Define response model
class SwapResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None

@mcp.tool(input_model=SwapInput)
def jupiter_swap(token_in: str, token_out: str, amount: float, tx_sender_pubkey: str) -> SwapResponse:
    """
    Execute a token swap on Jupiter via Dialect Blink.
    
    Args:
        token_in: Input token symbol (e.g., SOL)
        token_out: Output token symbol (e.g., DARK)
        amount: Amount of token_in to swap
        tx_sender_pubkey: Solana account public key of the transaction sender
    
    Returns:
        SwapResponse: Result of the swap request
    """
    if not BLINK_CLIENT_KEY:
        return SwapResponse(
            success=False,
            error="Missing BLINK_CLIENT_KEY environment variable"
        )
    
    try:
        # Construct Jupiter URL for the swap
        jupiter_url = f"https://jupiter.dial.to/swap/{token_in}-{token_out}/{amount}?_bin={BIN_UUID}"
        
        # URL encode the Jupiter URL as the apiUrl parameter
        encoded_api_url = urllib.parse.quote(jupiter_url)
        
        # Full Dialect Blink API URL
        blink_url = f"https://api.dial.to/v1/blink?apiUrl={encoded_api_url}"
        
        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY
        }
        
        # Request body
        data = {
            "type": "transaction",
            "account": tx_sender_pubkey
        }
        
        # Make the API request
        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return SwapResponse(
            success=True,
            result=response.json()
        )
        
    except requests.exceptions.RequestException as e:
        error_message = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and 'error' in error_data:
                    error_message = f"API error: {error_data['error']}"
            except:
                error_message = f"API error: {e.response.text}"
        
        return SwapResponse(
            success=False,
            error=error_message
        )
    except Exception as e:
        return SwapResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

# Set up description for the server
mcp.description = """
Jupiter Swap MCP enables token swaps on Jupiter DEX via Dialect Blink API.
Provides a simple interface for executing swaps between Solana-based tokens.
"""

# Prompt suggestion for Claude
mcp.prompt_suggestions = [
    "Swap 0.1 SOL for DARK tokens",
    "Exchange USDC for SOL using my wallet address",
]

if __name__ == "__main__":
    mcp.run() 