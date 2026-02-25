import streamlit as st
import requests
import json
import os
from tools.web_search import search_web
from tools.voice import listen, speak

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Clawdbot Pro", page_icon="🤖")
st.title("🤖 Clawdbot Pro")
st.caption("GPU Powered • Coding Specialized • Memory Enabled")

# -------- CONFIG --------
MODEL = "llama3:8b-instruct-q4_0"
API_URL = "http://localhost:11434/api/generate"
MEMORY_FILE = "memory.json"

# -------- MODE SELECTION --------
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Coding Copilot", "Chat Assistant"]
)

def get_system_prompt(mode):
    if mode == "Coding Copilot":
        return """
You are Clawdbot, an elite coding copilot.
Always respond with:
- Clean, production-ready code
- Proper formatting
- Short explanation after code
Support Python, JavaScript, C++, SQL.
"""
    else:
        return "You are a helpful AI assistant."

system_prompt = get_system_prompt(mode)

# -------- LOAD MEMORY --------
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        chat_history = json.load(f)
else:
    chat_history = []

if "messages" not in st.session_state:
    st.session_state.messages = chat_history

# -------- FILE UPLOAD --------
uploaded_file = st.sidebar.file_uploader(
    "Upload Code File",
    type=["py", "js", "txt", "cpp"]
)

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    st.sidebar.success("File uploaded successfully!")

    if st.sidebar.button("Analyze File"):
        analysis_prompt = f"""
Analyze this code and suggest improvements:

{file_content}
"""

        try:
            response = requests.post(
                API_URL,
                json={
                    "model": MODEL,
                    "prompt": analysis_prompt,
                    "stream": False,
                },
                timeout=120
            )

            result = response.json().get("response", "No response from model.")
            st.write(result)

        except Exception as e:
            st.error(f"Error: {e}")

# -------- VOICE MODE --------
if st.sidebar.button("🎤 Voice Mode"):
    user_voice = listen()
    if user_voice:
        st.write("You said:", user_voice)
        speak("Processing your request")

        st.session_state.messages.append(
            {"role": "user", "content": user_voice}
        )

# -------- DISPLAY CHAT --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------- CHAT INPUT --------
prompt = st.chat_input("Ask Clawdbot...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # -------- SEARCH MODE --------
    if prompt.lower().startswith("search:"):
        query = prompt.replace("search:", "").strip()
        results = search_web(query)

        with st.chat_message("assistant"):
            st.write(results)

        st.session_state.messages.append(
            {"role": "assistant", "content": str(results)}
        )

    else:
        # -------- BUILD FULL CONTEXT --------
        full_prompt = system_prompt + "\n"

        for msg in st.session_state.messages:
            full_prompt += f"{msg['role']}: {msg['content']}\n"

        full_prompt += "assistant:"

        # -------- API CALL --------
        try:
            response = requests.post(
                API_URL,
                json={
                    "model": MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {
                        "temperature": 0.6,
                        "num_predict": 400
                    },
                },
                timeout=180
            )

            reply = response.json().get("response", "No response from model.")

        except Exception as e:
            reply = f"⚠️ Error connecting to model: {e}"

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.markdown(reply)

    # -------- SAVE MEMORY --------
    with open(MEMORY_FILE, "w") as f:
        json.dump(st.session_state.messages, f, indent=4)