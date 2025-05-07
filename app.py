import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# ---------- Page Config ----------
st.set_page_config(page_title="AI Assistant Bot", page_icon="🤖", layout="wide")

# ---------- Default Dark Mode ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Prevent message duplication during reruns ----------
if "processing_message" not in st.session_state:
    st.session_state.processing_message = False
    
# ---------- Welcome Popup Control ----------
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True
    
# ---------- Language Tracking ----------
if "current_language" not in st.session_state:
    st.session_state.current_language = "en"
    
# ---------- User Language Preferences ----------
if "user_language_preference" not in st.session_state:
    st.session_state.user_language_preference = None

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

# ---------- Apply Custom CSS with Improved Responsive Design ----------
st.markdown(f"""
    <style>
    /* Base styles */
    html, body, .stApp {{
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        color: {text_color} !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
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
    .stTextArea > div > textarea,
    .stChatInput > div > textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
    }}
    /* Fix for chat input container */
    .stChatInput > div {{
        background-color: {input_bg} !important;
    }}
    /* Fix for chat message colors */
    .message[data-testid*="StyledTheme"] {{
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        color: {text_color} !important;
    }}
    [data-testid="stChatMessageContent"] p {{
        color: {text_color} !important;
    }}
    /* Fix for heading colors in sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: {text_color} !important;
    }}
    /* Make input text more visible in both modes */
    .stChatInput textarea::placeholder {{
        color: {'#777777' if st.session_state.dark_mode else '#555555'} !important;
    }}
    .stChatInput textarea {{
        color: {text_color} !important; 
        caret-color: {'#ffffff' if st.session_state.dark_mode else '#000000'};
    }}
    
    /* Fix for dark mode input background in mobile */
    .stChatInput {{
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
    }}
    
    /* Make all Streamlit containers and elements adapt to dark mode */
    div.stButton > button:hover {{
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        color: {text_color} !important;
    }}
    
    div[data-baseweb="base-input"] {{
        background-color: {input_bg} !important; 
    }}
    
    div[data-baseweb="base-input"] > input {{
        color: {text_color} !important;
    }}
    
    /* Enhanced Responsive design */
    @media screen and (max-width: 768px) {{
        /* For tablet and mobile */
        h1 {{
            font-size: 22px !important;
        }}
        h3 {{
            font-size: 16px !important;
        }}
        p {{
            font-size: 14px !important;
        }}
        /* Make chat messages fit better on small screens */
        [data-testid="stChatMessageContent"] p {{
            padding: 5px !important;
            margin: 5px 0 !important;
        }}
        /* Fix for download button wrapping */
        .stDownloadButton > button {{
            white-space: nowrap !important;
            min-width: auto !important;
            padding: 5px 10px !important;
            font-size: 12px !important;
            line-height: 1.2 !important;
            height: auto !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        /* Fix header wrapping on mobile */
        .main-title {{
            font-size: 22px !important;
            line-height: 1.2 !important;
            padding: 0.5rem 0 !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }}
        /* Improve sidebar responsiveness */
        section[data-testid="stSidebar"] {{
            min-width: 1px !important;
            max-width: 100% !important;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            width: 100% !important;
        }}
        [data-testid="stSidebarNavItems"] {{
            max-width: 100% !important;
        }}
        /* Button adjustments for mobile */
        .stButton > button {{
            padding: 5px 10px !important;
            font-size: 12px !important;
            white-space: nowrap !important;
        }}
        /* Reduce main column padding */
        .main .block-container {{
            padding: 1rem !important;
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        /* Ensure content fits mobile screens */
        img, video {{
            max-width: 100% !important;
            height: auto !important;
        }}
        /* Make sure the chat elements use dark mode properly */
        .stChatInput {{
            background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        }}
        .stChatInput > div {{
            background-color: {input_bg} !important;
        }}
        [data-testid="stChatMessage"] {{
            background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        }}
        /* Make header in sidebar responsive and prevent text overflow */
        [data-testid="stSidebar"] h1 {{
            font-size: 18px !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            white-space: normal !important;
            display: block !important;
        }}
        /* Fix layout for top row elements */
        div.row-widget.stButton, 
        div.row-widget.stDownloadButton {{
            width: auto !important;
            min-width: auto !important;
            display: flex !important;
            justify-content: center !important;
        }}
        /* Fix column layout */
        div.row-widget.stHorizontal {{
            flex-wrap: nowrap !important;
            gap: 5px !important;
        }}
        div.row-widget.stHorizontal > div {{
            flex: none !important;
            width: auto !important;
        }}
    }}
    
    @media screen and (max-width: 480px) {{
        /* For small mobile screens */
        h1 {{
            font-size: 18px !important;
        }}
        h3 {{
            font-size: 14px !important;
        }}
        p {{
            font-size: 12px !important;
        }}
        .main-title {{  
            font-size: 18px !important;
            padding: 0.2rem 0 !important;
            line-height: 1.3 !important;
        }}
        /* Further reduce element sizes */
        [data-testid="stChatMessage"] {{
            margin: 4px 0 !important;
            padding: 6px !important;
        }}
        /* Tighten layout for small screens */
        .main .block-container {{
            padding: 0.5rem !important;
        }}
        /* Adjust button size for small screens */
        .stButton > button, .stDownloadButton > button {{
            padding: 3px 6px !important;
            font-size: 10px !important;
            min-height: 1.5rem !important;
            height: auto !important;
        }}
        /* Fix chat input for small screens */
        .stChatInput {{
            padding: 0.25rem !important;
            margin-bottom: 1rem !important;
            background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
        }}
        /* Optimize sidebar for small screens */
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1rem !important;
            padding-right: 0.5rem !important;
            padding-left: 0.5rem !important;
        }}
        /* Fix top layout for mobile */
        .stHorizontal > div {{
            width: auto !important;
            flex-shrink: 1 !important;
        }}
        .stHorizontal > div:first-child, 
        .stHorizontal > div:last-child {{
            flex-grow: 0 !important;
            flex-basis: auto !important;
        }}
        .stHorizontal > div:nth-child(2) {{
            flex-grow: 1 !important;
            flex-basis: 0 !important;
        }}
    }}
    
    /* Add typing dots animation */
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
    
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    

""", unsafe_allow_html=True)

