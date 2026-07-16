import streamlit as st
import requests
import random
from urllib.parse import quote

st.set_page_config(page_title="AI Image Studio", page_icon="🎨", layout="wide")
st.markdown("""
<style>
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed, #db2777);
        border: none;
        font-weight: 600;
    }
    .block-container { padding-top: 2rem; }
    div[data-testid="stImage"] img {
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 The AI Image Studio")
st.caption("Describe it, style it, generate it.")
st.title("The AI Image Studio")

SURPRISE_PROMPTS = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon made entirely of stained glass",
    "A tiny wizard brewing coffee in a giant mug",
    "A lighthouse on the moon overlooking Earth"
]


st.sidebar.header("SETTINGS")
art=st.sidebar.selectbox("Select Art Style", ["Photorealastic","Anime","Cyberpunk","Vintage","Sketch","3D RENDER"])

img_width = st.sidebar.slider("Image width", min_value=256, max_value=1024, value=512, step=64)
img_height = st.sidebar.slider("Image height", min_value=256, max_value=1024, value=512, step=64)


magic_enhance = st.sidebar.checkbox("✨ Enable Magic Enhance")

if "prompt_text" not in st.session_state:
    st.session_state.prompt_text=""
    
if st.button("🎲 Surprise Me!"):
    st.session_state.prompt_text= random.choice(SURPRISE_PROMPTS)

user_prompt=st.text_input("Describe your masterpiece",key="prompt_text")


if st.button("GENERATE IMAGE") :
    if user_prompt:
        with st.spinner("Rendering the Image"):
            full_prompt=f"{user_prompt},make the art style: {art}"
            if magic_enhance:
                full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"
            
            encoded_prompt = quote(full_prompt)
            url=f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={img_width}&height={img_height}"
            
            # after calling url reques to store
            response=requests.get(url)
            
            if response.status_code==200:
                st.success("Image Generator")
                image_bytes = response.content
                
                st.image(image_bytes, caption=full_prompt, width="stretch")
                
                st.download_button(
                    label="download image",
                    data=image_bytes,
                    file_name=f"{art}image.png",
                    mime="image/png"
                )
                
            else:
                st.error(f"error generating image (status code {response.status_code})")
    else : st.warning("Please enter the prompt first")