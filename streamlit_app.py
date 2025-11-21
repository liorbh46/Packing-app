import streamlit as st
import os
from openai import OpenAI

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
st.caption("מופעל ע\"י OpenAI GPT")

# --- קבלת מפתח API ---
# אפשר דרך משתנה סביבה (OPENAI_API_KEY) או דרך ה-UI
api_key_env = os.getenv("OPENAI_API_KEY", "")

with st.sidebar:
    st.markdown("### 🔑 OpenAI API Key")
    st.caption("לא לשתף, לא להעלות ל-GitHub. מומלץ לשים כ־secret ב-Streamlit או כמשתנה סביבה.")
    api_key = st.text_input("הדבק כאן את ה-API Key שלך", value=api_key_env, type="password")

if not api_key:
    st.warning("יש להזין OpenAI API Key כדי להשתמש בבוט.")
    st.stop()

# יצירת לקוח OpenAI
client = OpenAI(api_key=api_key)

# --- ניהול זיכרון השיחה ---
# נשמור פורמט פשוט: role = "user"/"assistant", content = טקסט
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "היי! אני מומחה האריזה שלך. לאן טסים ומתי?"}
    ]

# --- פונקציה לפניה ל-OpenAI ---
def ask_openai():
    """
    בונה את כל ההיסטוריה בפורמט messages של OpenAI ושולח למודל.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "אתה PackBot, מומחה אריזה חכם. "
                "תנהל שיחה נעימה וקצרה בעברית, תשאל שאלות על הנסיעה, "
                "ובסוף תעזור למשתמש לבנות רשימת אריזה מסודרת, מותאמת ליעד, משך, מזג אוויר ומי נוסע."
            ),
        }
    ]

    for msg in st.session_state.messages:
        messages.append(
            {
                "role": msg["role"],       # 'user' או 'assistant'
                "content": msg["content"], # הטקסט עצמו
            }
        )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",   # אפשר להחליף לדגם אחר אם יש לך
        messages=messages,
        temperature=0.6,
    )

    return completion.choices[0].message.content

# --- הצגת השיחה הקודמת ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- קלט חדש מהמשתמש ---
if prompt := st.chat_input("כתוב כאן..."):
    # 1. להציג ולשמור את הודעת המשתמש
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. לשלוח ל-OpenAI
    with st.spinner("אורז מחשבות..."):
        ai_response = ask_openai()

    # 3. להציג ולשמור את תגובת המודל
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
