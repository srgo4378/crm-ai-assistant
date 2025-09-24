import streamlit as st
import anthropic

st.set_page_config(page_title="CRM AI Sales Assistant", page_icon="🤝", layout="centered")
st.title("🤝 CRM AI Sales Assistant")
st.write("Paste raw call notes → get a lead summary, tags, next step, and a follow-up email.")

# ---- Controls
tone = st.selectbox("Email Tone", ["Professional", "Friendly", "Luxury"])

notes = st.text_area(
    "Call notes:",
    height=200,
    placeholder="E.g., Spoke with Sarah J. Wants a 3-bed in Denver under $750k. Mentioned Compass. Open house Sat. Prefers email.",
)

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please enter some call notes first.")
        st.stop()

    # ---- Connect to Claude
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        if not api_key or not api_key.startswith("sk-ant-"):
            st.error("Your ANTHROPIC_API_KEY is missing or invalid. Add it in Manage app → Secrets.")
            st.stop()
        client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        st.error("Missing ANTHROPIC_API_KEY in Streamlit Secrets.")
        st.stop()

    # ---- Prompt (tight, consistent outputs)
    prompt = f"""
You are an AI Sales Assistant for a real-estate CRM (like Follow Up Boss).

TASK: From the raw notes, produce EXACTLY four sections:

1) Lead Summary — ≤3 short sentences, concrete details only.
2) Tags — max 6 in this exact style: {{Buyer/Seller, City, 3-bed (or N-bed), Budget<###k, Neighborhood, Timeline=##-##mo}}.
3) Next Step — ONE action + a due-by date within 3 business days (write the weekday, e.g., “by Friday”).
4) Email Draft — include:
   Subject: one clear line (≤60 chars)
   Body: 4–5 short sentences, skimmable, 1 clear CTA with a day/time window. Tone: {tone}.

RAW NOTES:
{notes}
"""

    with st.spinner("Thinking..."):
        try:
            resp = client.messages.create(
                model="claude-3-haiku-20240307",  # fast + widely available
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            output = resp.content[0].text
        except anthropic.APIError as e:
            st.error(f"Anthropic API error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.stop()

    # ---- Show raw sections
    st.subheader("📌 AI Output")
    st.write(output)

    # ---- Extract & display Tags nicely (badges)
    try:
        if "Tags:" in output:
            tags_line = output.split("Tags:", 1)[1].split("\n", 1)[0]
            cleaned = tags_line.strip().strip("{}")
            tags = [t.strip() for t in cleaned.split(",") if t.strip()]
            if tags:
                st.subheader("🏷️ Tags")
                st.write(" ".join(f"`{t}`" for t in tags[:6]))
    except Exception:
        pass  # don't block if parsing fails

    # ---- Extract Email: Subject + Body into copy-ready boxes
    subject, body = "", ""
    if "Email Draft:" in output:
        email_block = output.split("Email Draft:", 1)[1].strip()

        # Prefer "Subject:" label if present
        if "Subject:" in email_block:
            after = email_block.split("Subject:", 1)[1].strip()
            if "\n" in after:
                first_line, rest = after.split("\n", 1)
                subject = first_line.strip()
                body = rest.strip()
            else:
                subject = after.strip()
                body = ""
        else:
            # Fallback: first non-empty line = subject, rest = body
            lines = [ln for ln in email_block.splitlines() if ln.strip()]
            if lines:
                subject = lines[0].strip()
                body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    if subject or body:
        st.subheader("📧 Email (copy-ready)")
        st.text_input("Subject", subject)
        st.text_area("Body", body, height=200)

# ---- Footer
st.caption("Prototype demo. In a full product, these outputs would auto-fill CRM fields and schedule the next task.")
