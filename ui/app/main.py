import os
import json
import uuid
from typing import List, Dict, Any, Literal, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


def post_json(path: str, payload: dict) -> dict:
    url = f"{BACKEND_URL}{path}"
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


def extract_file_text(uploaded_file) -> str:
    """Extract text from uploaded file.

    Supports:
    - .txt / .md / .csv / .json (decode bytes)
    - .pdf (PyPDF2 text extraction)
    """
    name = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if name.endswith((".txt", ".md", ".csv", ".json")):
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            from io import BytesIO
            from PyPDF2 import PdfReader

            reader = PdfReader(BytesIO(data))
            pages_text = []
            for page in reader.pages:
                pages_text.append((page.extract_text() or "").strip())
            extracted = "\n\n".join([t for t in pages_text if t])
            return extracted
        except Exception as e:
            raise ValueError(f"Failed to extract PDF text: {e}")

    raise ValueError("Unsupported file type. Please upload .txt/.md/.csv/.json or .pdf.")



def init_state():
    if "docs" not in st.session_state:
        st.session_state.docs = []  # list of {id,name,text,summary,keyTakeaways,suggestedQuestions,isDemo}
    if "active_doc_id" not in st.session_state:
        st.session_state.active_doc_id = None
    if "chats" not in st.session_state:
        st.session_state.chats = {}  # doc_id -> list[ {role,content,timestamp} ]


def set_active(doc_id: str):
    st.session_state.active_doc_id = doc_id
    if doc_id not in st.session_state.chats:
        st.session_state.chats[doc_id] = []


def call_analyze(doc: dict):
    res = post_json(
        "/api/analyze",
        {"documentText": doc["text"], "documentName": doc["name"]},
    )
    doc.update(
        summary=res.get("summary", ""),
        keyTakeaways=res.get("keyTakeaways", []),
        suggestedQuestions=res.get("suggestedQuestions", []),
    )


def call_chat(messages: List[Dict[str, str]], doc: dict) -> str:
    res = post_json(
        "/api/chat",
        {
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            "documentText": doc["text"],
            "documentName": doc["name"],
        },
    )
    return res.get("text", "")


def main():
    st.set_page_config(page_title="DocuMind AI", layout="wide")
    init_state()

    st.title("DocuMind AI — Document Chatbot")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Workspace")
        uploaded = st.file_uploader(
            "Upload a document (supports txt/md/csv/json/pdf)",
            type=["txt", "md", "csv", "json", "pdf"],
        )

        if uploaded is not None:
            try:
                with st.spinner("Extracting text..."):
                    text = extract_file_text(uploaded)
                if not text.strip():
                    raise ValueError("Extracted text is empty")

                doc_id = str(uuid.uuid4())
                doc = {
                    "id": doc_id,
                    "name": uploaded.name,
                    "text": text,
                    "summary": None,
                    "keyTakeaways": [],
                    "suggestedQuestions": [],
                }
                st.session_state.docs.insert(0, doc)
                set_active(doc_id)

                with st.spinner("Analyzing document..."):
                    call_analyze(doc)

                # persist analysis in state
                st.session_state.docs = [
                    (doc if d["id"] == doc_id else d) for d in st.session_state.docs
                ]
                st.success("Document analyzed")
            except Exception as e:
                st.error(str(e))

        # Document list
        for doc in st.session_state.docs:
            active = st.session_state.active_doc_id == doc["id"]
            label = f"{'👉 ' if active else ''}{doc['name']}"
            if st.button(label, key=f"doc_{doc['id']}"):
                set_active(doc["id"])

        active_doc: Optional[dict] = None
        if st.session_state.active_doc_id:
            active_doc = next((d for d in st.session_state.docs if d["id"] == st.session_state.active_doc_id), None)

        if active_doc is None:
            st.info("Upload a file to begin.")
            return

        st.divider()
        st.subheader("Executive Brief")
        if active_doc.get("summary"):
            st.write(active_doc["summary"])
        else:
            st.write("(Summary not generated yet)")

        st.write("**Key takeaways**")
        for t in active_doc.get("keyTakeaways", [])[:6]:
            st.write(f"- {t}")

        st.write("**Suggested prompts**")
        for q in active_doc.get("suggestedQuestions", [])[:6]:
            if st.button(q, key=f"q_{active_doc['id']}_{q}"):
                # Send prompt
                messages = st.session_state.chats.get(active_doc["id"], [])
                messages.append({"role": "user", "content": q, "timestamp": None})
                st.session_state.chats[active_doc["id"]] = messages

                with st.spinner("Gemini is answering..."):
                    assistant = call_chat(messages, active_doc)
                messages.append({"role": "model", "content": assistant, "timestamp": None})
                st.session_state.chats[active_doc["id"]] = messages

    with col_right:
        st.subheader("Chat")
        doc_id = active_doc["id"]
        chat = st.session_state.chats.get(doc_id, [])

        # Render chat
        for msg in chat:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").markdown(msg["content"])

        # Input
        user_text = st.chat_input("Ask a question about the active document")
        if user_text:
            chat = st.session_state.chats.get(doc_id, [])
            chat.append({"role": "user", "content": user_text, "timestamp": None})
            st.session_state.chats[doc_id] = chat
            with st.spinner("Gemini is answering..."):
                assistant = call_chat(chat, active_doc)
            chat.append({"role": "model", "content": assistant, "timestamp": None})
            st.session_state.chats[doc_id] = chat


if __name__ == "__main__":
    main()

