import streamlit as st
import google.generativeai as genai

# --- הגדרות עמוד ---
st.set_page_config(page_title="PackBot AI", page_icon="🧳", layout="centered")

# --- עיצוב ---
st.markdown("""
<style>
    .stChatMessage {direction: rtl; text-align: right;}
    .stChatInput {direction: rtl;}
    div[data-testid="stMarkdownContainer"] {text-align: right;}
    h1 {text-align: center;}
    .stButton button {width: 100%;}
</style>
""", unsafe_allow_html=True)

st.title("🧳 PackBot AI")
st.caption("מופעל ע\"י Google Gemini - חכם, מהיר וחינמי")

# --- סרגל צד למפתח ---
with st.sidebar:
    st.header("הגדרות")
    api_key = "AIzaSyC37M65UwKU3RuKXMb9W6TFCq7IB8yrGS8"
    st.markdown("[קבל מפתח בחינם כאן](https://aistudio.google.com/app/apikey)")
    if not api_key:
        st.warning("חובה להכניס מפתח כדי להתחיל.")

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["היי! אני מומחה האריזה שלך. לאן טסים ומתי? תהיה ספציפי כדי שאוכל לתת טיפים מעולים."]}
    ]

# --- פונקציה לפניה לגוגל ---
def ask_gemini(prompt, key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-pro')
        
        # יצירת היסטוריה בפורמט של גוגל
        chat = model.start_chat(history=st.session_state.messages[:-1]) # שולחים את ההיסטוריה ללא ההודעה האחרונה כי נוסיף אותה ידנית
        
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה: {str(e)}. ודא שהמפתח תקין."

# --- הצגת השיחה ---
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    st.chat_message(role).write(msg["parts"][0])

# --- טיפול בקלט ---
if prompt := st.chat_input("כתוב כאן..."):
    if not api_key:
        st.error("נא להזין API Key בסרגל הצד")
        st.stop()

    # הצגת הודעת המשתמש
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # קבלת תשובה
    with st.spinner("חושב..."):
        ai_response = ask_gemini(prompt, api_key)

    # הצגת התשובה
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})

