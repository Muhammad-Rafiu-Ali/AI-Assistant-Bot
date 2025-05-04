import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# ---------- Page Config ----------
st.set_page_config(page_title="Career Advisor Bot", page_icon="🎓", layout="wide")

# ---------- Default Dark Mode ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Gemini API Key ----------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key not found. Please set GEMINI_API_KEY in your environment.")
else:
    genai.configure(api_key=api_key, transport="rest")

# ---------- Theme Settings ----------
dark_bg = '#1e1e1e'
light_bg = '#ffffff'
dark_text = '#ffffff'
light_text = '#000000'
sidebar_bg = '#0e1117' if st.session_state.dark_mode else '#f9f9f9'
text_color = dark_text if st.session_state.dark_mode else light_text
button_text_color = dark_text if not st.session_state.dark_mode else light_text
scrollbar_color = '#555555' if st.session_state.dark_mode else '#cccccc'
input_bg = '#333333' if st.session_state.dark_mode else '#f0f0f0'

# ---------- Apply Custom CSS ----------
st.markdown(f"""
    <style>
    html, body, .stApp {{
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        color: {text_color} !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {sidebar_bg};
        color: {text_color};
    }}

    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-thumb {{
        background-color: {scrollbar_color};
        border-radius: 10px;
    }}

    .stButton > button, .stDownloadButton > button {{
        color: {text_color} !important;
        background-color: transparent;
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
    }}

    .typing-dots span {{
        height: 10px;
        width: 10px;
        margin: 0 2px;
        background-color: {'#ccc' if not st.session_state.dark_mode else '#666'};
        display: inline-block;
        border-radius: 50%;
        animation: bounce 1.4s infinite;
    }}

    .typing-dots span:nth-child(2) {{
        animation-delay: 0.2s;
    }}
    .typing-dots span:nth-child(3) {{
        animation-delay: 0.4s;
    }}

    @keyframes bounce {{
        0%, 80%, 100% {{ transform: scale(0); }}
        40% {{ transform: scale(1); }}
    }}
    </style>
""", unsafe_allow_html=True)

# ---------- Top Layout ----------
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.experimental_rerun()

with col2:
    st.markdown(f"""
        <h1 style='text-align: center; font-size: 36px; color: #4da6ff; animation: fadeIn 5s;'>
            🎓 Career Advisor Bot — Your AI Guide for Career Growth 🚀
        </h1>
        <style>
        @keyframes fadeIn {{
            from {{opacity: 0;}}
            to {{opacity: 1;}}
        }}
        </style>
    """, unsafe_allow_html=True)

with col3:
    st.download_button(
        "📄 Download",
        "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]),
        file_name="chat_history.txt"
    )

# ---------- Sidebar ----------
with st.sidebar:
    logo = Image.open(r"C:\\Users\\PMYLS\\Desktop\\gpt\\logo.png")
    st.image(logo, width=100)

    st.markdown(f"""
        <h1 style='display:inline; position:relative; bottom:20px; color: {text_color};'>
            Career Advisor Bot
        </h1>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='color: {text_color};'>
        <h4>📘 About </h4>
        <p>This AI Career Advisor helps you grow in your profession.</p>

        <p><i>Made by Rafiu Ali Memon ❤️</i></p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🆑 New Chat"):
        if st.session_state.messages:
            title = st.session_state.messages[0]['content'][:20] + "..." if st.session_state.messages[0]['content'] else "New Chat"
            st.session_state.chat_history.append((title, st.session_state.messages.copy()))
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.experimental_rerun()

    if st.session_state.chat_history:
        st.subheader("🖓 Previous Chats")
        for i, (title, msgs) in enumerate(st.session_state.chat_history):
            if st.button(title, key=f"chat_{i}"):
                st.session_state.messages = msgs.copy()
                if "chat" in st.session_state:
                    del st.session_state.chat
                st.experimental_rerun()

# ---------- Initialize Gemini Chat Object ----------
if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    st.session_state.chat = model.start_chat(history=[
        {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages
    ])

# ---------- Language Detection Setup ----------
DetectorFactory.seed = 0

# Define roman urdu and roman sindhi keywords
roman_urdu_keywords = ['kese', 'mein', 'acha', 'kyun', 'tum', 'kaise', 'kya', 'nahi', 'ho', 'thik', 'hun']
roman_sindhi_keywords = ['cha', 'hal', 'aa', 'tu', 'budha', 'theek', 'aahiyan', 'qurab', 'mahrabni', 'Shukar', 'Allah ']


def detect_language(text):
    try:
        lower_text = text.lower()
        if any(word in lower_text for word in roman_sindhi_keywords):
            return "roman_sd"
        elif any(word in lower_text for word in roman_urdu_keywords):
            return "roman_ur"
        else:
            lang = detect(text)
            if lang in ["en", "ur", "hi", "sd"]:
                return lang
            return "en"
    except LangDetectException:
        return "en"
# ---------- Chat Messages ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------- User Input ----------
prompt = st.chat_input("Ask me anything about your career...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        dots_placeholder = st.empty()
        dots_html = """
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
        """
        for _ in range(2):
            dots_placeholder.markdown(dots_html, unsafe_allow_html=True)
            time.sleep(0.2)

        try:
            language = detect_language(prompt)
            system_instruction = {
                "en": "Reply in natural, friendly English with emoji 🙂 if appropriate. Match tone and be brief.",
                "ur": "جواب اردو میں دیں، دوستانہ انداز اور ایموجی شامل کریں 🙂 اگر موزوں ہوں۔ سادہ اور مختصر رکھیں۔",
                "sd": "سنڌيءَ ۾ جواب ڏيو، دوستانه لهجو ۽ ايموجيز سان 🙂، مختصر ۽ سادو.",
                "roman_ur": "Roman Urdu mein jawab do, friendly tone mein aur emojis ke sath 🙂. Short aur simple raho.",
                "roman_sd": "Roman Sindhi mein jawab de, sutho friendly tone mein 😄. Mukhtasir te pyaro jawab de."
            }
            final_prompt = f"{system_instruction.get(language, system_instruction['en'])}\nUser: {prompt}"

            response = st.session_state.chat.send_message(final_prompt)
            output = response.text
            dots_placeholder.empty()
            st.markdown(output, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            dots_placeholder.empty()
            st.error(f"Error: {e}")

# ---------- Footer ----------
st.markdown("""
    <div style='text-align: center; padding-top: 10px; font-size: 14px; color: gray;'>
    🔐 Please do not share your personal information to maintain your privacy.
    </div>
""", unsafe_allow_html=True)
