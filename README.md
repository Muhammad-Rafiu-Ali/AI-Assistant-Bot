## 🤖 AI Assistant Bot — Your Smart AI Guide for Everything 🚀

An intelligent and friendly AI chatbot built using **Streamlit** and **Google's Gemini API**. This assistant helps users with a wide range of queries in multiple languages, offering quick, smart, and helpful responses. Perfect for showcasing AI-powered assistance in a demo or sharing with friends!

---

### 🌟 Features

* ✅ Built with [Streamlit](https://streamlit.io/)
* 🧠 Powered by **Google Gemini Pro**
* 🌍 Multilingual: English, Urdu, Roman Urdu, Roman Sindhi
* 🌙 Dark/Light Mode Toggle
* 💬 Save, View, and Download Chat History
* 🎨 Custom UI with Logo
* 📁 Easy Deployment (Local + Cloud)

---

### 🔧 Requirements

Install the required Python libraries:

```bash
pip install streamlit google-generativeai Pillow langdetect
```

---

### 🔑 Set Up API Key

Set your **Gemini API Key** as an environment variable:

**Linux/macOS:**

```bash
export GEMINI_API_KEY=your_api_key_here
```

**Windows (CMD):**

```bash
set GEMINI_API_KEY=your_api_key_here
```

Or inside the app, use:

```python
os.environ["GEMINI_API_KEY"] = "your_api_key_here"
```

---

### ▶️ How to Run

```bash
streamlit run app.py
```

Visit: `http://localhost:8501` in your browser.

---

### 📁 Project Structure

```
project/
├── app.py                    # Streamlit chatbot app
├── logo.png                  # Logo displayed in sidebar
├── requirements.txt          # Required Python packages
├── .env                      # Local API key (for development)
├── .streamlit/
│   └── secrets.toml          # Secure API key (for deployment)
└── README.md                 # This file

```

---

### 🚀 Deploy for Free (Streamlit Cloud)

1. Push code to **GitHub**
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Create new app → Select your repo and branch
4. Set `app.py` as the main file
5. Go to **Settings > Secrets** and add:

   ```
   GEMINI_API_KEY = your_actual_key_here
   ```
6. Share the link with friends! 🌐

---

### 👤 Developer

**Rafiu Ali Memon**
📍 Data Science & AI Enthusiast
🔗 [LinkedIn](https://linkedin.com/in/rafiu-ali) | 🐙 [GitHub](https://github.com/Muhammad-Rafiu-Ali)

---


