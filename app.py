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

    # Prompt (strict format to keep outputs short & clear)
    prompt = f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK: From the raw notes, produce EXACTLY four sections:

1) Lead Summary — ≤3 short sentences, concrete details only.
2) Tags — max 6 in this exact style: {{Buyer/Seller, City, Beds, Budget<###k, Neighborhood, Timeline=##-##mo}}.
3) Next Step — one action + a due-by date within 3 business days.
4) Email Draft — include:
   - Subject: one clear line (≤60 chars)
   - Body: 4–5 short sentences, skimmable, 1 clear CTA with day/time window.
Tone: {tone}.

RAW NOTES:
{notes}
"""

    with st.spinner("Thinking..."):
        resp = client.messages.create(
            model="claude-3-haiku-20240307",   # ✅ Haiku is fast + available to all accounts
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        output = resp.content[0].text

    # Show the raw sections
    st.subheader("📌 AI Output")
    st.write(output)

    # Extra: Extract and show just the email
    email_part = output.split("Email Draft:")[-1].strip() if "Email Draft:" in output else ""
    if email_part:
        st.subheader("📧 Copy-ready Email")
        st.text_area("Email", email_part, height=180)

# Footer note
st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
