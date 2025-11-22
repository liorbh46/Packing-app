import os
import json
import streamlit as st
from groq import Groq

# =========================
#   הגדרות עמוד
# =========================
st.set_page_config(
    page_title="PackBot ✈️ חו\"ל",
    page_icon="✈️",
    layout="centered"
)

# =========================
#   עיצוב – יוקרתי, נקי, מותאם מובייל
# =========================
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: radial-gradient(circle at top, #e0f2ff 0, #f5f7fb 40%, #ffffff 100%);
    }

    [data-testid="stAppViewContainer"] > .main {
        max-width: 560px;
        margin: 0 auto;
        padding: 0.75rem 0.75rem 2.75rem 0.75rem;
    }

    h1 {
        text-align: center;
        font-size: 1.9rem;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        text-align: center;
        font-size: 0.95rem;
        color: #4b5563;
        margin-bottom: 1.1rem;
    }

    .card {
        background: #ffffffcc;
        backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 1.1rem 1rem 1.2rem 1rem;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .step-title {
        font-weight: 650;
        margin-bottom: 0.25rem;
        font-size: 1.05rem;
        color: #111827;
    }

    .step-subtitle {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.85rem;
    }

    .pill-progress {
        display: flex;
        gap: 0.25rem;
        margin-bottom: 0.6rem;
        justify-content: center;
    }
    .pill {
        flex: 1;
        height: 6px;
        border-radius: 999px;
        background: #e5e7eb;
    }
    .pill.active {
        background: linear-gradient(to right, #2563eb, #06b6d4);
    }

    .pill-label {
        text-align: center;
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 0.2rem;
    }

    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>PackBot ✈️ חו\"ל</h1>", unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">אשף חכם לבניית רשימת ציוד יסודית לטיסות לחו״ל – מותאם אישית עבורך</div>',
    unsafe_allow_html=True
)

# =========================
#   מפתח Groq (מ-Secrets)
# =========================
api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    st.error(
        "לא נמצא GROQ_API_KEY.\n\n"
        "ב-Streamlit Cloud: היכנס ל-Settings → Secrets והוסף שורה:\n"
        'GROQ_API_KEY = "gsk_XXXXXXXXXXXX"'
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================
#   אתחול state
# =========================
DEFAULT_DATA = {
    "destination_city": "",
    "destination_country": "",
    "trip_name": "",
    "days": 5,
    "travellers_type": "",
    "has_women": False,
    "weather": "",
    "trip_kinds": [],
    "flight_length": "",
    "baggage_type": "",
    "accommodation_type": "",
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
#   Groq – בניית רשימת ציוד יסודית לחו״ל
# =========================
def generate_packing_plan(data: dict):
    """
    משתמש ב-Groq (Llama 3.1) כדי לבנות כותרת ורשימת פריטים יסודית לטיסה לחו״ל.
    מחזיר: (title: str, items: list[str])
    """

    system_prompt = (
        "אתה PackBot, מומחה אריזה לטיסות לחו\"ל.\n"
        "אתה מקבל נתוני נסיעה בפורמט JSON, ועל בסיסם אתה בונה רשימת ציוד יסודית, "
        "שתאפשר לנוסע לסמן וי על כל פריט בלי לשכוח שום דבר חשוב.\n\n"
        "הנסיעה היא *תמיד לחו\"ל* (לא נסיעה בארץ).\n\n"
        "שים לב במיוחד לשדות הבאים:\n"
        "- destination_city, destination_country: יעד הנסיעה.\n"
        "- days: מספר לילות מחוץ לבית.\n"
        "- travellers_type: 'רק אני', 'זוג', 'זוג עם ילדים', 'משפחה / קבוצה'.\n"
        "- has_women: אם True – יש נשים/נערות ויש לכלול גם ציוד היגיינה נשי (תחבושות, טמפונים, כוס מחזור, וכדומה).\n"
        "- weather: חם מאוד / נעים / קריר / קר מאוד / שלג.\n"
        "- trip_kinds: סוגי נסיעה, למשל: עיר / שופינג, בטן-גב, טרק/שטח, נסיעת עבודה, אירוע מיוחד, ביקור משפחה.\n"
        "- flight_length: טיסה קצרה / בינונית / ארוכה.\n"
        "- baggage_type: כבודת יד בלבד, מזוודה בלבד, או שניהם.\n"
        "- accommodation_type: מלון, דירה/Airbnb, משפחה/חברים, הוסטל.\n"
        "- luggage: אמצעי נשיאה – טרולי, מזוודה גדולה, תיק גב, תיק רחצה וכו'.\n"
        "- laundry: האם מתוכננת כביסה.\n"
        "- special_activities + notes: אירועים מיוחדים, ציוד ייעודי, הדגשים ספציפיים.\n\n"
        "בנה רשימה יסודית שכוללת:\n"
        "1. מסמכים ונסיעה:\n"
        "   דרכון, צילום/סריקה של דרכון, ויזה (אם רלוונטי), כרטיסי טיסה/Boarding Pass, אישורי מלון/לינה, ביטוח נסיעות, רישיון נהיגה בינלאומי (אם צריך), פרטי טיסות וחברת תעופה, כתובת וטלפון של מקום הלינה.\n"
        "2. כסף ואמצעי תשלום:\n"
        "   כרטיסי אשראי בינלאומיים, כסף מזומן במטבע היעד, מעט כסף חירום, ארנק, חגורת כסף (אם מתאים).\n"
        "3. אלקטרוניקה:\n"
        "   טלפון, מטען טלפון, מטען USB-C/Micro/Lightning לפי הצורך, מטען לשעון חכם, מטען לאוזניות, סוללה ניידת, מתאם תקע בינלאומי מתאים ליעד, מפצל/כבל מאריך קטן, אוזניות לטיסה, לפטופ (אם צריך), מטען ללפטופ, כבל נתונים, eSIM / כרטיס SIM מקומי (אם רלוונטי).\n"
        "4. ביגוד:\n"
        "   תחתונים וגרביים (מספיק לכל הימים + עוד יום-יומיים), חולצות יומיומיות, מכנסיים, פיג'מה, ביגוד שכבות, סוודר/קפוצ'ון/ז'קט, מעיל חם אם קר, מעיל גשם/חוף אם צריך, בגדי ים וכפכפים אם יש ים/בריכה, נעליים נוחות להליכה, נעליים אלגנטיות אם יש אירוע או עבודה.\n"
        "   התאם את סוג הביגוד למזג האוויר ולסוג הנסיעה.\n"
        "5. היגיינה וטואלטיקה:\n"
        "   מברשת ומשחת שיניים, חוט דנטלי/קיסמים לשיניים, דאודורנט, שמפו, סבון גוף/פנים, קרם פנים וקרם גוף, מסרק/מברשת, ג'ל/חומר לשיער אם צריך, צמר גפן/מגבונים, ערכת ציפורניים (קוצץ, פצירה), סכין/מכונת גילוח, קרם גילוח/אפטר שייב.\n"
        "   אם has_women = True: כלול גם תחבושות היגייניות, טמפונים, כוס מחזור (לפי הצורך), מגבונים אינטימיים.\n"
        "6. בריאות:\n"
        "   תרופות קבועות, תרופות חירום (משככי כאבים, כדורים לכאבי בטן/שלשולים, כדורים נגד אלרגיה), פלסטרים, מדבקות גב/שרירים אם צריך, ערכת עזרה ראשונה קטנה.\n"
        "7. לטיסה עצמה (במיוחד אם flight_length ארוכה/בינונית):\n"
        "   כרית צוואר, מסכת עיניים, אטמי אוזניים, גרביים נוחות, ג'קט/חולצה ארוכה למזגן במטוס, בקבוק מים רב-פעמי ריק (למילוי אחרי הבידוק), חטיפים.\n"
        "8. לפי סוג הנסיעה:\n"
        "   - עיר / שופינג: תיק צד/תיק יום, נעליים נוחות להליכה, שקית רב-פעמית לקניות.\n"
        "   - בטן-גב: בגדי ים נוספים, בגד חוף, קרם הגנה חזק, כובע, משקפי שמש, תיק ים, שקית אטומה למים לטלפון.\n"
        "   - טרק / שטח / קמפינג: נעלי הליכה טובות, ביגוד מנדף זיעה, כובע, פנס, בקבוקי מים, אולי ערכת קמפינג בסיסית.\n"
        "   - נסיעת עבודה / כנס: לבוש רשמי/עסקי, נעליים אלגנטיות, מחשב נייד ומטען, מסמכים, כרטיסי ביקור.\n"
        "   - אירוע מיוחד: בגדים אלגנטיים לאירוע, נעליים מתאימות, אביזרים (עניבה, תכשיטים וכו').\n"
        "   - תנועת נוער / טיול שנתי: בגדים נוחים, ביגוד ספורט, בקבוק מים, כובע, מעיל גשם, תיק יום.\n"
        "9. לינה:\n"
        "   ציוד שינה בסיסי אם צריך (אטמי אוזניים, מסכת עיניים, אולי כיסוי כרית קטן אם רגישים), נעילת מזוודות.\n"
        "10. ארגון ונוחות:\n"
        "   שקיות כביסה לבגדים מלוכלכים, שקיות אטומות, איירטאג/מעקב למזוודה (אם מתאים), עט, מחברת קטנה, קלסר מסמכים קטן.\n\n"
        "קח בחשבון את כל הנתונים (למשל אם יש רק כבודת יד – לא להעמיס ציוד עודף, אבל עדיין רשימה יסודית), "
        "והתאם את כמות הפריטים באופן חכם ולא מוגזם.\n\n"
        "פורמט הפלט חייב להיות JSON חוקי בלבד, ללא טקסט נוסף:\n"
        "{\n"
        "  \"title\": \"כותרת הרשימה בעברית\",\n"
        "  \"items\": [\"פריט 1\", \"פריט 2\", \"פריט 3\", ...]\n"
        "}\n\n"
        "החזר רק JSON תקין, ללא הסברים, ללא Markdown, ללא טקסט לפני או אחרי."
    )

    user_prompt = (
        "להלן נתוני נסיעה לטיסה לחו\"ל, בפורמט JSON. "
        "על בסיסם צור כותרת ורשימת ציוד יסודית בפורמט JSON כפי שהוגדר:\n\n"
        + json.dumps(data, ensure_ascii=False, indent=2)
    )

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
    )

    content = completion.choices[0].message.content.strip()

    try:
        plan = json.loads(content)
        title = plan.get("title") or "רשימת ציוד לטיסה לחו\"ל"
        items_raw = plan.get("items", []) or []
        items = [i.strip() for i in items_raw if isinstance(i, str) and i.strip()]
        if not items:
            raise ValueError("No items.")
        return title, items
    except Exception:
        # fallback – ליתר ביטחון
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        if not lines:
            return "רשימת ציוד לטיסה לחו\"ל", []
        title = lines[0]
        rest = lines[1:]
        return title, rest


# =========================
#   UI – אשף שלבים
# =========================
data = st.session_state.form_data
step = st.session_state.step
TOTAL_STEPS = 6

# Steppers ויזואלי
step_labels = [
    "יעד ובסיס",
    "משך הנסיעה",
    "מי נוסע",
    "אופי הטיסה",
    "מזג אוויר וסגנון",
    "פרטים אחרונים"
]

st.markdown(f'<div class="pill-label">שלב {min(step+1, TOTAL_STEPS)} מתוך {TOTAL_STEPS} – {step_labels[min(step, TOTAL_STEPS-1)]}</div>', unsafe_allow_html=True)
st.markdown('<div class="pill-progress">', unsafe_allow_html=True)
for i in range(TOTAL_STEPS):
    active = "active" if i <= step else ""
    st.markdown(f'<div class="pill {active}"></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

# ----- שלב 0: יעד וכותרת -----
if step == 0:
    st.markdown('<div class="step-title">1. לאן טסים?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">נגדיר את היעד כדי להתאים את הרשימה למדינה ולעיר הספציפית.</div>',
        unsafe_allow_html=True
    )

    data["destination_city"] = st.text_input(
        "עיר היעד העיקרית:",
        value=data["destination_city"],
        placeholder="לונדון, פריז, ניו-יורק..."
    )

    data["destination_country"] = st.text_input(
        "מדינה:",
        value=data["destination_country"],
        placeholder="בריטניה, צרפת, ארה\"ב..."
    )

    data["trip_name"] = st.text_input(
        "שם לרשימה (אופציונלי)",
        value=data["trip_name"],
        placeholder="רשימת ציוד לטיסה ללונדון..."
    )

    disabled_next = not data["destination_city"].strip() or not data["destination_country"].strip()

    if st.button("המשך ➜", use_container_width=True, disabled=disabled_next):
        st.session_state.step = 1

# ----- שלב 1: משך הנסיעה -----
elif step == 1:
    st.markdown('<div class="step-title">2. כמה זמן תהיו בחו״ל?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">המשך השהייה קובע את כמות הבגדים והציוד.</div>',
        unsafe_allow_html=True
    )

    data["days"] = st.number_input(
        "מספר לילות מחוץ לבית:",
        min_value=1,
        max_value=90,
        value=int(data["days"] or 5)
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
        '<div class="step-subtitle">נשתמש בזה כדי להתאים כמויות, ילדים, וציוד היגיינה נשי אם רלוונטי.</div>',
        unsafe_allow_html=True
    )

    traveller_options = ["רק אני", "זוג", "זוג עם ילדים", "משפחה / קבוצה"]
    t_idx = traveller_options.index(data["travellers_type"]) if data["travellers_type"] in traveller_options else 0

    data["travellers_type"] = st.radio(
        "בחר את התיאור הכי מתאים:",
        options=traveller_options,
        index=t_idx
    )

    has_women_option = st.radio(
        "האם יש נשים / נערות שצריך לכלול עבורן ציוד היגיינה נשי?",
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

# ----- שלב 3: אופי הטיסה והלינה -----
elif step == 3:
    st.markdown('<div class="step-title">4. אופי הטיסה והלינה</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">כך אפשר לדייק ציוד לטיסה עצמה ולסוג השהייה.</div>',
        unsafe_allow_html=True
    )

    flight_len_opts = ["טיסה קצרה (עד ~4 שעות)", "טיסה בינונית (4–8 שעות)", "טיסה ארוכה (8+ שעות)"]
    f_idx = flight_len_opts.index(data["flight_length"]) if data["flight_length"] in flight_len_opts else 1

    data["flight_length"] = st.radio(
        "מה אורך הטיסה בערך?",
        options=flight_len_opts,
        index=f_idx
    )

    baggage_opts = ["כבודת יד בלבד (טרולי/תיק עלייה למטוס)", "מזוודה בבטן המטוס בלבד", "גם כבודת יד וגם מזוודה"]
    b_idx = baggage_opts.index(data["baggage_type"]) if data["baggage_type"] in baggage_opts else 2

    data["baggage_type"] = st.radio(
        "איך אתם טסים מבחינת מזוודות?",
        options=baggage_opts,
        index=b_idx
    )

    acc_opts = ["מלון", "דירה / Airbnb", "הורים / משפחה / חברים", "הוסטל / אכסניה"]
    a_idx = acc_opts.index(data["accommodation_type"]) if data["accommodation_type"] in acc_opts else 0

    data["accommodation_type"] = st.radio(
        "איפה ישנים ברוב הזמן?",
        options=acc_opts,
        index=a_idx
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 2
    with col2:
        if st.button("המשך ➜", use_container_width=True):
            st.session_state.step = 4

# ----- שלב 4: מזג אוויר + סוג נסיעה -----
elif step == 4:
    st.markdown('<div class="step-title">5. איך ייראה היום-יום בחו״ל?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">מזג האוויר וסגנון החופשה משפיעים מאוד על מה מכניסים למזוודה.</div>',
        unsafe_allow_html=True
    )

    weather_options = ["חם מאוד", "נעים", "קריר", "קר מאוד / שלג"]
    w_idx = weather_options.index(data["weather"]) if data["weather"] in weather_options else 1

    data["weather"] = st.radio(
        "איך בערך יהיה מזג האוויר שם?",
        options=weather_options,
        index=w_idx
    )

    st.markdown("**איזה סגנון נסיעה זה?** (אפשר לבחור יותר מאחד)")

    trip_kind_options = [
        "עיר / שופינג",
        "בטן-גב / ים / בריכה",
        "טרק / שטח / קמפינג",
        "נסיעת עבודה / כנס",
        "אירוע מיוחד (חתונה, הופעה, בר/בת מצווה)",
        "ביקור משפחה / חברים",
        "תנועת נוער / טיול שנתי"
    ]

    data["trip_kinds"] = st.multiselect(
        "בחר את מה שמתאר הכי טוב את הנסיעה:",
        options=trip_kind_options,
        default=data["trip_kinds"] or []
    )

    st.markdown("**במה אתה משתמש בפועל לסחיבת הציוד?**")
    luggage_options = [
        "טרולי (מזוודה קטנה)",
        "מזוודה בינונית",
        "מזוודה גדולה",
        "תיק גב יומי",
        "תיק צד / תיק כתף",
        "תיק רחצה"
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

# ----- שלב 5: כביסה, אקטיביטיז, הערות -----
elif step == 5:
    st.markdown('<div class="step-title">6. פרטים אחרונים</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">עוד קצת הקשר – ומשם PackBot כבר מרכיב עבורך רשימה מלאה.</div>',
        unsafe_allow_html=True
    )

    data["laundry"] = st.checkbox(
        "כנראה שתעשו כביסה במהלך הטיול (מכבסה / מכונה בדירה)",
        value=bool(data["laundry"])
    )

    data["special_activities"] = st.text_input(
        "יש פעילות מיוחדת שצריך ציוד בשבילה? (אופציונלי)",
        value=data["special_activities"],
        placeholder="חתונה, מסיבה, טרק לילה, פעילות מים, ספורט, ציוד צילום..."
    )

    data["notes"] = st.text_area(
        "העדפות אישיות / דברים שחייבים לזכור (אופציונלי)",
        value=data["notes"],
        placeholder="תרופות מסוימות, מינימום ציוד, מקום למתנות, ציוד עבודה מיוחד..."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ חזור", use_container_width=True):
            st.session_state.step = 4
    with col2:
        if st.button("צור רשימת ציוד לטיסה ✈️✅", use_container_width=True):
            with st.spinner("PackBot מכין עבורך רשימת ציוד יסודית לחו\"ל..."):
                title, items = generate_packing_plan(data)
                st.session_state.packing_title = title or "רשימת ציוד לטיסה לחו\"ל"
                st.session_state.packing_items = items
                st.session_state.checked_items = set()
                st.session_state.step = 6

# ----- שלב 6: רשימת ציוד סופית -----
else:
    st.markdown('<div class="step-title">רשימת הציוד שלך לחו״ל מוכנה ✔</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-subtitle">סמן וי על מה שכבר ארזת, או העתק ל״פתקים״ / שלח לעצמך בוואטסאפ.</div>',
        unsafe_allow_html=True
    )

    title = st.session_state.packing_title
    items = st.session_state.packing_items

    if not items:
        st.warning("לא נמצאה רשימת ציוד. חזור אחורה ונסה שוב.")
    else:
        st.markdown(f"**{title}**")
        st.write("")

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
        total = len(items)

        st.progress(done_count / float(total))
        st.caption(f"סימנת {done_count} מתוך {total} פריטים.")

        # טקסט נקי להעתקה ל"פתקים"
        text_lines = [title, ""]
        text_lines.extend(items)
        notes_text = "\n".join(text_lines)

        st.markdown("**להעתקה ל״פתקים״ / לשליחה לעצמך:**")
        st.text_area(
            "סמן הכל והעתק:",
            value=notes_text,
            height=260,
        )

        st.download_button(
            "📥 הורד כקובץ TXT",
            data=notes_text,
            file_name="packing_list_abroad.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("🔁 התחל שאלון חדש", use_container_width=True):
        reset_all()

st.markdown('</div>', unsafe_allow_html=True)