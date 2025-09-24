import streamlit as st
import anthropic

st.set_page_config(page_title="CRM AI Sales Assistant", page_icon="🤝")
st.title("🤝 CRM AI Sales Assistant")
st.write("Paste raw call notes → get a lead summary, tags, next step, and a follow-up email.")

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

    # Build the prompt
    prompt = f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK:
Given the raw call notes below, produce:
1) Lead Summary: 2–4 sentences with actionable specifics.
2) Tags: 3–7 concise tags inside curly braces, e.g. {{Buyer, Denver, 3-bed, Budget<750k, Competitor=Compass, Timeline=2-3mo}}.
3) Next Step: ONE specific action and timeframe.
4) Email Draft: 4–6 sentences, professional and friendly, soft CTA, natural human tone.

RAW NOTES:
{notes}

Return the four sections clearly labeled.
"""

    with st.spinner("Thinking..."):
        resp = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=700,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        output = resp.content[0].text

    st.subheader("📌 AI Output")
    st.write(output)

st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
