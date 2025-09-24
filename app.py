import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="CRM AI Sales Assistant", page_icon="🤝")
st.title("🤝 CRM AI Sales Assistant")
st.write("Paste raw call notes → get a lead summary, tags, next step, and a follow-up email.")

# Text input
notes = st.text_area(
    "Call notes:",
    height=200,
    placeholder="E.g., Spoke with Sarah J. Wants a 3-bed in Denver under $750k. Mentioned Compass. Open house Sat. Prefers email."
)

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please enter some call notes first.")
        st.stop()

    # Make sure your key is in Streamlit Secrets: OPENAI_API_KEY = sk-...
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("Missing OPENAI_API_KEY in Streamlit Secrets.")
        st.stop()

    # Use triple quotes so no unterminated strings
    prompt = f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK:
Given the raw call notes below, produce:
1) Lead Summary: 2–4 sentences with actionable specifics.
2) Tags: 3–7 concise tags inside curly braces, e.g. {{Buyer, Denver, 3-bed, Budget<750k, Competitor=Compass, Timeline=2-3mo}}.
3) Next Step: ONE specific action and timeframe (e.g., 'Send list of 5 homes and schedule tour within 3 days').
4) Email Draft: 4–6 sentences, professional and friendly, soft CTA, natural human tone.

RAW NOTES:
{notes}

Return the four sections clearly labeled.
"""

    with st.spinner("Thinking..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        output = resp.choices[0].message.content

    st.subheader("📌 AI Output")
    st.write(output)

st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
