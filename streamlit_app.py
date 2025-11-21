import streamlit as st
import pandas as pd

# --- כותרת והגדרות עיצוב ---
st.set_page_config(page_title="PackSmart", page_icon="🧳")

st.title("🧳 PackSmart - הצ'ק ליסט החכם שלך")
st.markdown("הזן את פרטי הנסיעה וקבל רשימה מותאמת אישית בשניות.")

# --- אזור הקלט (סרגל צד) ---
st.sidebar.header("פרטי הנסיעה")

days = st.sidebar.number_input("כמה ימים תימשך הנסיעה?", min_value=1, value=5)
weather = st.sidebar.selectbox("מה צפוי להיות מזג האוויר?", ["חם / קיצי", "קר / חורפי", "נעים / מעורב", "גשום מאוד"])
trip_type = st.sidebar.selectbox("סוג הנסיעה", ["חופשה עירונית", "בטן-גב (ים)", "נסיעת עסקים", "טיול תרמילאים/שטח"])
accommodation = st.sidebar.radio("איפה ישנים?", ["מלון (מספקים הכל)", "דירה/Airbnb", "קמפינג"])
is_international = st.sidebar.checkbox("האם זו טיסה לחו\"ל?", value=True)
do_laundry = st.sidebar.checkbox("האם תעשה כביסה במהלך הטיול?", value=False)

# --- הלוגיקה ליצירת הרשימה ---
def generate_packing_list(days, weather, trip_type, accommodation, is_international, do_laundry):
    
    packing_list = {
        "ביגוד": [],
        "רחצה והיגיינה": [],
        "אלקטרוניקה": [],
        "מסמכים וכסף": [],
        "שונות": []
    }

    # --- חישוב כמויות ---
    # אם עושים כביסה, אורזים ל-7 ימים מקסימום, אחרת לכל התקופה + 1 ספייר
    clothes_count = min(days + 1, 7) if do_laundry else days + 1
    
    # --- ביגוד בסיסי ---
    packing_list["ביגוד"].append(f"{clothes_count} תחתונים")
    packing_list["ביגוד"].append(f"{clothes_count} זוגות גרביים")
    packing_list["ביגוד"].append(f"{int(days/2) + 1} מכנסיים")
    packing_list["ביגוד"].append(f"{clothes_count} חולצות")
    packing_list["ביגוד"].append("פיג'מה / בגדי שינה")

    # --- התאמות מזג אוויר ---
    if "קר" in weather or "גשום" in weather:
        packing_list["ביגוד"].extend(["מעיל חם", "צעיף וכפפות", "גופיות תרמיות"])
        packing_list["שונות"].append("מטריה")
    elif "חם" in weather:
        packing_list["ביגוד"].extend(["כובע", "משקפי שמש"])
        packing_list["שונות"].append("קרם הגנה")
    
    # --- התאמות סוג טיול ---
    if trip_type == "בטן-גב (ים)":
        packing_list["ביגוד"].extend(["2 בגדי ים", "כפכפים"])
        packing_list["שונות"].append("מגבת חוף")
    elif trip_type == "נסיעת עסקים":
        packing_list["ביגוד"].extend(["חליפה/לבוש רשמי", "נעליים אלגנטיות", "חגורה"])
        packing_list["אלקטרוניקה"].append("לפטופ + מטען")
    elif trip_type == "טיול תרמילאים/שטח":
        packing_list["ביגוד"].append("נעלי הליכה נוחות")
        packing_list["שונות"].extend(["תיק עזרה ראשונה", "פנס", "אולר/לדרמן"])

    # --- התאמות לינה ---
    if accommodation != "מלון (מספקים הכל)":
        packing_list["רחצה והיגיינה"].extend(["שמפו וסבון גוף", "מגבת רחצה"])
    
    packing_list["רחצה והיגיינה"].extend(["מברשת ומשחת שיניים", "דאודורנט", "מסרק/מברשת שיער", "תיק רחצה"])

    # --- אלקטרוניקה ---
    packing_list["אלקטרוניקה"].extend(["מטען לטלפון", "אוזניות"])
    if is_international:
        packing_list["אלקטרוניקה"].append("מתאם לשקע חשמל (Universal Adapter)")
        packing_list["אלקטרוניקה"].append("Power Bank (סוללה ניידת)")

    # --- מסמכים ---
    packing_list["מסמכים וכסף"].extend(["ארנק + כרטיסי אשראי", "תעודה מזהה"])
    if is_international:
        packing_list["מסמכים וכסף"].extend(["דרכון בתוקף", "ביטוח נסיעות (מודפס/בטלפון)", "מטבע מקומי"])

    return packing_list

# --- יצירת הרשימה והצגה ---
if st.button("צור לי צ'ק ליסט לאריזה! 🚀"):
    final_list = generate_packing_list(days, weather, trip_type, accommodation, is_international, do_laundry)
    
    st.success(f"הרשימה שלך מוכנה! נסיעה ל-{days} ימים.")
    
    # תצוגה ויזואלית של הרשימה
    for category, items in final_list.items():
        if items: # רק אם יש פריטים בקטגוריה
            st.subheader(category)
            for item in items:
                st.checkbox(item, key=f"{category}_{item}")
            st.markdown("---")

# --- הערה תחתונה ---
st.info("טיפ: הרשימה נשמרת זמנית עד לרענון העמוד. צלם מסך לפני שאתה יוצא!")
