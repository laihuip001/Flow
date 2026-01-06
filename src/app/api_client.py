"""
API Client for AI Clipboard Pro Backend

Handles communication with the FastAPI backend.
"""
import httpx
from typing import Optional


async def process_text(
    text: str,
    style: str = "business",
    base_url: str = "http://localhost:8000"
) -> dict:
    """
    Send text to backend for AI processing.

    Args:
        text: The text to process.
        style: Processing style (business, casual, summary, english, proofread).
        base_url: Backend server URL.

    Returns:
        dict: Response containing 'result' key with processed text,
              or 'error' key if processing failed.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{base_url}/process",
                json={
                    "text": text,
                    "style": style,
                    "current_app": "flet_app"
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP Error: {e.response.status_code}",
                "detail": e.response.text
            }
        except httpx.RequestError as e:
            return {
                "error": "Connection Error",
                "detail": str(e)
            }


async def process_text_stream(
    text: str,
    style: str = "business",
    base_url: str = "http://localhost:8000"
):
    """
    Stream text processing results from backend (SSE).

    Args:
        text: The text to process.
        style: Processing style.
        base_url: Backend server URL.

    Yields:
        str: Partial text chunks as they arrive.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{base_url}/process/stream",
                json={
                    "text": text,
                    "style": style,
                    "current_app": "flet_app"
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        yield data
        except Exception as e:
            yield f"Error: {str(e)}"
