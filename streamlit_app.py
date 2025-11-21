import streamlit as st
import pandas as pd
import time

# --- הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="PackSmart Pro", page_icon="✈️", layout="wide")

# CSS מותאם אישית לשיפור הנראות
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- אתחול Session State (כדי לזכור מה סומן) ---
if 'checked_items' not in st.session_state:
    st.session_state.checked_items = set()

def toggle_item(item):
    if item in st.session_state.checked_items:
        st.session_state.checked_items.remove(item)
    else:
        st.session_state.checked_items.add(item)

# --- כותרת ---
st.title("✈️ PackSmart Pro")
st.markdown("<h4 style='text-align: center; color: #7f8c8d;'>האריזה שלך מעולם לא הייתה קלה יותר</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- סרגל צד (הגדרות) ---
with st.sidebar:
    st.header("⚙️ הגדרות נסיעה")
    
    destination = st.text_input("לאן טסים?", "לונדון")
    days = st.number_input("מספר ימים", min_value=2, value=5)
    
    st.subheader("👥 מי נוסע?")
    adults = st.number_input("מבוגרים", 1, 5, 2)
    children = st.number_input("ילדים (2-12)", 0, 5, 0)
    infants = st.number_input("תינוקות (0-2)", 0, 2, 0)
    
    st.subheader("⛅ תנאים")
    weather = st.select_slider("מזג אוויר צפוי", options=["לוהט", "נעים", "קריר", "קפוא/שלג"])
    trip_type = st.selectbox("סוג הטיול", ["עירוני/שופינג", "בטן-גב", "עסקים", "טרק/שטח"])
    
    is_intl = st.toggle("טיסה לחו\"ל?", value=True)
    laundry = st.toggle("מתכננים כביסה?", value=False)

    if st.button("🔄 רענן רשימה", use_container_width=True):
        st.session_state.checked_items = set() # איפוס סימונים
        st.rerun()

# --- לוגיקה חכמה (Backend) ---
def get_items(days, weather, trip_type, adults, children, infants, is_intl, laundry):
    items = {
        "👖 ביגוד": [],
        "🪥 היגיינה": [],
        "🔌 גאדג'טים": [],
        "📂 מסמכים": [],
        "🧸 ילדים ותינוקות": [],
        "💊 בריאות ושונות": []
    }
    
    # חישוב כמויות
    factor = min(days + 1, 7) if laundry else days + 1
    total_people = adults + children
    
    # ביגוד
    items["👖 ביגוד"].append(f"{factor * total_people} תחתונים וגרביים")
    items["👖 ביגוד"].append(f"{factor * total_people} חולצות (קצר/ארוך)")
    items["👖 ביגוד"].append(f"{int(days/2)+1} זוגות מכנסיים לאדם")
    items["👖 ביגוד"].append("פיג'מות לכולם")
    
    if weather in ["קריר", "קפוא/שלג"]:
        items["👖 ביגוד"].extend(["מעילים", "צעיפים וכפפות", "גופיות תרמיות"])
    elif weather == "לוהט":
        items["👖 ביגוד"].extend(["כובעים", "משקפי שמש"])
        
    if trip_type == "בטן-גב":
        items["👖 ביגוד"].extend(["בגדי ים", "כפכפים", "בגדי חוף"])
    elif trip_type == "עסקים":
        items["👖 ביגוד"].extend(["חליפה/לבוש רשמי", "נעליים אלגנטיות"])

    # היגיינה
    items["🪥 היגיינה"].extend(["מברשות ומשחת שיניים", "דאודורנט", "שמפו וסבון", "קרם פנים/גוף", "מסרק/מברשת שיער"])
    if trip_type == "בטן-גב" or weather == "לוהט":
        items["🪥 היגיינה"].append("קרם הגנה חזק")

    # אלקטרוניקה
    items["🔌 גאדג'טים"].extend(["מטענים לטלפונים", "אוזניות"])
    if is_intl:
        items["🔌 גאדג'טים"].append("מתאם חשמל אוניברסלי")
        items["🔌 גאדג'טים"].append("סוללה ניידת (Power Bank)")
    
    # ילדים ותינוקות
    if children > 0:
        items["🧸 ילדים ותינוקות"].extend(["משחקים לטיסה/נסיעה", "נשנושים לדרך", "בגדים להחלפה בתיק גב"])
    if infants > 0:
        items["🧸 ילדים ותינוקות"].extend([
            f"{days * 6} חיתולים", "מגבונים לחים (חבילה גדולה)", "משחה לתפרחת", 
            "בקבוקים + תמ\"ל", "מוצצים (כולל ספייר)", "עגלה/מנשא", "שקיות לחיתולים מלוכלכים"
        ])

    # מסמכים
    items["📂 מסמכים"].extend(["ארנק + כרטיסי אשראי", "תעודות זהות"])
    if is_intl:
        items["📂 מסמכים"].extend(["דרכונים בתוקף", "ביטוח נסיעות", "כרטיסי טיסה (בטלפון)"])

    # שונות
    items["💊 בריאות ושונות"].extend(["תיק עזרה ראשונה בסיסי", "משככי כאבים", "שקיות לכביסה מלוכלכת"])
    
    # ניקוי קטגוריות ריקות
    return {k: v for k, v in items.items() if v}

# יצירת הרשימה
final_list = get_items(days, weather, trip_type, adults, children, infants, is_intl, laundry)

# חישוב התקדמות
all_items_count = sum(len(v) for v in final_list.values())
checked_count = len(st.session_state.checked_items)
progress = checked_count / all_items_count if all_items_count > 0 else 0

# --- תצוגת ההתקדמות ---
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress, text=f"התקדמות אריזה: {int(progress*100)}%")
with col2:
    if progress == 1.0:
        st.balloons()
        st.success("סיימת לארוז! 🎒")

# --- תצוגת הטאבים ---
tabs = st.tabs(final_list.keys())

for i, (category, items) in enumerate(final_list.items()):
    with tabs[i]:
        st.subheader(f"{category}")
        for item in items:
            # מפתח ייחודי לכל צ'קבוקס כדי למנוע התנגשויות
            is_checked = item in st.session_state.checked_items
            if st.checkbox(item, value=is_checked, key=item):
                if not is_checked:
                    toggle_item(item)
                    st.rerun() # רענון כדי לעדכן את סרגל ההתקדמות
            elif is_checked:
                toggle_item(item)
                st.rerun()

# --- אזור ייצוא ---
st.markdown("---")
text_output = f"רשימת אריזה ל{destination} ({days} ימים):\n\n"
for cat, items in final_list.items():
    text_output += f"{cat}:\n"
    for item in items:
        mark = "V" if item in st.session_state.checked_items else "O"
        text_output += f"[{mark}] {item}\n"
    text_output += "\n"

st.download_button("📥 הורד רשימה כקובץ", text_output, file_name="my_packing_list.txt")
