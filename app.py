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

TASK:
Produce exactly four sections from the raw call notes below.

1) Lead Summary: <= 3 sentences, concise and actionable.
2) Tags: max 6 tags, format like {{Buyer/Seller, City, Beds, Budget, AreaOrNeighborhood, Timeline=...}}.
3) Next Step: one clear action + due date within 3 business days.
4) Email Draft: include a subject line and 4–5 sentence body, clear CTA with a day/time window. Tone: {tone}.

RAW NOTES:
{notes}
"""

    with st.spinner("Thinking..."):
        resp = client.messages.create(
            model="claude-3-haiku-20240307",   # ✅ haiku works for all accounts
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        output = resp.content[0].text

    st.subheader("📌 AI Output")
    st.write(output)

st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
