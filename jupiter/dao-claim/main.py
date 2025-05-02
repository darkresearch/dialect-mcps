"""
Jupiter DAO Claim MCP Server
A FastMCP server for claiming ASR rewards from Jupiter DAO using Dialect Blink
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

mcp = FastMCP("Jupiter DAO Claim MCP")

class DaoClaimInput(BaseModel):
    tx_sender_pubkey: str = Field(
        description="Solana account public key of the transaction sender",
        examples=["C7GCggFP3464XJK4DudqkSkMjQSeKbNa9SMTf26tPQ5E"]
    )

class DaoClaimResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None

@mcp.tool(input_model=DaoClaimInput)
def jupiter_dao_claim(
    tx_sender_pubkey: str
) -> DaoClaimResponse:
    """
    Claim ASR rewards from Jupiter DAO via Dialect Blink.
    
    Args:
        tx_sender_pubkey: Solana account public key of the transaction sender
    
    Returns:
        DaoClaimResponse: Result of the claim request
    """
    if not BLINK_CLIENT_KEY:
        return DaoClaimResponse(
            success=False,
            error="Missing BLINK_CLIENT_KEY environment variable"
        )
    
    try:
        blink_url = "https://jupiter.dial.to/dao/asr?action=claim"
        
        headers = {
            "Content-Type": "application/json",
            "X-Blink-Client-Key": BLINK_CLIENT_KEY
        }
        
        data = {
            "type": "transaction",
            "account": tx_sender_pubkey
        }
        
        response = requests.post(blink_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return DaoClaimResponse(
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
        
        return DaoClaimResponse(
            success=False,
            error=error_message
        )
    except Exception as e:
        return DaoClaimResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

mcp.description = """
Jupiter DAO Claim MCP enables claiming ASR rewards from Jupiter DAO via Dialect Blink API.
Provides a simple interface for claiming rewards from the DAO.
"""

mcp.prompt_suggestions = [
    "Claim my ASR rewards from Jupiter DAO",
    "Claim ASR rewards from Jupiter DAO",
]

if __name__ == "__main__":
    mcp.run()
