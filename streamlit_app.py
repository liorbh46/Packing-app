import streamlit as st
from groq import Groq
import time

# ==========================================
# הגדרות עמוד בסיסיות
# ==========================================
st.set_page_config(
    page_title="PackBot Pro",
    page_icon="🧳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# קבלת המפתח מתוך Secrets
# ==========================================
try:
    # מנסה למשוך את המפתח מהסודות של סטרימליט
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("❌ שגיאה: לא נמצא מפתח GROQ_API_KEY ב-Secrets.")
    st.info("ב-Streamlit Cloud: לך ל-Settings -> Secrets והוסף:\nGROQ_API_KEY = 'gsk_...'")
    st.stop()

client = Groq(api_key=api_key)

# ==========================================
# עיצוב CSS מקצועי (Look & Feel)
# ==========================================
st.markdown("""
<style>
    /* ייבוא פונט מודרני (Rubik) */
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
    }

    /* הסתרת אלמנטים של המערכת למראה נקי */
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* מרכוז וכותרות */
    h1 {
        color: #2E86C1;
        text-align: center;
        font-weight: 700;
        font-size: 2rem;
        margin-top: -50px;
    }
    
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    /* עיצוב בועות הצ'אט */
    .stChatMessage {
        background-color: transparent;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 5px;
    }

    /* צבע רקע להודעות הבוט */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f7f9fc;
        border-right: 3px solid #2E86C1;
    }

    /* הקטנת רווחים מיותרים */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 10rem; /* מקום להקלדה */
    }
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# ניהול מצב (Session State)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "היי! אני PackBot Pro 🤖.\nלאן טסים ומתי? אני אעזור לך לארגן הכל."}
    ]
if "list_ready" not in st.session_state:
    st.session_state.list_ready = False
if "final_text" not in st.session_state:
    st.session_state.final_text = ""

# ==========================================
# לוגיקה - המוח של Groq
# ==========================================
def ask_groq():
    # פרומפט מערכת חכם
    system_prompt = """
    אתה עוזר אריזה מקצועי ותכליתי.
    שלב 1 (ראיון): שאל שאלות קצרות אחת-אחת כדי להבין: יעד, מזג אוויר, מי נוסע, סוג הטיול (עסקים/נופש), והאם עושים כביסה.
    שלב 2 (יצירה): כשיש לך את המידע, או שהמשתמש מבקש, צור את הרשימה.
    
    חשוב מאוד: ברגע שאתה יוצר את הרשימה הסופית, התחל את ההודעה במילים בדיוק: "### הרשימה שלך מוכנה"
    לאחר הכותרת הזו, כתוב את הרשימה בצורה נקייה (בלי כוכביות מודגשות על כל מילה), מסודרת לפי קטגוריות עם אימוג'ים.
    דוגמה לקטגוריה:
    👕 ביגוד
    - 5 חולצות
    - 2 מכנסיים
    """

    messages_payload = [{"role": "system", "content": system_prompt}]
    # הוספת ההיסטוריה
    for msg in st.session_state.messages:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile", # מודל חזק מאוד ומהיר
            messages=messages_payload,
            temperature=0.5,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"שגיאה בתקשורת: {str(e)}"

# ==========================================
# ממשק המשתמש (UI)
# ==========================================

st.title("PackBot Pro 🧳")
st.markdown('<div class="subtitle">מומחה אריזה מבוסס AI</div>', unsafe_allow_html=True)

# הצגת ההיסטוריה
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# בדיקה אם הרשימה מוכנה כדי להציג כפתורים מיוחדים
if st.session_state.list_ready:
    st.success("✅ הרשימה נוצרה בהצלחה!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 הורד כקובץ",
            data=st.session_state.final_text,
            file_name="packing_list.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        if st.button("🔄 התחל מחדש", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "יאללה, מתחילים מחדש. לאן טסים?"}]
            st.session_state.list_ready = False
            st.rerun()

# אזור הקלט (נמצא למטה קבוע)
if prompt := st.chat_input("כתוב תשובה כאן..."):
    # 1. הצגת הודעת משתמש
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. חשיבה ותשובה
    with st.chat_message("assistant"):
        with st.spinner("חושב..."):
            response = ask_groq()
            st.markdown(response)
    
    # 3. שמירה ועיבוד
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # בדיקה אם ה-AI החליט שהרשימה מוכנה
    if "### הרשימה שלך מוכנה" in response:
        st.session_state.list_ready = True
        # ניקוי הטקסט להורדה
        clean_list = response.replace("### הרשימה שלך מוכנה", "").strip()
        st.session_state.final_text = clean_list
        st.rerun() # רענון כדי להציג את הכפתורים


