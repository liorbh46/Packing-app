import streamlit as st
from duckduckgo_search import DDGS

# --- הגדרות עמוד ---
st.set_page_config(page_title="PackBot Genius", page_icon="🧠", layout="centered")

# --- עיצוב ---
st.markdown("""
<style>
    .stChatMessage {direction: rtl; text-align: right;}
    .stChatInput {direction: rtl;}
    div[data-testid="stMarkdownContainer"] {text-align: right;}
    h1 {text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("🧠 PackBot Genius")
st.caption("AI חכם ואותנטי - בחינם וללא הרשמה")

# --- ניהול זיכרון השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "היי! אני פה כדי לבנות לך רשימה שלא תמצא בשום מקום אחר. לאן טסים ומתי?"}
    ]

# --- הפונקציה שפונה ל-AI החינמי ---
def ask_ai(prompt):
    try:
        # אנחנו מבקשים מה-AI להתנהג כמו מומחה אריזה
        full_prompt = f"""
        אתה מומחה אריזה ונסיעות עולמי. דבר בעברית בלבד.
        המטרה שלך: לעזור למשתמש לארוז בצורה חכמה.
        
        בקשת המשתמש: {prompt}
        
        הנחיות:
        1. אל תיתן סתם רשימות גנריות. תן טיפים ספציפיים ליעד.
        2. אם המשתמש נתן יעד, תחשוב על מזג האוויר, התרבות המקומית, ומה באמת צריך.
        3. תהיה קליל, מצחיק ומועיל.
        4. בסוף, אם צריך, תציע רשימת אריזה מסודרת.
        """
        
        # שליחה ל-DuckDuckGo AI (מודל GPT-4o-mini או Llama בחינם)
        results = DDGS().chat(full_prompt, model='gpt-4o-mini')
        return results
    except Exception as e:
        return "אופס, ה-AI עמוס רגע. נסה שוב בעוד כמה שניות! (שגיאת חיבור)"

# --- הצגת ההיסטוריה ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- הטיפול בקלט המשתמש ---
if user_input := st.chat_input("כתוב כאן..."):
    # 1. הצגת הודעת המשתמש
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # 2. מחשבה... (Spinner)
    with st.spinner("ה-AI בודק את היעד וחושב על רשימה..."):
        # כאן מתרחש הקסם - פנייה ל-AI האמיתי
        ai_response = ask_ai(user_input)

    # 3. הצגת התשובה
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.chat_message("assistant").write(ai_response)
