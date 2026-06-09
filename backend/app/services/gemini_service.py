import os
from typing import List, Optional

from google.genai import Client
from google.genai import types


def _get_client() -> Client:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY environment variable is required.")
    return Client(api_key=key)


def analyze_document(document_text: str, document_name: Optional[str] = None) -> dict:
    client = _get_client()

    truncated_text = document_text[:150000]
    prompt = (
        f"Analyze the document named \"{document_name or 'document'}\" and extract key information.\n"
        f"Document content preview:\n{truncated_text}\n\n"
        "Format your output strictly as a JSON object containing a brief summary, key takeaways, and three relevant suggested questions."
    )

    system_instruction = (
        "You are an elite corporate research advisor. "
        "Digest the provided text and synthesize a pristine, highly-informative JSON payload detailing an overview, "
        "specific takeaways, and suggested smart questions that the user should click to learn more. "
        "Respond strictly in JSON format matching the schema."
    )

    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "keyTakeaways": {"type": "array", "items": {"type": "string"}},
            "suggestedQuestions": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary", "keyTakeaways", "suggestedQuestions"],
    }

    resp = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "systemInstruction": system_instruction,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    )

    text = getattr(resp, "text", None) or resp.candidates[0].content.parts[0].text
    if not text:
        raise RuntimeError("No response text received from Gemini API")

    # Gemini should return JSON text
    import json

    return json.loads(text.strip())


def chat_with_document(messages, document_text: str, document_name: Optional[str] = None) -> str:
    client = _get_client()

    system_instruction = (
        "You are an expert document analysis system designed to mimic ChatPDF.\n"
        f"The user is interacting with a document named \"{document_name or 'Document.pdf'}\".\n\n"
        "Here is the entire extracted text content of the document:\n"
        "=== EXTRACTED CONTEXT START ===\n"
        f"{document_text}\n"
        "=== EXTRACTED CONTEXT END ===\n\n"
        "Your strict instructions are:\n"
        "1. Provide accurate, polished answers grounded primary in the text content provided.\n"
        "2. Cite sections, page numbers, tables, or quotes when possible so the user knows where the information is.\n"
        "3. If the user asks a question about general concepts or items NOT listed anywhere in the file, "
        "state that 'This information is not directly mentioned in the document. Here is some general context:' "
        "and answer concisely from general knowledge.\n"
        "4. Keep a highly professional, human, helpful, and scannable tone. Write answers using beautiful, crisp Markdown. "
        "Use lists, tables, and bold highlights generously where they add informational structure."
    )

    # Map to Gemini parts
    # Defensive: only forward roles Gemini can accept in this MVP.
    # This avoids OpenAI/LiteLLM tool-message history issues like:
    # "role 'tool' must be a response to a preceding message with 'tool_calls'".
    allowed_roles = {"user", "model"}
    sanitized_messages = [m for m in messages if getattr(m, "role", None) in allowed_roles]

    contents = []
    for m in sanitized_messages:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})


    resp = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
        config={"systemInstruction": system_instruction},
    )

    text = getattr(resp, "text", None) or resp.candidates[0].content.parts[0].text
    return text or ""

