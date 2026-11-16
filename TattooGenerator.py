import streamlit as st
from google import genai
import urllib.parse
import random

# 1. Page Configuration (Dark Mode & Studio Layout)
st.set_page_config(page_title="God of Thunder ⚡ Tattoo AI", layout="wide", initial_sidebar_state="expanded")
st.title("⚡ GOD OF THUNDER — Tattoo Design Studio")

# 2. Setup Gemini API Client (Read key from Streamlit Secrets)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Please add your free GEMINI_API_KEY to Streamlit Secrets!")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Master System Prompt (All 6 Styles + Rules)
SYSTEM_PROMPT = """
You are God of Thunder ⚡, an elite tattoo design assistant.
Always guide the user through the 3 Required Questions (Placement, Size in inches, Style) if missing.
Our styles: Neo-Traditional, American Traditional, Old Disney, McComicland, Blackwork, West Coast Chicano.
Calculate Needle Tier Ratios based on size.
When ready to produce a design, output the exact technical breakdown, then format the prompts clearly.
Conclude with: "Would you like to adjust the line thickness, shading, or placement?"
"""

# 4. Helper Function: Pollinations Image Generator
def get_tattoo_urls(stencil_prompt: str, color_prompt: str):
    seed = random.randint(1, 1000000)
    enc_stencil = urllib.parse.quote(stencil_prompt)
    enc_color = urllib.parse.quote(color_prompt)
    
    return {
        "stencil": f"https://image.pollinations.ai/prompt/{enc_stencil}?model=flux&width=768&height=1024&seed={seed}&nologo=true",
        "color": f"https://image.pollinations.ai/prompt/{enc_color}?model=flux&width=768&height=1024&seed={seed}&nologo=true"
    }

# 5. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "⚡ God of Thunder online. Placement, size, and style—what are we building?"}
    ]

# 6. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "images" in msg:
            col1, col2 = st.columns(2)
            with col1:
                st.caption("IMAGE 1: TATTOO STENCIL")
                st.image(msg["images"]["stencil"], use_container_width=True)
            with col2:
                st.caption("IMAGE 2: COLOR REFERENCE")
                st.image(msg["images"]["color"], use_container_width=True)

# 7. User Input & Streaming
if prompt := st.chat_input("Describe your tattoo idea or adjustments..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Gemini
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[m["content"] for m in st.session_state.messages],
            config={"system_instruction": SYSTEM_PROMPT}
        )
        reply_text = response.text
        st.markdown(reply_text)
        
        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": reply_text})