# ---------- Top Layout ----------
# Improved header with buttons on opposite sides
st.markdown("""
<style>
/* Professional header layout with elements on opposite sides */
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 1rem;
    padding: 8px 0;
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}

.header-left {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 10px;
    min-width: 40px; /* Ensure minimum width for the toggle button */
}

.header-center {
    flex: 1;
    text-align: center;
    padding: 0 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.header-right {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    min-width: 40px; /* Ensure minimum width for the download button */
}

.theme-toggle button {
    padding: 6px 8px !important;
    border-radius: 20px !important;
    min-height: 36px !important;
    min-width: 38px !important;
    width: 38px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.download-button button {
    padding: 6px 8px !important;
    border-radius: 20px !important;
    min-height: 36px !important;
    min-width: 100px !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

@media (max-width: 768px) {
    .header-center {
        font-size: 0.9em;
        padding: 0 5px;
    }
    .theme-toggle button, .download-button button {
        padding: 4px 8px !important;
        min-height: 32px !important;
    }
}

@media (max-width: 576px) {
    /* Mobile layout with both buttons on the same row */
    .header-container {
        display: flex;
        flex-direction: column;
        padding: 5px 0;
    }
    
    .header-left, .header-right {
        flex: 0 0 auto;
        padding: 5px 10px;
    }
    
    /* Create a separate top row for buttons */
    .header-container::before {
        content: '';
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 10px;
    }
    
    /* First row with buttons side by side */
    .header-left, .header-right {
        position: static;
        display: flex;
    }
    
    .header-left {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 10;
    }
    
    .header-right {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 10;
    }
    
    /* Title below the buttons */
    .header-center {
        width: 100%;
        margin-top: 40px; /* Space for buttons above */
        font-size: 0.8em;
        text-align: center;
        padding: 5px 0;
    }
    
    .main-title {
        font-size: 22px !important;
    }
    
    /* Make buttons more compact on mobile */
    .theme-toggle button {
        min-width: 32px !important;
        width: 32px !important;
        min-height: 32px !important;
        padding: 3px !important;
    }
    
    .download-button button {
        min-width: 90px !important;
        min-height: 32px !important;
        padding: 3px 6px !important;
    }
}
</style>

<div class="header-container">
    <div class="header-left" id="theme-toggle-container"></div>
    <div class="header-center" id="title-container"></div>
    <div class="header-right" id="download-container"></div>
</div>
""", unsafe_allow_html=True)

