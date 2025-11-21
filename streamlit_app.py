import streamlit as st
import pandas as pd

# =========================
#   הגדרות עמוד ועיצוב
# =========================
st.set_page_config(
    page_title="PackWise – רשימת אריזה חכמה",
    page_icon="🧳",
    layout="wide"
)

# CSS מותאם אישית
st.markdown("""
    <style>
    :root {
        --primary: #2563EB;
        --primary-soft: #EFF3FF;
        --bg: #F5F7FA;
        --card-bg: #FFFFFF;
        --accent: #10B981;
        --muted: #6B7280;
    }

    html, body, [class*="css"] {
        direction: rtl;
    }

    .main {
        background-color: var(--bg);
    }

    .packwise-hero {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .packwise-hero h1 {
        color: #0F172A;
        font-size: 2.4rem;
        margin-bottom: 0.3rem;
        font-weight: 800;
    }

    .packwise-hero p {
        color: var(--muted);
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }

    .packwise-tag {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        background-color: var(--primary-soft);
        color: #1D4ED8;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-bottom: 0.6rem;
    }

    .packwise-card {
        background-color: var(--card-bg);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .packwise-card h3 {
        margin-top: 0;
        margin-bottom: 0.4rem;
        font-size: 1rem;
        color: #111827;
    }

    .packwise-label {
        font-size: 0.85rem;
        color: #374151;
        margin-bottom: 0.15rem;
    }

    .packwise-summary-label {
        font-size: 0.85rem;
        color: #6B7280;
    }

    .packwise-summary-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #111827;
    }

    .packwise-progress-label {
        font-size: 0.85rem;
        color: #4B5563;
        margin-bottom: 0.1rem;
    }

    .packwise-footer {
        color: #9CA3AF;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 1.5rem;
    }

    /* טאבים */
    button[role="tab"] {
        font-size: 0.9rem !important;
    }

    /* כפתורי טקסט */
    .stDownloadButton > button, .stButton > button {
        border-radius: 999px;
        font-weight: 600;
    }

    </style>
""", unsafe_allow_html=True)

# =========================
#   פונקציית יצירת פריטים
# =========================
def get_items(days, weather, trip_type, adults, children, infants, is_intl, laundry):
    items = {
        "👖 ביגוד": [],
        "🪥 היגיינה": [],
        "🔌 אלקטרוניקה": [],
        "📂 מסמכים": [],
        "🧸 ילדים ותינוקות": [],
        "💊 בריאות ושונות": []
    }
    
    total_people = adults + children
    factor = min(days + 1, 7) if laundry else days + 1

    # ביגוד
    if total_people > 0:
        items["👖 ביגוד"].append(f"{factor * total_people} זוגות תחתונים וגרביים")
        items["👖 ביגוד"].append(f"{factor * total_people} חולצות (קצר/ארוך)")
    items["👖 ביגוד"].append(f"{max(int(days / 2) + 1, 2)} זוגות מכנסיים לאדם")
    items["👖 ביגוד"].append("פיג'מה לכל נוסע")
    
    if weather in ["קריר", "קפוא/שלג"]:
        items["👖 ביגוד"].extend(["מעילים חמים", "צעיפים וכפפות", "גופיות תרמיות"])
    elif weather == "לוהט":
        items["👖 ביגוד"].extend(["כובע רחב שוליים", "משקפי שמש"])

    if trip_type == "בטן-גב":
        items["👖 ביגוד"].extend(["בגדי ים", "כפכפים", "בגדי חוף נוחים"])
    elif trip_type == "עסקים":
        items["👖 ביגוד"].extend(["חליפה / לבוש רשמי", "נעליים אלגנטיות", "חגורה תואמת"])
    elif trip_type == "טרק/שטח":
        items["👖 ביגוד"].extend(["נעלי הליכה טובות", "גרביים מנדפות זיעה", "ביגוד יבש-מהר"])

    # היגיינה
    items["🪥 היגיינה"].extend([
        "מברשות ומשחת שיניים",
        "דאודורנט",
        "שמפו וסבון (בקבוקים קטנים)",
        "קרם פנים / גוף",
        "מסרק / מברשת שיער",
        "גילוח / מוצרי טיפוח אישיים"
    ])
    if trip_type == "בטן-גב" or weather == "לוהט":
        items["🪥 היגיינה"].append("קרם הגנה חזק (SPF 30 ומעלה)")

    # אלקטרוניקה
    items["🔌 אלקטרוניקה"].extend([
        "מטענים לטלפונים",
        "אוזניות",
        "מטען למחשב נייד (אם רלוונטי)"
    ])
    if is_intl:
        items["🔌 אלקטרוניקה"].append("מתאם חשמל אוניברסלי")
    items["🔌 אלקטרוניקה"].append("סוללה ניידת (Power Bank)")
    
    # מסמכים
    items["📂 מסמכים"].extend([
        "ארנק + כרטיסי אשראי",
        "תעודת זהות / רישיון נהיגה",
    ])
    if is_intl:
        items["📂 מסמכים"].extend([
            "דרכון בתוקף",
            "ביטוח נסיעות מודפס / דיגיטלי",
            "אישורי טיסה / כרטיס עלייה למטוס (בטלפון)",
            "הזמנת מלון / לינה",
        ])

    # ילדים ותינוקות
    if children > 0:
        items["🧸 ילדים ותינוקות"].extend([
            "משחקים / פעילויות לדרך",
            "נשנושים לילדים",
            "בגדים להחלפה בתיק היד",
        ])
    if infants > 0:
        items["🧸 ילדים ותינוקות"].extend([
            f"{days * 6} חיתולים (לפחות)",
            "מגבונים לחים (חבילה גדולה)",
            "משחה לתפרחת חיתולים",
            "בקבוקים + תמ\"ל (לפי הצורך)",
            "מוצצים (כולל ספייר)",
            "עגלה / מנשא",
            "שמיכה קלה לתינוק",
            "שקיות לחיתולים מלוכלכים"
        ])

    # בריאות ושונות
    items["💊 בריאות ושונות"].extend([
        "תיק עזרה ראשונה בסיסי",
        "משככי כאבים / תרופות קבועות",
        "מד חום (בעיקר עם ילדים)",
        "שקית לכביסה מלוכלכת",
        "בקבוק מים רב-פעמי לכל נוסע"
    ])
    if trip_type == "טרק/שטח":
        items["💊 בריאות ושונות"].extend([
            "תחבושות / פלסטרים",
            "ספריי נגד יתושים",
            "פנס קטן / פנס ראש"
        ])

    # החזרת קטגוריות לא ריקות בלבד
    return {k: v for k, v in items.items() if v}

