import os
import json
import streamlit as st
from groq import Groq

# =========================
# עיצוב גלובלי מודרני + RTL + מובייל
# =========================
st.set_page_config(
    page_title="PackBot AI",
    page_icon="🧳",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    html, body, [class*="css"] {
        direction: rtl;
        font-family: 'Assistant', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f9fafb;
        color: #374151;
    }
    [data-testid="stAppViewContainer"] > .main {
        max-width: 570px;
        margin: 2rem auto 3rem;
        background: #fff;
        padding: 1.4rem 1.6rem 2.8rem;
        box-shadow: 0 4px 8px rgb(0 0 0 / 0.05);
        border-radius: 10px;
    }
    .stChatMessage, div[data-testid="stMarkdownContainer"] {
        text-align: right;
    }
    h1 {
        font-weight: 700;
        font-size: 1.7rem;
        margin-bottom: 0.3rem;
        text-align: center;
        color: #111827;
    }
    .sub-caption {
        text-align: center;
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.1rem;
    }
    .step-title {
        font-weight: 700;
        font-size: 1.15rem;
        margin-bottom: 0.3rem;
        color: #111827;
    }
    .step-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }
    button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 700;
        font-size: 1.05rem !important;
    }
    button[disabled] {
        background-color: #9ca3af !important;
        cursor: not-allowed !important;
        color: white !important;
    }
    .stCheckbox > label {
        font-size: 0.95rem;
    }
    .stTextInput > div > input, .stNumberInput > label > div > input,
    textarea, select {
        font-size: 1rem;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1.8px solid #d1d5db;
        background-color: #f3f4f6;
        transition: border-color 0.2s ease-in-out;
    }
    .stTextInput > div > input:focus, .stNumberInput > label > div > input:focus,
    textarea:focus, select:focus {
        border-color: #3b82f6;
        background-color: white;
        outline: none;
    }
    .footer-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: 1.4rem;
    }
    @media (max-width: 400px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 1rem;
            margin: 1rem auto 2rem;
        }
        .footer-buttons {
            flex-direction: column;
            gap: 0.6rem;
        }
        .footer-buttons > button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# =========================
# ראשים ומיתוג
# =========================
st.markdown(
    """
    <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-bottom: 10px;">
        <img src="https://cdn-icons-png.flaticon.com/512/2972/2972444.png" alt="Logo" width="38" style="border-radius:10px;">
        <h1>PackBot AI 🧳</h1>
    </div>
    """, unsafe_allow_html=True
)

st.markdown('<div class="sub-caption">אשף חכם לבניית רשימת ציוד יסודית לכל סוג נסיעה</div>', unsafe_allow_html=True)

