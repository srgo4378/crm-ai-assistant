import time
import streamlit as st

st.set_page_config(page_title="CRM AI Sales Assistant", page_icon="🤝")
st.title("🤝 CRM AI Sales Assistant")
st.write("Paste raw call notes → get a lead summary, tags, next step, and a follow-up email.")

notes = st.text_area(
    "Call notes:",
    height=200,
    placeholder="E.g., Spoke with Sarah J. Wants a 3-bed in Denver under $750k. Mentioned Compass. Open house Sat. Prefers email."
)

def build_prompt(n):
    return f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK:
Given the raw call notes below, produce:
1) Lead Summary: 2–4 sentences with actionable specifics.
2) Tags: 3–7 concise tags inside curly braces, e.g. {{Buyer, Denver, 3-bed, Budget<750k, Competitor=Compass, Timeline=2-3mo}}.
3) Next Step: ONE specific action and timeframe (e.g., 'Send list of 5 homes and schedule tour within 3 days').
4) Email Draft: 4–6 sentences, professional and friendly, soft CTA, natural human tone.

RAW NOTES:
{n}

Return the four sections clearly labeled.
""".strip()

def try_openai(prompt):
    # Try OpenAI up to 3 times with backoff
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    last_err = None
    for i in range(3):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,   # lighter to avoid rate limits
            )
            return resp.choices[0].message.content
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (i + 1))  # 1.5s, 3s, 4.5s
    raise last_err

def try_anthropic(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model="claude-3-5-sonnet-latest",
        temperature=0.3,
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please enter some call notes first.")
        st.stop()

    prompt = build_prompt(notes)

    with st.spinner("Thinking..."):
        output = None
        # Prefer OpenAI; if rate-limited and Claude key exists, fall back
        if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"].startswith("sk-"):
            try:
                output = try_openai(prompt)
            except Exception as e:
                if "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"].startswith("sk-ant-"):
                    st.info("OpenAI is busy; trying Claude fallback…")
                    try:
                        output = try_anthropic(prompt)
                    except Exception as e2:
                        st.error(f"Both providers failed. Error: {e2}")
                        st.stop()
                else:
                    st.error("OpenAI is rate-limited or blocked. Add an Anthropic key in Secrets to enable fallback.")
                    st.stop()
        elif "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"].startswith("sk-ant-"):
            output = try_anthropic(prompt)
        else:
            st.error("No API keys found. Add OPENAI_API_KEY or ANTHROPIC_API_KEY in Secrets.")
            st.stop()

    st.subheader("📌 AI Output")
    st.write(output)

st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
