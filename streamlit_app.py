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
</style>
""", unsafe_allow_html=True)

st.title("🧳 PackBot AI")
st.caption("מופעל ע\"י Google Gemini Pro")

# ---------------------------------------------------------
# המפתח שלך מוטמע כאן בפנים
# ---------------------------------------------------------
my_secret_key = "AIzaSyC37M65UwKU3RuKXMb9W6TFCq7IB8yrGS8"

# --- הגדרת המודל (הגרסה היציבה ביותר) ---
try:
    genai.configure(api_key=my_secret_key)
    # שינוי ל-gemini-pro שעובד תמיד
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"שגיאה בהתחברות: {e}")

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["היי! אני מומחה האריזה שלך. לאן טסים ומתי?"]}
    ]

# --- פונקציה לפניה לגוגל ---
def ask_gemini(prompt):
    try:
        # בניית היסטוריה ללא ההודעה האחרונה
        history = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": msg["parts"]})
            
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"שגיאה: {str(e)}"

# --- הצגת השיחה ---
for msg in st.session_state.messages:
    role = "assistant" if msg["role"] == "model" else "user"
    st.chat_message(role).write(msg["parts"][0])

# --- טיפול בקלט ---
if prompt := st.chat_input("כתוב כאן..."):
    # הצגת הודעת המשתמש
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # קבלת תשובה
    with st.spinner("אורז מחשבות..."):
        ai_response = ask_gemini(prompt)

    # הצגת התשובה
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})
