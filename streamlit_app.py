import os
import json
import streamlit as st
from groq import Groq

# =========================
#   הגדרות עמוד
# =========================
st.set_page_config(
    page_title="PackBot AI",
    page_icon="🧳",
    layout="centered"
)

# =========================
#   עיצוב מותאם מובייל + RTL, בלי סיידבר
# =========================
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    [data-testid="stAppViewContainer"] > .main {
        max-width: 480px;
        margin: 0 auto;
        padding: 0.75rem 0.75rem 2.75rem 0.75rem;
    }

    .stChatMessage {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stMarkdownContainer"] {
        text-align: right;
    }

    h1 {
        text-align: center;
        font-size: 1.6rem;
        margin-bottom: 0.1rem;
    }

    .sub-caption {
        text-align: center;
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.8rem;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .step-title {
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .step-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("PackBot AI 🧳")
st.markdown(
    '<div class="sub-caption">אשף חכם לבניית רשימת ציוד מותאמת אישית</div>',
    unsafe_allow_html=True
)

# =========================
#   מפתח Groq (מ-Secrets בלבד)
# =========================
api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    st.error(
        "לא נמצא GROQ_API_KEY.\n\n"
        "ב-Streamlit Cloud: היכנס ל-Settings → Secrets והוסף שורה:\n"
        'GROQ_API_KEY = "gsk_XXXXXXXXXXXX"\n\n'
        "את המפתח יוצרים בחשבון החינמי ב-console.groq.com."
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================
#   אתחול state
# =========================
DEFAULT_DATA = {
    "destination": "",
    "trip_name": "",
    "days": 3,
    "travellers": "",
    "kids": "",
    "weather": "",
    "trip_style": [],
    "luggage": "",
    "laundry": False,
    "special_activities": "",
    "notes": ""
}

if "step" not in st.session_state:
    st.session_state.step = 0

if "form_data" not in st.session_state:
    st.session_state.form_data = DEFAULT_DATA.copy()

if "packing_text" not in st.session_state:
    st.session_state.packing_text = ""


def reset_all():
    st.session_state.step = 0
    st.session_state.form_data = DEFAULT_DATA.copy()
    st.session_state.packing_text = ""


# =========================
#   פונקציה שמדברת עם Groq
# =========================
def generate_packing_list(data: dict) -> str:
    system_prompt = (
        "אתה PackBot, מומחה אריזה. "
        "אתה מקבל נתוני נסיעה מובנים בפורמט JSON, ועל בסיסם אתה יוצר רשימת ציוד מדויקת.\n\n"
        "פורמט הפלט חשוב מאוד:\n"
        "1. שורה ראשונה: כותרת, למשל 'רשימת ציוד נסיעה ל<יעד>' או 'רשימת ציוד שהייה'.\n"
        "2. שורה שנייה: ריקה.\n"
        "3. משם והלאה: כל פריט בשורה נפרדת, בלי מספרים, בלי מקפים, בלי נקודות.\n"
        "4. בלי טקסט הסבר לפני או אחרי, בלי אמוג׳י, בלי סוגריים.\n"
        "5. הרשימה צריכה להיות תמציתית אבל מעשית, מותאמת לנתוני הנסיעה.\n"
        "6. כתוב הכל בעברית.\n"
    )

    user_prompt = (
        "להלן פרטי הנסיעה בפורמט JSON. "
        "על בסיסם צור רשימת ציוד בפורמט שצוין:\n\n"
        + json.dumps(data, ensure_ascii=False, indent=2)
    )

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    return completion.choices[0].message.content.strip()


# =========================
#   UI – אשף שלבים
# =========================
data = st.session_state.form_data
step = st.session_state.step

st.progress((step) / 6.0 if step <= 6 else 1.0)

# ----- שלב 0: יעד ושם נסיעה -----
if step == 0:
    st.markdown('<div class="step-title">1. היעד והכותרת</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">נתחיל בלעשות סדר: לאן הנסיעה ואיך תרצה לקרוא לה ברשימה?</div>',
        unsafe_allow_html=True
    )

    data["destination"] = st.text_input("לאן הנסיעה?", value=data["destination"], placeholder="לונדון, אילת, ארה״ב...")

    data["trip_name"] = st.text_input(
        "כותרת לרשימה (אופציונלי)",
        value=data["trip_name"],
        placeholder="רשימת ציוד שהייה, רשימת ציוד לטיסה לניו-יורק..."
    )

    if st.button("המשך ➜", use_container_width=True, disabled=(data["destination"].strip() == "")):
        st.session_state.step = 1

# ----- שלב 1: משך הנסיעה -----
elif step == 1:
    st.markdown('<div class="step-title">2. כמה זמן אתם נוסעים?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">המשך השהייה משפיע על כמות הבגדים והציוד.</div>',
        unsafe_allow_html=True
    )

    data["days"] = st.number_input("מספר לילות מחוץ לבית", min_value=1, max_value=60, value=int(data["days"] or 3))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 0
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 2

# ----- שלב 2: מי נוסע -----
elif step == 2:
    st.markdown('<div class="step-title">3. מי נוסע?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">כך נדע להתאים כמויות וציוד מיוחד.</div>',
        unsafe_allow_html=True
    )

    data["travellers"] = st.radio(
        "בחר אפשרות אחת:",
        options=["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"],
        index=["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"].index(data["travellers"])
        if data["travellers"] in ["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"] else 0,
    )

    if data["travellers"] in ["זוג עם ילדים", "משפחה / קבוצה"]:
        data["kids"] = st.radio(
            "ילדים:",
            options=["בלי ילדים", "עם ילדים קטנים", "עם ילדים גדולים"],
            index=["בלי ילדים", "עם ילדים קטנים", "עם ילדים גדולים"].index(data["kids"])
            if data["kids"] in ["בלי ילדים", "עם ילדים קטנים", "עם ילדים גדולים"] else 1,
        )
    else:
        data["kids"] = "בלי ילדים"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 1
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 3

# ----- שלב 3: מזג אוויר -----
elif step == 3:
    st.markdown('<div class="step-title">4. מזג האוויר המשוער</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">הערכה גסה מספיקה – רק כדי להבין איזה ביגוד צריך.</div>',
        unsafe_allow_html=True
    )

    options = ["חם מאוד", "נעים", "קריר", "קר מאוד / שלג"]
    current_index = options.index(data["weather"]) if data["weather"] in options else 1

    data["weather"] = st.radio(
        "איך כנראה יהיה שם?",
        options=options,
        index=current_index
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 2
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 4

# ----- שלב 4: אופי הטיול -----
elif step == 4:
    st.markdown('<div class="step-title">5. סוג החופשה</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">אפשר לבחור יותר מאפשרות אחת.</div>',
        unsafe_allow_html=True
    )

    styles = [
        "עיר / שופינג",
        "בטן-גב / ים / בריכה",
        "טרק / טבע",
        "נסיעת עבודה",
        "מסיבה / אירוע מיוחד"
    ]

    data["trip_style"] = st.multiselect(
        "מה הכי מתאים?",
        options=styles,
        default=data["trip_style"] or []
    )

    data["special_activities"] = st.text_input(
        "משהו מיוחד שצריך לקחת בחשבון? (אופציונלי)",
        value=data["special_activities"],
        placeholder="למשל: הופעה, חתונה, ספורט, ציוד צילום..."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 3
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 5

# ----- שלב 5: מזוודה, כביסה, הערות -----
elif step == 5:
    st.markdown('<div class="step-title">6. ציוד נסיעה כללי</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">עוד רגע יש לך רשימה מלאה.</div>',
        unsafe_allow_html=True
    )

    luggage_options = ["טרולי קטן", "מזוודה בינונית", "מזוודה גדולה", "תרמיל גב לטיולים"]
    current_index = luggage_options.index(data["luggage"]) if data["luggage"] in luggage_options else 1

    data["luggage"] = st.radio(
        "מה הכלי העיקרי שבו אתה אורז?",
        options=luggage_options,
        index=current_index
    )

    data["laundry"] = st.checkbox("כנראה שתעשו כביסה במהלך הנסיעה", value=bool(data["laundry"]))

    data["notes"] = st.text_area(
        "העדפות אישיות / דברים חשובים (אופציונלי)",
        value=data["notes"],
        placeholder="לדוגמה: חייב לזכור תרופות, רוצה מינימום ציוד, צריך מקום למתנות..."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 4
    with col2:
        if st.button("צור רשימת ציוד ✅", use_container_width=True):
            with st.spinner("מחשב עבורך רשימה חכמה..."):
                st.session_state.packing_text = generate_packing_list(data)
                st.session_state.step = 6

# ----- שלב 6: תוצאה סופית -----
else:
    st.markdown('<div class="step-title">רשימת הציוד שלך מוכנה</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">אפשר להעתיק ישירות ל״פתקים״ או לשמור כקובץ.</div>',
        unsafe_allow_html=True
    )

    if st.session_state.packing_text:
        st.text_area(
            "העתק את הטקסט כמו שהוא (Ctrl+C / לחיצה ארוכה והעתק):",
            value=st.session_state.packing_text,
            height=380,
        )

        st.download_button(
            "📥 הורד כקובץ TXT",
            data=st.session_state.packing_text,
            file_name="packing_list.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.warning("לא נוצרה עדיין רשימת ציוד. חזור אחורה וסיים למלא את השאלון.")

    if st.button("🔁 התחל שאלון חדש", use_container_width=True):
        reset_all()