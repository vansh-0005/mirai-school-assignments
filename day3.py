import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

st.title("THE MULTIVERSE OF CHATBOTS")

personality = st.selectbox(
    "Who do u want to talk?",
    ["crazy ronaldo fan", "jarvis", "Dr. Strange", "Captain America", "Hulk", "Thor"]
)

@st.cache_resource
def get_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = get_client()

# With cache: "The road is already built, so just use it."
# Without cache: "Build a brand new road every single trip, even though it's the same road."

# --- NEW: initialize chat history once ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- NEW: bin/clear button ---
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()


# --- NEW: show past messages every time the script reruns ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_msg = st.text_input("Say Something")

if st.button("SEND"):
    if user_msg:
        ai_instruction = f"You are acting as {personality}. Respond to the message sent by user staying completely in character."
        with st.spinner("Connecting with multiverse"):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{ai_instruction}\n\nUser: {user_msg}"
                )
                # --- NEW: save both sides of the conversation ---
                st.session_state.chat_history.append({"role": "user", "content": user_msg})
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.rerun()  # refresh so the new messages show up in the loop above
            except Exception as e:
                st.error(f"The multiverse portal is overloaded right now — try again in a bit. ({e})")
    else:
        st.warning("please type the msg first")