import os
import streamlit as st
from openai import OpenAI, RateLimitError, APIError

# ============== הגדרות עמוד ==============
st.set_page_config(
    page_title="PackBot AI",
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
st.caption("צ׳אט חכם לבניית רשימת אריזה מותאמת אישית (מופעל ע\"י OpenAI)")

# ============== קריאת ה-API KEY ==============
# המפתח צריך להיות שמור ב-Secrets של Streamlit תחת השם OPENAI_API_KEY
# או כמשתנה סביבה במערכת ההפעלה.
api_key = os.getenv("OPENAI_API_KEY", "")

with st.sidebar:
    st.markdown("### 🔑 מפתח OpenAI")
    st.caption("מומלץ לשמור את המפתח ב-Secrets של Streamlit בשם OPENAI_API_KEY.\n"
               "השדה כאן הוא רק לגיבוי (לשימוש מקומי).")
    manual_key = st.text_input("אם אין SECRET, אפשר להדביק מפתח ידנית:", type="password")
    if manual_key.strip():
        api_key = manual_key.strip()

if not api_key:
    st.error("לא נמצא OpenAI API Key.\n\n"
             "ב-Streamlit Cloud: הוסף ב-Settings → Secrets:\n\n"
             'OPENAI_API_KEY = "sk-..."')
    st.stop()

client = OpenAI(api_key=api_key)

# ============== ניהול זיכרון השיחה ==============
# נשמור שיחה בפורמט הפשוט של OpenAI: role + content
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "היי! אני PackBot, מומחה האריזה שלך. ספר לי בקצרה לאן אתה נוסע ומתי."
        }
    ]

# ============== פונקציה לפניה ל-OpenAI ==============
def ask_openai():
    """
    בונה את ההיסטוריה ושולח למודל.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "אתה PackBot, מומחה אריזה חכם. "
                "אתה מדבר בעברית פשוטה וזורמת, שואל שאלות כדי להבין את הנסיעה "
                "(יעד, תאריכים, מזג אוויר צפוי, מי נוסע, סוג חופשה ועוד), "
                "ובסוף עוזר למשתמש לבנות רשימת אריזה מסודרת, עם ביגוד, היגיינה, אלקטרוניקה, מסמכים, "
                "ודברים מיוחדים לפי מה שסיפר."
            )
        }
    ]

    # מוסיפים את השיחה שהייתה עד עכשיו
    messages.extend(st.session_state.messages)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.6,
        )
        return completion.choices[0].message.content

    except RateLimitError:
        # זה קורה אם אין קרדיט / עברתם את המגבלה בחשבון OpenAI
        return (
            "קיבלתי שגיאת Rate Limit מ-OpenAI.\n"
            "זה בדרך כלל אומר שאין מספיק קרדיט בחשבון ה-API שלך או שעברת את מגבלת השימוש.\n"
            "כדאי להיכנס ל-platform.openai.com → Billing ולבדוק את מצב החיובים/קרדיטים."
        )
    except APIError as e:
        return f"שגיאה מה-API של OpenAI: {str(e)}"
    except Exception as e:
        return f"שגיאה כללית: {str(e)}"


# ============== הצגת היסטוריית השיחה ==============
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ============== קלט מהמשתמש ==============
user_input = st.chat_input("כתוב כאן את התשובה / השאלה שלך...")

if user_input:
    # מציגים ומוסיפים את הודעת המשתמש
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # שולחים ל-OpenAI
    with st.spinner("אורז מחשבות..."):
        ai_response = ask_openai()

    # מציגים ומוסיפים את תגובת המודל
    st.chat_message("assistant").write(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})