# =========================
#   כותרת / Hero
# =========================
st.markdown("""
<div class="packwise-hero">
    <div class="packwise-tag">גרסת בטא • PackWise</div>
    <h1>PackWise – רשימת אריזה חכמה אישית</h1>
    <p>ענו על כמה שאלות קצרות – וקבלו רשימת אריזה מותאמת ליעד, למזג האוויר ולסגנון הטיול שלכם.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
#   תפריט צד – הגדרות
# =========================
with st.sidebar:
    st.markdown("### ⚙️ הגדרות נסיעה")
    st.caption("מלאו את פרטי הנסיעה כדי לבנות רשימה מותאמת אישית.")

    destination = st.text_input("לאן נוסעים?", value="לונדון")
    days = st.number_input("כמה ימים?", min_value=1, max_value=60, value=5)

    st.markdown("#### 👥 מי נוסע?")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        adults = st.number_input("מבוגרים", min_value=1, max_value=10, value=2)
    with col_a2:
        children = st.number_input("ילדים (2–12)", min_value=0, max_value=10, value=0)
    infants = st.number_input("תינוקות (0–2)", min_value=0, max_value=5, value=0)

    st.markdown("#### 🌤 סוג הטיול")
    weather = st.select_slider("מזג אוויר צפוי", options=["לוהט", "נעים", "קריר", "קפוא/שלג"], value="נעים")
    trip_type = st.selectbox("סוג החופשה", ["עירוני/שופינג", "בטן-גב", "עסקים", "טרק/שטח"])

    st.markdown("#### ✈️ פרטי טיסה")
    is_intl = st.toggle("טיסה לחו\"ל", value=True)
    laundry = st.toggle("מתכננים כביסה במהלך הנסיעה?", value=False)

    st.markdown("---")
    suitcase_type = st.selectbox(
        "סוג מזוודה / תיק",
        ["טרולי קטן (יד)", "מזוודה בינונית", "מזוודה גדולה", "תיק גב בלבד"]
    )

# =========================
#   לוגיקה: יצירת רשימת פריטים
# =========================
final_list = get_items(
    days=days,
    weather=weather,
    trip_type=trip_type,
    adults=adults,
    children=children,
    infants=infants,
    is_intl=is_intl,
    laundry=laundry
)

# יצירת מפת מפתחות לכל פריט
item_keys = {
    category: [f"{category}_{i}" for i in range(len(items))]
    for category, items in final_list.items()
}

# כפתור איפוס סימונים – אחרי שיש רשימה
reset_requested = False

with st.sidebar:
    reset_requested = st.button("🔄 התחל רשימה חדשה")

if reset_requested:
    # איפוס כל הצ'קבוקסים
    for cat, keys in item_keys.items():
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
    st.rerun()

# =========================
#   חישוב התקדמות
# =========================
all_items_count = sum(len(v) for v in final_list.values())
checked_count = 0
for category, items in final_list.items():
    for idx, _ in enumerate(items):
        key = f"{category}_{idx}"
        if st.session_state.get(key, False):
            checked_count += 1

progress = checked_count / all_items_count if all_items_count > 0 else 0

# =========================
#   תצוגת מידע כללי + התקדמות
# =========================
top_col1, top_col2, top_col3 = st.columns([2.2, 2.2, 1.6])

with top_col1:
    st.markdown('<div class="packwise-card">', unsafe_allow_html=True)
    st.markdown("#### 📍 כרטיס נסיעה")
    st.markdown(f"""
    <div class="packwise-summary-label">יעד</div>
    <div class="packwise-summary-value">{destination}</div>
    <div class="packwise-summary-label">משך הנסיעה</div>
    <div class="packwise-summary-value">{days} ימים</div>
    <div class="packwise-summary-label">סוג טיול</div>
    <div class="packwise-summary-value">{trip_type}</div>
    <div class="packwise-summary-label">סוג מזוודה</div>
    <div class="packwise-summary-value">{suitcase_type}</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with top_col2:
    st.markdown('<div class="packwise-card">', unsafe_allow_html=True)
    st.markdown("#### 👨‍👩‍👧‍👦 נוסעים")
    st.markdown(f"""
    <div class="packwise-summary-label">מבוגרים</div>
    <div class="packwise-summary-value">{adults}</div>
    <div class="packwise-summary-label">ילדים (2–12)</div>
    <div class="packwise-summary-value">{children}</div>
    <div class="packwise-summary-label">תינוקות (0–2)</div>
    <div class="packwise-summary-value">{infants}</div>
    <div class="packwise-summary-label">טיסה לחו"ל?</div>
    <div class="packwise-summary-value">{'כן' if is_intl else 'לא'}</div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with top_col3:
    st.markdown('<div class="packwise-card">', unsafe_allow_html=True)
    st.markdown("#### ✅ התקדמות אריזה")
    st.markdown(
        f'<div class="packwise-progress-label">סימנת {checked_count} מתוך {all_items_count} פריטים</div>',
        unsafe_allow_html=True
    )
    st.progress(progress, text=f"{int(progress * 100)}% הושלמו")
    if progress == 1.0 and all_items_count > 0:
        st.success("סיימת לארוז! נשאר רק לסגור את הריצ'רץ' 🧳")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================
#   רשימת הפריטים – טאבים
# =========================
st.markdown("### 📋 רשימת האריזה שלך")

tabs = st.tabs(list(final_list.keys()))

for i, (category, items) in enumerate(final_list.items()):
    with tabs[i]:
        st.subheader(category)
        st.caption("סמן/י כל פריט לאחר שהכנסת אותו למזוודה.")

        for idx, item in enumerate(items):
            key = item_keys[category][idx]
            # צ'קבוקס – המצב נשמר אוטומטית ב-session_state
            st.checkbox(item, key=key)

# =========================
#   יצוא רשימה
# =========================
st.markdown("---")
st.markdown("#### 📥 יצוא הרשימה")

text_output = f"רשימת אריזה ל{destination} ({days} ימים):\n\n"
for cat, items in final_list.items():
    text_output += f"{cat}:\n"
    for idx, item in enumerate(items):
        key = item_keys[cat][idx]
        mark = "V" if st.session_state.get(key, False) else "O"
        text_output += f"[{mark}] {item}\n"
    text_output += "\n"

st.download_button(
    "📄 הורדת הרשימה כטקסט",
    text_output,
    file_name="packing_list.txt",
    mime="text/plain"
)

st.markdown(
    '<div class="packwise-footer">PackWise – מוודאים שלא תשכחו כלום, חוץ מהדאגות ✈️</div>',
    unsafe_allow_html=True
)
