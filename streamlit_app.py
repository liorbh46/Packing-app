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
        max-width: 520px;
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
        font-size: 1.7rem;
        margin-bottom: 0.1rem;
    }

    .sub-caption {
        text-align: center;
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.9rem;
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
        font-size: 1.05rem;
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
    '<div class="sub-caption">אשף חכם לבניית רשימת ציוד יסודית לכל סוג נסיעה</div>',
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
#   קריאה ל-Groq – יצירת רשימת ציוד יסודית
# =========================
def generate_packing_plan(data: dict):
    """
    משתמש ב-Groq (Llama 3.1) כדי לבנות כותרת ורשימת פריטים יסודית.
    מחזיר: (title: str, items: list[str])
    """

    system_prompt = (
        "אתה PackBot, מומחה אריזה יסודי.\n"
        "אתה מקבל נתוני נסיעה בפורמט JSON, ועל בסיסם אתה בונה רשימת ציוד יסודית ומלאה, "
        "כך שהמשתמש יוכל פשוט לסמן וי על מה שארז ולא לשכוח שום דבר חשוב.\n\n"
        "שים לב במיוחד לשדות הבאים:\n"
        "- destination: יעד הנסיעה.\n"
        "- days: מספר לילות מחוץ לבית.\n"
        "- travellers_type: למשל 'רק אני', 'זוג', 'זוג עם ילדים', 'משפחה / קבוצה'.\n"
        "- has_women: אם True – יש נשים/נערות ויש לכלול גם ציוד היגיינה נשי (תחבושות, טמפונים, כוס מחזור וכו').\n"
        "- weather: חם מאוד / נעים / קריר / קר מאוד / שלג.\n"
        "- trip_kinds: רשימה של סוגי נסיעה, למשל: עיר / שופינג, בטן-גב, טרק/שטח, נסיעת עבודה, אירוע מיוחד, תנועת נוער.\n"
        "- luggage: רשימה של אמצעי נשיאה (טרולי, מזוודה גדולה, תיק גב וכו').\n"
        "- laundry: אם True – מתוכננת כביסה.\n"
        "- special_activities + notes: כל דבר מיוחד שצריך ציוד ייעודי.\n\n"
        "בנה רשימה יסודית שכוללת:\n"
        "- ביגוד: כולל תחתונים, גרביים, פיג׳מות, מכנסיים, חולצות, שכבות חמות אם צריך, בגדי ים אם רלוונטי.\n"
        "- היגיינה וטואלטיקה: כולל מברשת ומשחת שיניים, דאודורנט, שמפו/סבון, קרם גוף/פנים, מסרק, "
        "גילוח, גזירת ציפורניים, כרטיסיות/קיסמים לשיניים, ערכת טיפוח בסיסית.\n"
        "- אם has_women = True: הוסף גם ציוד היגייני נשי רלוונטי.\n"
        "- בריאות: תרופות קבועות, משככי כאבים, פלסטרים, ערכת עזרה ראשונה בסיסית.\n"
        "- אלקטרוניקה: מטענים לכל המכשירים (טלפון, שעון, אוזניות), מתאם תקע (אם צריך), סוללה ניידת.\n"
        "- מסמכים וכסף: דרכון, תעודה מזהה, רישיון נהיגה אם רלוונטי, כרטיסי אשראי, כסף מזומן מקומי, ביטוח נסיעות.\n"
        "- ציוד לטיסה/נסיעה: כרית נסיעות, אוזניות, בקבוק מים רב-פעמי, נשנושים, מסכת עיניים אם מתאים.\n"
        "- ציוד לפי סוג הנסיעה: לבוש מרשים לאירוע, בגדים נוחים לטרק, ציוד קמפינג בסיסי, ביגוד חם מאוד וכו' – לפי trip_kinds.\n"
        "- אם יש ילדים/משפחה: ציוד בסיסי לילדים (אם עולה מהרמזים).\n"
        "- כל מה שמתחייב מהערות המשתמש.\n\n"
        "פורמט הפלט חייב להיות JSON חוקי **בלבד**, ללא טקסט נוסף:\n"
        "{\n"
        "  \"title\": \"כותרת הרשימה בעברית\",\n"
        "  \"items\": [\"פריט 1\", \"פריט 2\", \"פריט 3\", ...]\n"
        "}\n\n"
        "חשוב: החזר רק JSON תקין, ללא הסברים, ללא Markdown, ללא טקסט לפני או אחרי."
    )

    user_prompt = (
        "להלן נתוני הנסיעה בפורמט JSON. על בסיסם צור כותרת ורשימת ציוד יסודית בפורמט JSON כפי שהוגדר:\n\n"
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

    content = completion.choices[0].message.content.strip()

    # ניסיון לפרש כ-JSON
    try:
        plan = json.loads(content)
        title = plan.get("title") or f"רשימת ציוד נסיעה ל{data.get('destination','')}".strip()
        items_raw = plan.get("items", []) or []
        items = [i.strip() for i in items_raw if isinstance(i, str) and i.strip()]
        if not items:
            raise ValueError("No items in JSON.")
        return title, items
    except Exception:
        # נפילה – fallback: מפרש כטקסט פשוט שורה-שורה
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return "רשימת ציוד נסיעה", []
        title = lines[0]
        # מדלגים על שורה ריקה אחת אם יש
        rest = lines[1:]
        if rest and rest[0] == "":
            rest = rest[1:]
        return title, rest


# =========================
#   UI – אשף שלבים
# =========================
data = st.session_state.form_data
step = st.session_state.step

TOTAL_STEPS = 6
st.progress(min(step, TOTAL_STEPS) / float(TOTAL_STEPS))

# ----- שלב 0: יעד וכותרת -----
if step == 0:
    st.markdown('<div class="step-title">1. מה היעד?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">לאן הנסיעה ואיך תרצה לקרוא לרשימה שתופיע בפתקים?</div>',
        unsafe_allow_html=True
    )

    data["destination"] = st.text_input(
        "לאן הנסיעה?",
        value=data["destination"],
        placeholder="לונדון, אילת, ניו-יורק, טיול שנתי בצפון..."
    )

    data["trip_name"] = st.text_input(
        "כותרת לרשימה (אופציונלי)",
        value=data["trip_name"],
        placeholder="רשימת ציוד שהייה, רשימת ציוד לטיול שנתי..."
    )

    disabled_next = data["destination"].strip() == ""

    if st.button("המשך ➜", use_container_width=True, disabled=disabled_next):
        st.session_state.step = 1

# ----- שלב 1: משך הנסיעה -----
elif step == 1:
    st.markdown('<div class="step-title">2. כמה זמן אתם מחוץ לבית?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">המשך הנסיעה משפיע ישירות על כמות הבגדים והציוד.</div>',
        unsafe_allow_html=True
    )

    data["days"] = st.number_input(
        "מספר לילות מחוץ לבית",
        min_value=1,
        max_value=90,
        value=int(data["days"] or 3)
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 0
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 2

# ----- שלב 2: מי נוסע + האם יש נשים -----
elif step == 2:
    st.markdown('<div class="step-title">3. מי יוצא לדרך?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">ככה נדע להתאים כמויות וציוד מיוחד.</div>',
        unsafe_allow_html=True
    )

    traveller_options = ["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"]
    current_idx = traveller_options.index(data["travellers_type"]) if data["travellers_type"] in traveller_options else 0

    data["travellers_type"] = st.radio(
        "בחר תיאור שמתאים לכם:",
        options=traveller_options,
        index=current_idx
    )

    # שאלה על נשים/נערות לציוד היגיינה נשי
    has_women_option = st.radio(
        "האם יש נשים או נערות שצריך לכלול עבורן ציוד היגיינה נשי?",
        options=["לא", "כן"],
        index=1 if data["has_women"] else 0,
    )
    data["has_women"] = (has_women_option == "כן")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 1
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 3

# ----- שלב 3: מזג אוויר + סוגי נסיעה -----
elif step == 3:
    st.markdown('<div class="step-title">4. איך תיראה הנסיעה?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">מזג האוויר ואופי הנסיעה משפיעים מאוד על הציוד.</div>',
        unsafe_allow_html=True
    )

    weather_options = ["חם מאוד", "נעים", "קריר", "קר מאוד / שלג"]
    w_idx = weather_options.index(data["weather"]) if data["weather"] in weather_options else 1

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
        default=data["trip_kinds"] or []
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 2
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 4

# ----- שלב 4: מזוודות / תיקים (עם checkbox) -----
elif step == 4:
    st.markdown('<div class="step-title">5. במה אתה אורז?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">אפשר לבחור כמה אפשרויות – טרולי + תיק גב, מזוודה גדולה ועוד.</div>',
        unsafe_allow_html=True
    )

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
        default_checked = opt in data["luggage"]
        checked = st.checkbox(opt, value=default_checked, key=key)
        if checked:
            selected_luggage.append(opt)

    data["luggage"] = selected_luggage

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 3
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 5

# ----- שלב 5: כביסה, אקטיביטיז והערות -----
elif step == 5:
    st.markdown('<div class="step-title">6. עוד כמה פרטים חשובים</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">מכאן PackBot כבר יוכל להרכיב עבורך רשימת ציוד מלאה.</div>',
        unsafe_allow_html=True
    )

    data["laundry"] = st.checkbox(
        "כנראה שתעשו כביסה במהלך הנסיעה",
        value=bool(data["laundry"])
    )

    data["special_activities"] = st.text_input(
        "משהו מיוחד שצריך ציוד בשבילו? (אופציונלי)",
        value=data["special_activities"],
        placeholder="חתונה, מסיבה, טרק לילה, פעילות מים, ספורט, ציוד צילום..."
    )

    data["notes"] = st.text_area(
        "העדפות אישיות / דברים שחייבים לזכור (אופציונלי)",
        value=data["notes"],
        placeholder="לדוגמה: חייב לזכור תרופות מסוימות, רוצה לארוז כמה שפחות, צריך מקום למתנות..."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 4
    with col2:
        if st.button("צור רשימת ציוד ✅", use_container_width=True):
            with st.spinner("PackBot מרכיב עבורך רשימה יסודית..."):
                title, items = generate_packing_plan(data)
                st.session_state.packing_title = title or "רשימת ציוד נסיעה"
                st.session_state.packing_items = items
                st.session_state.checked_items = set()
                st.session_state.step = 6

# ----- שלב 6: רשימת ציוד סופית + checkbox לכל פריט -----
else:
    st.markdown('<div class="step-title">רשימת הציוד שלך מוכנה ✔</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">סמן וי על מה שכבר ארזת, או העתק ל"פתקים".</div>',
        unsafe_allow_html=True
    )

    title = st.session_state.packing_title
    items = st.session_state.packing_items

    if not items:
        st.warning("לא נמצאה רשימת ציוד. חזור אחורה ונסה שוב.")
    else:
        st.markdown(f"**{title}**")

        # צ'קבוקסים לכל פריט
        total = len(items)
        done_count = 0

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
        st.text_area(
            "סמן הכל והעתק (Ctrl+C / לחיצה ארוכה):",
            value=notes_text,
            height=260,
        )

        st.download_button(
            "📥 הורד כקובץ TXT",
            data=notes_text,
            file_name="packing_list.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("🔁 התחל שאלון חדש", use_container_width=True):
        reset_all()