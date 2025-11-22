import os
import streamlit as st
from groq import Groq

# ============== הגדרות עמוד ==============
st.set_page_config(
    page_title="PackBot AI (Groq)",
    page_icon="🧳",
    layout="centered"
)

# ============== עיצוב בסיסי (ימין-לשמאל) ==============
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
    }
    .stChatMessage {direction: rtl; text-align: right;}
    .stChatInput {direction: rtl;}
    div[data-testid="stMarkdownContainer"] {text-align: right;}
    h1 {text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("🧳 PackBot AI")
st.caption("צ'אט חכם לבניית רשימת אריזה – רץ על Groq + Llama 3.1 (חינם)")

# ============== מפתח Groq ==============
# המומלץ: לשים את המפתח כ-SECRET ב-Streamlit בשם GROQ_API_KEY
# Settings → Secrets →  GROQ_API_KEY = "gsk_...."
api_key = os.getenv("GROQ_API_KEY", "")

with st.sidebar:
    st.markdown("### 🔑 Groq API Key")
    st.caption(
        "מומלץ לשמור את המפתח ב-Secrets של Streamlit בשם GROQ_API_KEY.\n"
        "השדה כאן הוא רק לגיבוי (לבדיקות מקומיות)."
    )
    manual_key = st.text_input("אם אין SECRET, אפשר להדביק פה את המפתח:", type="password")
    if manual_key.strip():
        api_key = manual_key.strip()

if not api_key:
    st.error(
        "לא נמצא Groq API Key.\n\n"
        "ב-Streamlit Cloud: היכנס ל-Settings → Secrets והוסף שורה:\n\n"
        'GROQ_API_KEY = "gsk_XXXXXXXXXXXX"\n\n'
        "את המפתח יוצרים בחשבון החינמי שלך ב-console.groq.com."
    )
    st.stop()

# יצירת לקוח Groq
client = Groq(api_key=api_key)

# ============== ניהול זיכרון השיחה ==============
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "היי! אני PackBot, מומחה האריזה שלך. ספר בקצרה לאן אתה נוסע ומתי."
        }
    ]

# ============== פונקציה ששואלת את המודל ==============
def ask_groq():
    """
    שולח את כל השיחה למודל Llama 3.1 דרך Groq ומחזיר תשובה.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "אתה PackBot, מומחה אריזה חכם. "
                "אתה מדבר בעברית פשוטה וזורמת, שואל שאלות כדי להבין את הנסיעה "
                "(יעד, תאריכים, מזג אוויר משוער, מי נוסע, סוג חופשה, ציוד מיוחד וכו'), "
                "ובסוף עוזר למשתמש לבנות רשימת אריזה מסודרת ומפורטת. "
                "תן תשובות ברורות, נוחות לקריאה, עם רשימות נקודתיות כשצריך."
            )
        }
    ]

    messages.extend(st.session_state.messages)

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # מודל חינמי ומהיר
            messages=messages,
            temperature=0.6,
        )
        return completion.choices[0].message.content

    except Exception as e:
        # אם יש שגיאה (למשל מפתח לא תקין / חוסר הרשאות) – נחזיר טקסט ברור
        return f"שגיאה בשיחה עם Groq: {str(e)}"


# ============== הצגת היסטוריית השיחה ==============
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ============== קלט מהמשתמש ==============
user_input = st.chat_input("כתוב כאן את התשובה / השאלה שלך...")

if user_input:
    # מציגים ושומרים את הודעת המשתמש
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # שואלים את Groq
    with st.spinner("אורז מחשבות..."):
        ai_response = ask_groq()

    # מציגים ושומרים את תגובת המודל
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})