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

    # Plain string (not an f-string) to avoid brace/quote issues
    prompt = (
        "You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).\n\n"
        "TASK:\n"
        "Given the raw call notes below, produce:\
