# 📖 The Multi-Modal Visual Novel Engine

**MirAI School of Technology — Virtual Summer Internship 2026**
**AI Builder Track — Capstone Mini-Project**

An AI-powered "Choose Your Own Adventure" engine built in Streamlit. A Gemini-based Dungeon Master writes the story, generates the choices, and drives an illustrated, narrated scene — all rendered live in the browser.

---

## What it does

Each turn, the app:
1. Sends the player's action to **Gemini**, which returns a **strict JSON object** containing the next story beat, an image prompt, and 2–3 possible next actions.
2. **Parses** that JSON with Python's `json` module.
3. **Dynamically generates buttons** for whatever choices the AI just returned — no fixed UI, no `st.chat_input()`.
4. Sends the image prompt to **Pollinations** to illustrate the scene.
5. Converts the narration to speech with **gTTS** and plays it back in-browser.
6. Wraps every external call in `try/except` so a failed image or audio call never crashes the app — it just skips that piece and keeps the story going.

---

## Features

- 🎛️ **Story Settings sidebar** — pick a Genre and Art Style before you begin
- 🧠 **Structured JSON storytelling** — Gemini responds only in JSON (`story_text`, `image_prompt`, `options`)
- 🖱️ **Dynamic choice buttons** — generated fresh every turn from the AI's own output
- 🎨 **AI-generated scene art** via Pollinations
- 🔊 **Text-to-speech narration** via gTTS, playable inline with `st.audio()`
- 🛡️ **Graceful failure handling** — image/audio/API errors show a toast and the story continues, never a crash
- 📜 **Full chapter history** — every past scene, image, and narration stays visible as the story grows
- ✍️ **Custom actions** — type your own move instead of picking a suggested option

---

## Setup

### 1. Clone and enter the folder
```bash
cd Assignment5
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key
Create a `.env` file in this folder:
```
GEMINI_API_KEY=your_key_here
```
Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### 5. Run the app
```bash
streamlit run app.py
```

---

## Tech stack

| Layer | Tool |
|---|---|
| UI / app framework | Streamlit |
| Story generation | Gemini (`gemini-3.5-flash`) via `google-genai` |
| Structured output | Python `json` |
| Image generation | Pollinations API |
| Text-to-speech | gTTS |
| Config | `python-dotenv` |

---

## Known limitations

- **Pollinations** is a free, unauthenticated image API and is occasionally slow or unavailable. When this happens, the app shows an "Image server is busy, skipping visual..." toast and continues the story without an image — this is intentional graceful-failure handling, not a bug.
- **Gemini's free tier** has a daily request quota per model. Heavy testing in one day can temporarily exhaust it; if you see a `429 RESOURCE_EXHAUSTED` error, wait for the quota to reset or use a different API key.

---

## Project structure

```
Assignment5/
├── app.py              # Main Streamlit application
├── requirements.txt     # Python dependencies
├── generated_media/     # Auto-created at runtime — stores generated images/audio per scene
└── README.md
```

---

## Author

Built by Vansh Sharma as part of the MirAI School of Technology AI Builder Track capstone.
