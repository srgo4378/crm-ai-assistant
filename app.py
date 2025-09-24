import streamlit as st
import anthropic

st.set_page_config(page_title="CRM AI Sales Assistant", page_icon="🤝")
st.title("🤝 CRM AI Sales Assistant")
st.write("Paste raw call notes → get a lead summary, tags, next step, and a follow-up email.")

# Tone selector
tone = st.selectbox("Email Tone", ["Professional", "Friendly", "Luxury"])

# Text input for notes
notes = st.text_area(
    "Call notes:",
    height=200,
    placeholder="E.g., Spoke with Sarah J. Wants a 3-bed in Denver under $750k. Mentioned Compass. Open house Sat. Prefers email."
)

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please enter some call notes first.")
        st.stop()

    # Connect to Claude
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        st.error("Missing ANTHROPIC_API_KEY in Streamlit Secrets.")
        st.stop()

    # Prompt (triple quotes, no weird spacing)
   prompt = f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK: From the raw notes, produce EXACTLY four sections with these rules:

1) Lead Summary — ≤3 short sentences, concrete details only.
2) Tags — max 6 in this exact style: {{Buyer/Seller, City, Beds, Budget<###k, Neighborhood, Timeline=##-##mo}}.
3) Next Step — one action + a due-by date within 3 business days (e.g., “Send 5 listings + lender intro by Wed, Oct 1”).
4) Email Draft — include:
   - Subject: one clear line (≤60 chars)
   - Body: 4–5 short sentences, skimmable, 1 concrete CTA with day/time window, no fluff.

RAW NOTES:
{notes}
"""
