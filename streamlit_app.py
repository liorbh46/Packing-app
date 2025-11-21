import streamlit as st
import google.generativeai as genai

# --- הגדרות עמוד ---
st.set_page_config(page_title="PackBot AI", page_icon="🧳", layout="centered")

# --- הטמעת המפתח שלך ---
# שים לב: בגלל שפרסמת את המפתח כאן, מומלץ בעתיד למחוק אותו וליצור חדש בגוגל.
# בינתיים זה יעבוד מעולה.
API_KEY = "AIzaSyC37M65UwKU3RuKXMb9W6TFCq7IB8yrGS8"

# --- הגדרת המודל ---
try:
    genai.configure(api_key=API_KEY)
    # שימוש במודל Flash המהיר והעדכני
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"שגיאה בהגדרת המפתח: {e}")

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
st.caption("מופעל ע\"י Google Gemini")

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["היי! אני מומחה האריזה שלך. לאן טסים ומתי? תהיה ספציפי כדי שאוכל לתת טיפים מעולים."]}
    ]

# --- פונקציה לפניה לגוגל ---
def ask_gemini(prompt):
    try:
        # יצירת היסטוריה
        history = []
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": msg["parts"]})
            
        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        # אם יש שגיאה, ננסה מודל גיבוי ישן יותר
        try:
            fallback_model = genai.GenerativeModel('gemini-pro')
            chat = fallback_model.start_chat(history=history)
            response = chat.send_message(prompt)
            return response.text
        except:
            return f"שגיאה: {str(e)}. ודא שהמפתח תקין ושקובץ requirements.txt מעודכן."

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
    with st.spinner("חושב..."):
        ai_response = ask_gemini(prompt)

    # הצגת התשובה
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})