# =========================
# התחברות ל-GROQ API
# =========================
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.error(
        "⚠️ לא נמצא GROQ_API_KEY. אנא הוסף אותו ב-Settings → Secrets:\n"
        '`GROQ_API_KEY = "gsk_XXXXXXXXXXXX"`\n'
        "את המפתח יוצרים בחשבון החינמי Console.groq.com",
        icon="🚨"
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================
# אתחול state
# =========================
DEFAULT_DATA = {
    "destination": "",
    "trip_name": "",
    "days": 3,
    "travellers_type": "",
    "has_women": False,
    "weather": "",
    "trip_kinds": [],
    "luggage": [],
    "laundry": False,
    "special_activities": "",
    "notes": ""
}

if "step" not in st.session_state:
    st.session_state.step = 0
if "form_data" not in st.session_state:
    st.session_state.form_data = DEFAULT_DATA.copy()
if "packing_title" not in st.session_state:
    st.session_state.packing_title = ""
if "packing_items" not in st.session_state:
    st.session_state.packing_items = []
if "checked_items" not in st.session_state:
    st.session_state.checked_items = set()


def reset_all():
    st.session_state.step = 0
    st.session_state.form_data = DEFAULT_DATA.copy()
    st.session_state.packing_title = ""
    st.session_state.packing_items = []
    st.session_state.checked_items = set()


# =========================
# פונקציית יצירת רשימת ציוד מ-GROQ
# =========================
def generate_packing_plan( dict):
    system_prompt = (
        "אתה PackBot, מומחה אריזה יסודי.\n"
        "אתה מקבל נתוני נסיעה בפורמט JSON, ועל בסיסם אתה בונה רשימת ציוד יסודית ומלאה, "
        "כך שהמשתמש יוכל פשוט לסמן וי על מה שארז ולא לשכוח שום דבר חשוב.\n\n"
        "שים לב במיוחד לשדות הבאים:\n"
        "- destination: יעד הנסיעה.\n"
        "- days: מספר לילות מחוץ לבית.\n"
        "- travellers_type: למשל 'רק אני', 'זוג', 'זוג עם ילדים', 'משפחה / קבוצה'.\n"
        "- has_women: אם True – יש נשים/נערות ויש לכלול גם ציוד היגיינה נשי.\n"
        "- weather: חם מאוד / נעים / קריר / קר מאוד / שלג.\n"
        "- trip_kinds: סוגי נסיעה, למשל: עיר / שופינג, בטן-גב, טרק/שטח, נסיעת עבודה, אירוע מיוחד.\n"
        "- luggage: רשימת אמצעי נשיאה.\n"
        "- laundry: אם True – מתוכננת כביסה.\n"
        "- special_activities + notes: ציוד מיוחד.\n\n"
        "רשימה יסודית כוללת: ביגוד, היגיינה, בריאות, אלקטרוניקה, מסמכים, ציוד נסיעה, ציוד לפי סוג הנסיעה, לילדים לפי הצורך, וכל מה שהמשתמש ציין.\n\n"
        "החזר JSON חוקי בלבד, ללא הסברים:\n"
        "{\n  \"title\": \"כותרת הרשימה\",\n  \"items\": [\"פריט 1\", \"פריט 2\"]\n}\n"
    )
    user_prompt = f"הנה נתוני הנסיעה:\n{json.dumps(data, ensure_ascii=False, indent=2)}"

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    content = completion.choices[0].message.content.strip()

    try:
        plan = json.loads(content)
        title = plan.get("title", f"רשימת ציוד ל{data.get('destination','')}")
        items_raw = plan.get("items", [])
        items = [item.strip() for item in items_raw if isinstance(item, str) and item.strip()]
        if not items:
            raise ValueError
        return title, items
    except Exception:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        title = lines[0] if lines else "רשימת ציוד נסיעה"
        rest = lines[1:] if len(lines) > 1 else []
        return title, rest


# =========================
# ממשק משתמש – אשף שלבים
# =========================
data = st.session_state.form_data
step = st.session_state.step
TOTAL_STEPS = 6

st.progress(min(step, TOTAL_STEPS) / float(TOTAL_STEPS))

# ----- שלב 0: יעד וכותרת -----
if step == 0:
    st.markdown('<div class="step-title">1. מה היעד?</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">לאן הנסיעה ואיך תרצה לקרוא לרשימה שתופיע בפתקים?</div>', unsafe_allow_html=True)

    data["destination"] = st.text_input(
        "לאן הנסיעה?",
        value=data.get("destination", ""),
        placeholder="לונדון, אילת, ניו-יורק, טיול שנתי בצפון..."
    )
    data["trip_name"] = st.text_input(
        "כותרת לרשימה (אופציונלי)",
        value=data.get("trip_name", ""),
        placeholder="רשימת ציוד שהייה, טיול שקיעה, טיול שנתי..."
    )

    if st.button("המשך ➜", use_container_width=True, disabled=(data["destination"].strip() == "")):
        st.session_state.form_data = data
        st.session_state.step = 1
        st.experimental_rerun()

# ----- שלב 1: משך הנסיעה -----
elif step == 1:
    st.markdown('<div class="step-title">2. כמה זמן אתם מחוץ לבית?</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">משך הנסיעה משפיע על כמות הבגדים והציוד.</div>', unsafe_allow_html=True)

    data["days"] = st.number_input(
        "מספר לילות מחוץ לבית",
        min_value=1, max_value=90,
        value=int(data.get("days", 3))
    )

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 0
            st.experimental_rerun()
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.form_data = data
            st.session_state.step = 2
            st.experimental_rerun()

# ----- שלב 2: מי נוסע + האם יש נשים -----
elif step == 2:
    st.markdown('<div class="step-title">3. מי יוצא לדרך?</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">ככה נדע להתאים כמויות וציוד מיוחד.</div>', unsafe_allow_html=True)

    traveller_options = ["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"]
    current_idx = traveller_options.index(data.get("travellers_type", "")) if data.get("travellers_type") in traveller_options else 0

    data["travellers_type"] = st.radio(
        "בחר תיאור שמתאים לכם:",
        options=traveller_options,
        index=current_idx
    )

    has_women_option = st.radio(
        "האם יש נשים או נערות שצריך לכלול עבורן ציוד היגיינה נשי?",
        options=["לא", "כן"],
        index=1 if data.get("has_women", False) else 0,
    )
    data["has_women"] = (has_women_option == "כן")

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 1
            st.experimental_rerun()
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.form_data = data
            st.session_state.step = 3
            st.experimental_rerun()

# ----- שלב 3: מזג אוויר + סוגי נסיעה -----
elif step == 3:
    st.markdown('<div class="step-title">4. איך תיראה הנסיעה?</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">מזג האוויר ואופי הנסיעה משפיעים מאוד על הציוד.</div>', unsafe_allow_html=True)

    weather_options = ["חם מאוד", "נעים", "קריר", "קר מאוד / שלג"]
    w_idx = weather_options.index(data.get("weather", "")) if data.get("weather") in weather_options else 1

    data["weather"] = st.radio(
        "איך בערך יהיה מזג האוויר?",
        options=weather_options,
        index=w_idx
    )

    st.markdown("**איזה סוג נסיעה זו?** (אפשר לבחור יותר מאחד)")

    trip_kind_options = [
        "עיר / שופינג",
        "בטן-גב / ים / בריכה",
        "טרק / שטח / קמפינג",
        "נסיעת עבודה / כנס",
        "אירוע מיוחד (חתונה, הופעה, בר/בת מצווה)",
        "תנועת נוער / טיול שנתי"
    ]

    data["trip_kinds"] = st.multiselect(
        "בחר סוגי נסיעה רלוונטיים:",
        options=trip_kind_options,
        default=data.get("trip_kinds", []),
    )

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 2
            st.experimental_rerun()
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.form_data = data
            st.session_state.step = 4
            st.experimental_rerun()

# ----- שלב 4: מזוודות / תיקים -----
elif step == 4:
    st.markdown('<div class="step-title">5. במה אתה אורז?</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">אפשר לבחור כמה אפשרויות – טרולי + תיק גב וכו׳.</div>', unsafe_allow_html=True)

    luggage_options = [
        "טרולי (מזוודה קטנה)",
        "מזוודה בינונית",
        "מזוודה גדולה",
        "תיק גב",
        "תיק צד / תיק כתף",
        "תיק רחצה תלוי / מתקפל"
    ]

    selected_luggage = []
    for opt in luggage_options:
        key = f"luggage_{opt}"
        default_checked = (opt in data.get("luggage", []))
        checked = st.checkbox(opt, value=default_checked, key=key)
        if checked:
            selected_luggage.append(opt)

    data["luggage"] = selected_luggage

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 3
            st.experimental_rerun()
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.form_data = data
            st.session_state.step = 5
            st.experimental_rerun()

# ----- שלב 5: כביסה, אקטיביטיז והערות -----
elif step == 5:
    st.markdown('<div class="step-title">6. עוד כמה פרטים חשובים</div>', unsafe_allow_html=True)
    st.markdown("<div class='step-subtitle'>מכאן PackBot כבר יוכל להרכיב רשימת ציוד מלאה.</div>", unsafe_allow_html=True)

    data["laundry"] = st.checkbox("כנראה שתעשו כביסה במהלך הנסיעה", value=bool(data.get("laundry", False)))

    data["special_activities"] = st.text_input(
        "משהו מיוחד שצריך ציוד בשבילו? (אופציונלי)",
        value=data.get("special_activities", ""),
        placeholder="חתונה, מסיבה, טרק לילה, פעילות מים, ספורט, ציוד צילום..."
    )

    data["notes"] = st.text_area(
        "העדפות אישיות / דברים שחייבים לזכור (אופציונלי)",
        value=data.get("notes", ""),
        placeholder="לדוגמה: תרופות, אריזה קומפקטית, מקום למתנות..."
    )

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 4
            st.experimental_rerun()
    with col2:
        if st.button("צור רשימת ציוד ✅", use_container_width=True):
            with st.spinner("PackBot מרכיב עבורך רשימה יסודית..."):
                title, items = generate_packing_plan(data)
                st.session_state.packing_title = title or "רשימת ציוד נסיעה"
                st.session_state.packing_items = items
                st.session_state.checked_items = set()
                st.session_state.step = 6
                st.experimental_rerun()

# ----- שלב 6: רשימת ציוד סופית + סימון פריטים -----
else:
    st.markdown('<div class="step-title">רשימת הציוד שלך מוכנה ✔</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-subtitle">סמן וי על מה שכבר ארזת, או העתק ל"פתקים".</div>', unsafe_allow_html=True)

    title = st.session_state.packing_title
    items = st.session_state.packing_items

    if not items:
        st.warning("לא נמצאה רשימת ציוד. חזור אחורה ונסה שוב.")
    else:
        st.markdown(f"**{title}**")

        total = len(items)
        new_checked_set = set(st.session_state.checked_items)

        for idx, item in enumerate(items):
            key = f"item_{idx}"
            checked = item in st.session_state.checked_items
            new_val = st.checkbox(item, value=checked, key=key)
            if new_val:
                new_checked_set.add(item)
            else:
                new_checked_set.discard(item)

        st.session_state.checked_items = new_checked_set
        done_count = len(new_checked_set)

        st.progress(done_count / float(total))
        st.caption(f"סימנת {done_count} מתוך {total} פריטים.")

        # טקסט נקי להעתקה ל"פתקים"
        text_lines = [title, ""]
        text_lines.extend(items)
        notes_text = "\n".join(text_lines)

        st.markdown("**להעתקה ל״פתקים״:**")
        st.text_area("סמן הכל והעתק (Ctrl+C / לחיצה ארוכה):", value=notes_text, height=260)

        st.download_button(
            "📥 הורד כקובץ TXT", data=notes_text, file_name="packing_list.txt", mime="text/plain", use_container_width=True,
        )

    if st.button("🔁 התחל שאלון חדש", use_container_width=True):
        reset_all()
