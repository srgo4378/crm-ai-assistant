import streamlit as st
from openai import OpenAI

st.title("🤝 CRM AI Sales Assistant")
st.write("Paste your raw call notes below and get a summary, tags, next step, and a follow-up email.")

# Input box
notes = st.text_area("Call notes:", height=200, placeholder="E.g., Spoke with Sarah J. Wants a 3-bed in Denver under $750k...")

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please enter some call notes first.")
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        prompt = f"""
        You are an AI Sales Assistant for real estate CRM Follow Up Boss.
        Input: {notes}

        Output:
        - Lead Summary (2-3 sentences)
        - Tags (3–5 tags in curly braces like {{Buyer, Denver, 3-bed, Budget<750k}})
        - Next Step (1 clear action with timeframe)
        - Follow-up Email Draft (5–6 sentences, professional and friendly)
        """

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                temperature=0.3,
                max_tokens=500
