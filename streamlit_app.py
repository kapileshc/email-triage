from pathlib import Path
import tempfile

import streamlit as st

from app.schemas import AttachmentInput, EmailRequest
from app.services.pipeline import run_pipeline

st.set_page_config(page_title="Agentic Email Triage", layout="wide")
st.title("Multimodal Agentic Email Triage")
st.caption("Local-first demo: email + attachments → triage → RAG → grounded Gemma 3 reply")

sender = st.text_input("Sender", "customer@example.com")
subject = st.text_input("Subject", "Unable to access my account")
body = st.text_area("Email body", "I reset my password twice but I still cannot login. Please tell me what I should do.", height=180)
uploads = st.file_uploader("Attachments", type=["pdf", "png", "jpg", "jpeg", "txt", "md"], accept_multiple_files=True)

if st.button("Run triage", type="primary"):
    attachments = []
    temp_dir = Path(tempfile.mkdtemp(prefix="email-triage-"))
    for upload in uploads or []:
        path = temp_dir / upload.name
        path.write_bytes(upload.getvalue())
        attachments.append(AttachmentInput(filename=upload.name, path=str(path)))

    result = run_pipeline(EmailRequest(sender=sender, subject=subject, body=body, attachments=attachments))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Triage decision")
        st.json(result.decision.model_dump())
        st.subheader("Processing trace")
        for step in result.trace:
            st.code(step)
        if result.extracted_attachments:
            st.subheader("Extracted attachment text")
            for name, text in result.extracted_attachments.items():
                with st.expander(name):
                    st.text(text[:12000])
    with c2:
        st.subheader("Grounded draft")
        st.text_area("Reply", result.draft_reply or "", height=320)
        st.subheader("Retrieved evidence")
        if not result.retrieved_context:
            st.info("No evidence retrieved.")
        for item in result.retrieved_context:
            with st.expander(item.source):
                st.write(item.text)
                if item.score is not None:
                    st.caption(f"Vector score: {item.score:.4f}")