# Use containers for better control and positioning - equal widths for mobile view
left_container, center_container, right_container = st.columns([1, 4, 1])

with left_container:
    # Wrap the toggle theme button in a container with the class
    st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="toggle_theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with center_container:
    st.markdown(f"""
        <h1 class='main-title' style='text-align: center; font-size: 32px; color: #4da6ff; animation: fadeIn 5s; margin: 0;'>
            🤖 AI Assistant Bot — Your Smart AI Guide for Everything 🚀
        </h1>
        <style>
        @keyframes fadeIn {{
            from {{opacity: 0;}}
            to {{opacity: 1;}}
        }}
        </style>
    """, unsafe_allow_html=True)

with right_container:
    # Add the download button with better styling
    st.markdown('<div class="download-button">', unsafe_allow_html=True)
    st.download_button(
        "📄 Download",
        "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]),
        file_name="chat_history.txt",
        key="download_chat"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Welcome Popup Component ----------
# Move the welcome popup to after the top navigation so it appears below it
if st.session_state.show_welcome:
    # Create styles for centered welcome card
    st.markdown("""
    <style>
    .welcome-card {
        background-color: var(--background-color);
        border: 2px solid #4da6ff;
        border-radius: 10px;
        padding: 30px;
        margin: 20px auto 30px;
        max-width: 500px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.6s ease-out;
    }
    @keyframes slideIn {
        0% { opacity: 0; transform: translateY(-30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a welcome card centered on the page
    cols = st.columns([1, 6, 1])
    with cols[1]:
        st.markdown(f"""
        <div class="welcome-card" style="background-color: {dark_bg if st.session_state.dark_mode else light_bg};">
            <h2 style="color: #4da6ff; margin-top: 0;">🤖 Welcome to AI Assistant Bot</h2>
            <p style="margin: 15px 0; font-size: 16px; color: {text_color};">Your Smart AI Guide for Everything 🚀</p>
            <p style="margin: 15px 0; font-size: 16px; color: {text_color};">Made by Rafiu Ali Memon ❤️</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add the button using Streamlit's native button which works more reliably
        if st.button("Get Started", key="welcome_close", type="primary", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()
# Nothing here - Removed the duplicated section

# ---------- Sidebar ----------
with st.sidebar:
    try:
        logo = Image.open("logo.png")  # Updated path assuming logo.png is in the root directory
        st.image(logo, width=100)
    except FileNotFoundError:
        st.info("Logo image not found. Using text header instead.")

    st.markdown(f"""
        <h1 style='display:inline; position:relative; bottom:20px; color: {text_color};'>
            AI Assistant Bot
        </h1>
    """, unsafe_allow_html=True)

    # About section with dark/light mode compatibility
    st.markdown(f"<h3 style='color:{text_color};'>📘 About</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{text_color};'>This AI Assistant helps you with almost anything you need - from answering questions to writing code.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{text_color};'><i>Made by Rafiu Ali Memon ❤️</i></p>", unsafe_allow_html=True)
    
    st.session_state.user_language_preference = None

    if st.button("🆑 New Chat"):
        if st.session_state.messages:
            title = st.session_state.messages[0]['content'][:20] + "..." if st.session_state.messages[0]['content'] else "New Chat"
            st.session_state.chat_history.append((title, st.session_state.messages.copy()))
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.session_state.processing_message = False
        st.rerun()

    if st.session_state.chat_history:
        st.markdown(f"<h3 style='color:{text_color};'>🖓 Previous Chats</h3>", unsafe_allow_html=True)
        for i, (title, msgs) in enumerate(st.session_state.chat_history):
            if st.button(title, key=f"chat_{i}"):
                st.session_state.messages = msgs.copy()
                if "chat" in st.session_state:
                    del st.session_state.chat
                st.session_state.processing_message = False
                st.rerun()
    
    # Add vertical space and divider before the feedback button            
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Add feedback button at the bottom of the sidebar
    st.markdown(f"""<div style='text-align: center;'><a href='https://docs.google.com/forms/u/0/' target='_blank'><button style='background-color: #4CAF50; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;'>Feedback</button></a></div>""", unsafe_allow_html=True)

# ---------- Language Detection Setup ----------
DetectorFactory.seed = 0

# Expanded keywords for better detection
roman_urdu_keywords = [
    'kese', 'mein', 'acha', 'kyun', 'tum', 'kaise', 'kya', 'nahi', 'ho', 'thik', 'hun', 
    'ap', 'main', 'hai', 'hain', 'kar', 'raha', 'rahi', 'rahe', 'karna', 'karein', 
    'karo', 'jao', 'aao', 'dena', 'lena', 'batao', 'sunao', 'dikhao', 'samjhao',
    'theek', 'acha', 'bura', 'mushkil', 'asan', 'koshish', 'mehnat', 'waqt', 'din',
    'raat', 'subah', 'shaam', 'dopahar', 'hamesha', 'kabhi', 'nahin', 'nahi',
    'haan', 'jee', 'bilkul', 'zaroor', 'shayad', 'matlab', 'lekin', 'magar',
    'aur', 'ya', 'per', 'phir', 'dobara', 'kab', 'kaisa', 'kesi', 'kuch'
]

roman_sindhi_keywords = [
    'cha', 'hal', 'aa', 'tu', 'budha', 'theek', 'aahiyan', 'qurab', 'mahrabni', 'Shukar', 'Allah',
    'ahes', 'aahiyan', 'keean', 'kaise', 'mitha', 'thoda', 'ganeyo', 'bhalaa', 'savere',
    'khalaan', 'budho', 'achho', 'kerao', 'kario', 'deo', 'cho', 'chhe', 'chha', 'tha',
    'tho', 'sahi', 'kharab', 'mushkil', 'asaan', 'waqt', 'dinh', 'raat', 'subh', 'shaam',
    'hamesh', 'kadhen', 'naa', 'haa', 'zaroor', 'shayad', 'matlab', 'pan', 'mokalyo',
    'acho', 'suthaa', 'pyaaro', 'mehrbani', 'khush', 'aaeindah', 'akhir'
]

def detect_language(text):
    # If user has specified a language preference, always use that
    if st.session_state.user_language_preference:
        return st.session_state.user_language_preference
        
    try:
        # Special case handling for common phrases
        lower_text = text.lower()
        
        # Test for Roman Urdu phrases
        urdu_test_phrases = ['kese ho', 'kaise ho', 'kia hal', 'kia haal', 'ap kese', 'tum kaise', 
                             'kya kar', 'kya ho', 'kidher', 'kahan', 'kyun', 'main', 'mein',
                             'theek', 'acha', 'han', 'nahi', 'bilkul']
        if any(phrase in lower_text for phrase in urdu_test_phrases):
            detected_lang = "roman_ur"
            st.session_state.current_language = detected_lang
            return detected_lang

        # Test for Roman Sindhi phrases
        sindhi_test_phrases = ['cha hal', 'keean ahes', 'keean aahiyan', 'tha kithay', 'cha',
                              'thiyo', 'aahiyan', 'pyaro', 'khush', 'achho', 'budho']
        if any(phrase in lower_text for phrase in sindhi_test_phrases):
            detected_lang = "roman_sd"
            st.session_state.current_language = detected_lang
            return detected_lang
            
        # If there's a conversation and the message is short, maintain the previous language
        if st.session_state.messages and len(text.split()) <= 3:
            return st.session_state.current_language
            
        # Check for Roman Sindhi keywords with more weight for multiple matches
        sindhi_matches = sum(1 for word in roman_sindhi_keywords if word in lower_text)
        if sindhi_matches >= 2 or (sindhi_matches == 1 and len(text.split()) <= 5):
            detected_lang = "roman_sd"
            st.session_state.current_language = detected_lang
            return detected_lang
            
        # Check for Roman Urdu keywords with more weight for multiple matches
        urdu_matches = sum(1 for word in roman_urdu_keywords if word in lower_text)
        if urdu_matches >= 2 or (urdu_matches == 1 and len(text.split()) <= 5):
            detected_lang = "roman_ur"
            st.session_state.current_language = detected_lang
            return detected_lang
            
        # Use langdetect for other languages
        lang = detect(text)
        if lang in ["en", "ur", "hi", "sd"]:
            # Map Hindi to Urdu as they're very similar for this use case
            if lang == "hi":
                lang = "ur"
            detected_lang = lang
            st.session_state.current_language = detected_lang
            return detected_lang
            
        # Default to English or previous language
        if st.session_state.current_language and st.session_state.current_language != "en":
            return st.session_state.current_language
        return "en"
    except LangDetectException:
        # Keep previous language if detection fails
        return st.session_state.current_language

# ---------- Initialize Gemini Chat ----------
if "chat" not in st.session_state and not st.session_state.processing_message:
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    st.session_state.chat = model.start_chat(history=[
        {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages
    ])

# ---------- Show All Messages ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------- User Input and privacy note ----------
# Add custom styling for chat input to ensure visibility in dark mode on mobile
st.markdown(f"""
    <style>
    .stChatInput {{{{  /* Double braces to escape inside f-string */
        background-color: {dark_bg if st.session_state.dark_mode else light_bg} !important;
    }}}}
    .stChatInput > div {{{{  /* Double braces to escape inside f-string */
        background-color: {input_bg} !important;
    }}}}
    .stChatInput textarea {{{{  /* Double braces to escape inside f-string */
        color: {dark_text if st.session_state.dark_mode else light_text} !important;
        background-color: {input_bg} !important;
        caret-color: {dark_text if st.session_state.dark_mode else light_text} !important;
    }}}}
    </style>
""", unsafe_allow_html=True)

prompt = st.chat_input("Ask me anything...")

# Show privacy note under the input box
st.markdown("""
    <div style='text-align: center; padding-top: 5px; font-size: 12px; color: gray;'>
    🔐 Please do not share your personal information to maintain your privacy.
    </div>
""", unsafe_allow_html=True)

if prompt and not st.session_state.processing_message:
    # Set processing flag to prevent duplication
    st.session_state.processing_message = True
    
    # Add user message to chat
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        # Detect language from user input
        language = detect_language(prompt)
        
        # Store detected language in session state for continuity
        st.session_state.current_language = language
        
        # Personality and context for more natural responses
        bot_persona = {
            "en": """You are a helpful, friendly AI assistant that can help with almost anything the user asks. 
                 You speak in a warm, conversational tone and use natural language with occasional emojis where appropriate. 
                 You're knowledgeable, clear, and concise when providing information, writing code, telling stories, or assisting with various tasks.
                 When responding to questions, provide thoughtful, personalized answers as if chatting with a friend.
                 Avoid robotic responses and respond like a supportive human assistant would.""",
                 
            "ur": """آپ ایک مددگار، دوستانہ اے آئی اسسٹنٹ ہیں جو تقریباً ہر وہ چیز کر سکتے ہیں جو صارف پوچھے۔
                 آپ گرم جوشی سے بات کرتے ہیں اور قدرتی زبان استعمال کرتے ہیں، مناسب جگہوں پر ایموجیز بھی شامل کرتے ہیں۔
                 آپ معلومات فراہم کرنے، کوڈ لکھنے، کہانیاں سنانے، یا مختلف کاموں میں مدد کرنے میں عالم، واضح اور مختصر ہیں۔
                 سوالات کے جواب دیتے وقت، ایک دوست کی طرح سوچے سمجھے، ذاتی جوابات دیں۔
                 روبوٹ جیسے جوابات سے بچیں اور ایک مددگار انسانی اسسٹنٹ کی طرح جواب دیں۔""",
                 
            "sd": """توهان هڪ مددگار، دوستاڻو اي آءِ اسسٽنٽ آهيو جيڪو تقريبن هر اها شيء ڪري سگهو ٿا جيڪا صارف پڇي.
                 توهان گرم جوشيءَ سان ڳالهايو ٿا ۽ فطري زبان استعمال ڪريو ٿا، مناسب جاين تي ايموجيز به شامل ڪريو ٿا.
                 توهان معلومات فراهم ڪرڻ، ڪوڊ لکڻ، ڪهاڻيون ٻڌائڻ، يا مختلف ڪمن ۾ مدد ڪرڻ ۾ عالم، واضح ۽ مختصر آهيو.
                 سوالن جا جواب ڏيندي، هڪ دوست جي طرح سوچي سمجهي، ذاتي جواب ڏيو.
                 روبوٽ جهڙن جوابن کان پاسو ڪريو ۽ هڪ مددگار انساني اسسٽنٽ جي طرح جواب ڏيو.""",
                 
            "roman_ur": """Aap aik helpful, friendly AI assistant hain jo taqreeban har wo cheez kar sakte hain jo user poochay.
                 Aap garm joshi se baat karte hain aur natural language istemal karte hain, emojis bhi appropriate jagah pe use karte hain.
                 Aap information provide karne, code likhne, kahaniyan sunane, ya mukhtalif kamon mein madad karne mein aalim, wazeh aur mukhtasar hain.
                 Sawalaat ke jawab dete waqt, thoughtful aur personalized answers dein, jaise ke aap kisi dost se baat kar rahe hon.
                 Robotic responses se bachein aur aik supportive human assistant ki tarah jawab dein.""",
                 
            "roman_sd": """Tavheen hik helpful, friendly AI assistant aahyo jeko taqreeban har uha shay kare sagho tho jeka user puche.
                 Tavheen garam joshi saan galhaayo tha aur natural language istemal kayo tha, emojis bi appropriate jayen te use kayo tha.
                 Tavheen information muhaya karan, code likhan, kahaniyon budhayan, ya mukhtalif kaman men madad karan men aalim, wazeh aur mukhtasar aahyo.
                 Sawalan ja jawab dindo waqt, sochyo samjhyo, zati jawab diyo, jayen te tavheen khangi dost saan galhayo tha.
                 Robotic responses khan bacho aur hik madad kanda insani assistant ji tarah jawab diyo."""
        }
        
        # Career context for more relevant responses
        career_context = {
            "en": """I understand various career challenges and can provide tailored advice for:
                 - Career transitions and job searching
                 - Resume/CV optimization and interview preparation
                 - Skill development and educational decisions
                 - Workplace conflicts and professional growth
                 - Entrepreneurship and freelancing
                 - Work-life balance and burnout prevention""",
                 
            "ur": """مجھے مختلف کیریئر چیلنجز کا علم ہے اور میں مندرجہ ذیل معاملات میں ڈھالے گئے مشورے دے سکتا ہوں:
                 - کیریئر کی تبدیلی اور نوکری کی تلاش
                 - ریزیومے/سی وی کی اصلاح اور انٹرویو کی تیاری
                 - ہنر کی ترقی اور تعلیمی فیصلے
                 - کام کی جگہ پر تنازعات اور پیشہ ورانہ ترقی
                 - کاروبار اور آزاد پیشہ
                 - کام اور زندگی کا توازن اور تھکاوٹ سے بچاؤ""",
                 
            "sd": """مون کي مختلف ڪيريئر چئلينجز جي ڄاڻ آهي ۽ آئون هيٺين معاملن ۾ مناسب صلاح ڏئي سگھان ٿو:
                 - ڪيريئر جي تبديلي ۽ نوڪري جي ڳولا
                 - ريزيومي/سي وي جي بهتري ۽ انٽرويو جي تياري
                 - هنر جي ترقي ۽ تعليمي فيصلا
                 - ڪم جي جاءِ تي تنازعن ۽ پيشه وراڻي ترقي
                 - ڪاروبار ۽ آزاد پيشه
                 - ڪم ۽ زندگي جو توازن ۽ ٿڪاوٽ کان بچاءُ""",
                 
            "roman_ur": """Mujhe mukhtalif career challenges ka ilm hai aur main darj zail mein tailored advice de sakta hun:
                 - Career transitions aur job searching
                 - Resume/CV ki optimization aur interview preparation
                 - Skill development aur educational decisions
                 - Workplace conflicts aur professional growth
                 - Entrepreneurship aur freelancing
                 - Work-life balance aur burnout prevention""",
                 
            "roman_sd": """Mun khe mukhtalif career challenges ji knowledge ahe aur aan hetheyan case men suitable advice dei saghyan tho:
                 - Career transitions aur job searching
                 - Resume/CV ji optimization aur interview preparation
                 - Skill development aur educational decisions
                 - Workplace conflicts aur professional growth
                 - Entrepreneurship aur freelancing
                 - Work-life balance aur burnout prevention"""
        }
        
        # Conversation style guides for more natural dialogue
        conversation_style = {
            "en": """I'll keep my responses conversational, friendly, and helpful. I'll use natural language patterns with varied sentence structures and an engaging tone. I might use rhetorical questions, personal anecdotes, or thoughtful pauses where appropriate.""",
            
            "ur": """میں اپنے جوابات کو گفتگو کے انداز میں، دوستانہ، اور مددگار رکھوں گا۔ میں قدرتی زبان کے نمونے استعمال کروں گا جس میں مختلف جملوں کی ساخت اور دلچسپ لہجہ ہوگا۔ میں مناسب جگہوں پر بلاغتی سوالات، ذاتی واقعات، یا سوچ بھرے وقفے استعمال کر سکتا ہوں۔""",
            
            "sd": """آءُ پنهنجي جوابن کي گفتگوءَ جي انداز ۾، دوستاڻي، ۽ مددگار رکندس. آءُ قدرتي ٻوليءَ جا نمونا استعمال ڪندس جن ۾ مختلف جملن جي ساخت ۽ دلچسپ لهجو هوندو. آءُ مناسب جاين تي بلاغتي سوال، ذاتي واقعا، يا سوچ ڀريل مهلت استعمال ڪري سگھان ٿو.""",
            
            "roman_ur": """Main apne jawabat ko guftugu ke andaz mein, dostana, aur helpful rakhun ga. Main natural language patterns use karun ga jis mein mukhtalif jumlon ki sakht aur engaging tone hogi. Main munasib jaghon par balaaghati sawalaat, zaati waqiyaat, ya soch bhare mawaqe istemal kar sakta hun.""",
            
            "roman_sd": """Aan panhnje jawaban khe guftugu je andaz men, dostana, aur helpful rakhandus. Aan natural language patterns istemal kandus jin men mukhtalif jumlan ji sakht aur engaging tone hondi. Aan munasib jayen te balaaghati sawal, zati waqia, ya soch bharyal waqfa istemal kare saghyan tho."""
        }
        
        # Combine instructions for a comprehensive but CONCISE prompt
        system_instruction = {
            "en": f"""You are an AI Assistant Bot that can help with almost anything. Answer CONCISELY with a maximum of 2-3 sentences. Be direct and simple. Use 1-2 emojis maximum. 

DO NOT WRITE LONG PARAGRAPHS. Keep answers short, simple, and to the point.

Even for complex questions, break down your answer into bullet points if needed, but keep the total response brief.""",
            
            "ur": f"""آپ ایک ای آئی اسسٹنٹ بوٹ ہیں جو تقریباً ہر چیز میں مدد کر سکتے ہیں۔ مختصر اور سیدھے جواب دیں، زیادہ سے زیادہ 2-3 جملوں میں۔ سادہ اور براہ راست بات کریں۔ زیادہ سے زیادہ 1-2 ایموجی استعمال کریں۔

لمبے پیراگراف نہ لکھیں۔ جوابات مختصر، آسان، اور مقصد تک محدود رکھیں۔

پیچیدہ سوالات کے لیے بھی، اگر ضروری ہو تو اپنے جواب کو بلٹ پوائنٹس میں تقسیم کریں، لیکن مجموعی جواب مختصر رکھیں۔""",
            
            "sd": f"""توهان هڪ ائي آئي اسسٽنٽ بوٽ آهيو جيڪو تقريبن هر شيء ۾ مدد ڪري سگهو ٿو۔ مختصر ۽ سڌي جواب ڏيو، وڌيڪ ۾ وڌيڪ 2-3 جملن ۾. سادو ۽ سڌو ڳالهايو. وڌيڪ ۾ وڌيڪ 1-2 ايموجي استعمال ڪريو.

ڏڪا پيراگراف نه لکو۔ جواب مختصر، سادا، ۽ مقصد تائين محدود رکو.

اڋيوڪڻين سوالن لاءَ به، جيڪڏهن ضروري هجي ته پنهنجي جواب کي بليٽ پوائينٽس ۾ ورهايو، پر سموري جواب مختصر رکو.""",
            
            "roman_ur": f"""Aap aik AI Assistant Bot hain jo taqreeban har cheez mein madad kar sakte hain. Mukhtasir aur seedhe jawab dein, ziada se ziada 2-3 jumlon mein. Sadah aur baraah rast baat karein. Ziada se ziada 1-2 emojis istemal karein.

Lambe paragraphs na likhein. Jawabaat mukhtasir, aasan, aur maqsad tak mehdood rakhein.

Pechida sawalaat ke liye bhi, agar zaroori ho to apne jawab ko bullet points mein taqseem karein, lekin majmui jawab mukhtasir rakhein.""",
            
            "roman_sd": f"""Tavheen hik AI Assistant Bot aahyo jeko taqreeban har shay men madad kare sagho tho. Mukhtasir te sudho jawab diyo, wadheek 2-3 jumlan men. Sadho te sudho galhayo. Wadheek 1-2 emojis istemal kayo.

Dhaga paragraphs na likho. Jawab mukhtasir, asaan, te maqsad taaen mehdood rakho.

Pechida sawalan lae bi, jeker zaroori huje ta panhjo jawab bullet points men warrhayo, par samuro jawab mukhtasir rakho."""
        }
        
        # Create prompt with language instruction, user message, and context
        final_prompt = f"{system_instruction.get(language, system_instruction['en'])}\n\nUser message: {prompt}\n\nKeep your response very concise, direct, and short, responding in {language} language. Remember that you can help with almost anything including writing code, stories, and providing various types of information."

        with st.chat_message("assistant"):
            dots_placeholder = st.empty()
            dots_html = """<div class="typing-dots"><span></span><span></span><span></span></div>"""
            for _ in range(2):
                dots_placeholder.markdown(dots_html, unsafe_allow_html=True)
                time.sleep(0.2)

            response = st.session_state.chat.send_message(final_prompt)
            output = response.text
            dots_placeholder.empty()
            st.markdown(output, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": output})
        
    except Exception as e:
        st.error(f"Error: {e}")
    
    # Reset processing flag and rerun to update UI
    st.session_state.processing_message = False
    st.rerun()


