import streamlit as st
import requests
import json
import os
import time
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv
from google import genai
from gtts import gTTS

load_dotenv()

APP_DIR = Path(__file__).parent
MEDIA_DIR = APP_DIR / "generated_media"
MEDIA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="AI Visual Novel Engine", page_icon="📖", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        white-space: normal;
        height: auto;
        padding: 0.75rem 1rem;
        font-weight: 600;
    }
    div[data-testid="stImage"] img {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

st.title("📖 The Multi-Modal Visual Novel Engine")
st.caption("An AI Dungeon Master that talks, draws, and narrates.")

# ---------------------------------------------------------------------------
# PHASE 1: THE DIRECTOR'S CUT (UI & CONFIGURATION)
# ---------------------------------------------------------------------------

st.sidebar.header("Story Settings")

genre = st.sidebar.selectbox(
    "Story Genre",
    ["High Fantasy", "Cyberpunk Noir", "Space Opera", "Post-Apocalyptic Survival", "Cozy Mystery"]
)

art_style = st.sidebar.selectbox(
    "Art Style",
    ["Digital Painting", "Anime", "Studio Ghibli", "Watercolor", "Cyberpunk Neon", "Dark Fantasy Concept Art"]
)

narrate = st.sidebar.checkbox("🔊 Narrate story with TTS", value=True)

st.sidebar.divider()
if st.sidebar.button("🔄 Restart Story"):
    st.session_state.clear()
    st.rerun()


@st.cache_resource
def get_client():
    """Cache the Gemini client so we don't rebuild it on every rerun."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("`GEMINI_API_KEY` environment variable not set.")
        st.stop()
    return genai.Client(api_key=api_key)


client = get_client()

SYSTEM_PROMPT = """You are the Dungeon Master for an interactive visual novel.
Genre: {genre}
Art style for image prompts: {art_style}

You MUST respond with ONLY a raw JSON object — no markdown fences, no commentary,
no text before or after it. The JSON object must have exactly these three keys:

{{
  "story_text": "A vivid narrative paragraph (4-6 sentences) continuing the story.",
  "image_prompt": "A concise, heavily engineered prompt (under 20 words) describing the
                    current scene for an image generation model, in the '{art_style}' style.",
  "options": ["Choice 1", "Choice 2", "Choice 3"]
}}

Rules:
- "options" must be a plain JSON list of 2 to 3 short, distinct action strings.
- Never break character, never add explanations, never wrap the JSON in ```.
- Keep continuity with everything that happened before in the conversation.
"""



if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-3.5-flash")

if "history" not in st.session_state:
    st.session_state.history = []  # list of parsed scene dicts

if "story_started" not in st.session_state:
    st.session_state.story_started = False

if "last_genre" not in st.session_state:
    st.session_state.last_genre = genre

if "last_art_style" not in st.session_state:
    st.session_state.last_art_style = art_style

if st.session_state.last_genre != genre or st.session_state.last_art_style != art_style:
    st.session_state.chat = client.chats.create(model="gemini-3.5-flash")
    st.session_state.history = []
    st.session_state.story_started = False
    st.session_state.last_genre = genre
    st.session_state.last_art_style = art_style



def clean_json_response(raw_text: str) -> str:
    """Strip markdown fences Gemini sometimes adds despite instructions not to."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response.")
    return cleaned[start:end + 1]


def parse_scene(raw_text: str) -> dict:
    """Parse and validate Gemini's JSON response into a usable dict."""
    data = json.loads(clean_json_response(raw_text))

    required_keys = {"story_text", "image_prompt", "options"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Gemini JSON is missing: {', '.join(sorted(missing))}")

    if not isinstance(data["options"], list) or not 2 <= len(data["options"]) <= 3:
        raise ValueError("Gemini must return 2 to 3 options.")

    data["options"] = [str(o).strip() for o in data["options"] if str(o).strip()]
    return data


def call_gemini(user_move: str) -> dict:
    """Send the player's move to Gemini and return the parsed JSON dict."""
    prompt = SYSTEM_PROMPT.format(genre=genre, art_style=art_style)
    full_message = f"{prompt}\n\nPlayer's move: {user_move}"
    response = st.session_state.chat.send_message(full_message)
    return parse_scene(response.text)



def generate_image(image_prompt: str, scene_number: int) -> str | None:
    """Fetch an image from Pollinations, save to disk. Returns file path, or None on failure."""
    try:
        encoded = quote(image_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=512&nologo=true"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        image_path = MEDIA_DIR / f"scene_{scene_number}.png"
        image_path.write_bytes(response.content)
        return str(image_path)
    except Exception:
        st.toast("Image server is busy, skipping visual...", icon="🖼️")
        return None


def generate_narration(story_text: str, scene_number: int) -> str | None:
    """Convert story_text to speech with gTTS, save to disk. Returns file path, or None on failure."""
    try:
        audio_path = MEDIA_DIR / f"scene_{scene_number}.mp3"
        tts = gTTS(text=story_text, lang="en", slow=False)
        tts.save(str(audio_path))
        return str(audio_path)
    except Exception:
        st.toast("Narrator lost their voice, skipping audio...", icon="🔊")
        return None


def take_turn(user_move: str) -> bool:
    """Full pipeline for one story beat: Gemini -> parse -> image -> audio -> save. Returns True on success."""
    with st.spinner("The story is unfolding..."):
        try:
            data = call_gemini(user_move)
        except (json.JSONDecodeError, ValueError) as e:
            st.toast(f"The narrator got tongue-tied, retrying next turn... ({e})", icon="⚠️")
            return False
        except Exception as e:
            st.toast(f"Connection to the story engine failed: {e}", icon="🔌")
            return False

        scene_number = len(st.session_state.history) + 1
        story_text = data["story_text"]
        image_prompt = data["image_prompt"]
        options = data["options"]

        image_path = generate_image(image_prompt, scene_number) if image_prompt else None
        audio_path = generate_narration(story_text, scene_number) if narrate else None

        st.session_state.history.append({
            "story_text": story_text,
            "image_path": image_path,
            "audio_path": audio_path,
            "options": options,
        })
        st.session_state.story_started = True
        return True




for i, beat in enumerate(st.session_state.history):
    st.markdown(f"### Chapter {i + 1}")
    col1, col2 = st.columns([3, 2])

    with col1:
        st.write(beat["story_text"])
        if beat["audio_path"]:
            st.audio(beat["audio_path"], format="audio/mp3")

    with col2:
        if beat["image_path"]:
            st.image(beat["image_path"], width="stretch")
        else:
            st.info("Visual skipped for this scene.")

    st.divider()

if not st.session_state.story_started:
    st.info(f"Press **Begin Story** to start your {genre} adventure.")
    if st.button("▶️ Begin Story", type="primary"):
        if take_turn("Begin the story with an opening scene."):
            st.rerun()
else:
    last_beat = st.session_state.history[-1]
    st.markdown("#### What do you do?")

    cols = st.columns(len(last_beat["options"])) if last_beat["options"] else [st]
    for idx, option in enumerate(last_beat["options"]):
        target = cols[idx] if last_beat["options"] else st
        with target:
            if st.button(option, key=f"option_{len(st.session_state.history)}_{idx}"):
                if take_turn(option):
                    st.rerun()

    with st.expander("✍️ Or type a custom action"):
        custom_move = st.text_input("Custom action", key="custom_move_input")
        if st.button("Submit custom action") and custom_move:
            if take_turn(custom_move):
                st.rerun()