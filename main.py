import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

# --- Modern UI Configuration ---
st.set_page_config(page_title="Pantry Genius", layout="wide", page_icon="🥘")

# Custom CSS for Modern Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 10px; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
if 'inventory' not in st.session_state: st.session_state.inventory = {}
if 'lang' not in st.session_state: st.session_state.lang = "English"

# --- Translations ---
text = {
    "English": {"title": "🥘 Pantry Genius", "scan": "📷 Scan", "stock": "📊 Stock", "recipe": "👩‍🍳 Recipes", "share": "📲 Share List"},
    "Hindi": {"title": "🥘 रसोई जीनियस", "scan": "📷 स्कैन", "stock": "📊 स्टॉक", "recipe": "👩‍🍳 रेसिपी", "share": "📲 लिस्ट भेजें"},
    "Punjabi": {"title": "🥘 ਰਸੋਈ ਜੀਨੀਅਸ", "scan": "📷 ਸਕੈਨ", "stock": "📊 ਸਟਾਕ", "recipe": "👩‍🍳 ਰੈਸਿਪੀ", "share": "📲 ਲਿਸਟ ਭੇਜੋ"}
}

# --- Sidebar (Settings) ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.lang = st.selectbox("Choose Language", ["English", "Hindi", "Punjabi"])
    L = text[st.session_state.lang]

st.title(L["title"])

tab1, tab2, tab3, tab4 = st.tabs([L["scan"], L["stock"], L["recipe"], L["share"]])

# --- Tab 1: Scanner ---
with tab1:
    img_file = st.camera_input("Scan Barcode")
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                # OpenFoodFacts API for Product Name
                res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json")
                name = res.json().get('product', {}).get('product_name', f"Item {code}") if res.status_code == 200 else f"Item {code}"
                st.session_state.inventory[code] = st.session_state.inventory.get(code, {"name": name, "qty": 0})
                st.session_state.inventory[code]['qty'] += 1
                st.success(f"Added: {name}")

# --- Tab 2: Stock Management ---
with tab2:
    if not st.session_state.inventory: st.info("Inventory is empty!")
    for code, details in list(st.session_state.inventory.items()):
        c1, c2, c3 = st.columns([3,1,1])
        c1.write(f"**{details['name']}**")
        c2.write(f"Qty: {details['qty']}")
        if c3.button("➖", key=code):
            st.session_state.inventory[code]['qty'] -= 1
            if st.session_state.inventory[code]['qty'] <= 0: del st.session_state.inventory[code]
            st.rerun()

# --- Tab 3: AI Recipe Suggestions ---
with tab3:
    if st.session_state.inventory:
        items = [d['name'] for d in st.session_state.inventory.values()]
        st.subheader("What can you cook?")
        # Using a simple prompt logic for recipes
        if st.button("Generate Recipes"):
            st.write(f"Based on {', '.join(items[:3])}, you can make:")
            st.info("1. Classic Stir-fry\n2. Quick Pantry Soup\n3. Loaded Sandwiches")
    else:
        st.warning("Please add items to stock first.")

# --- Tab 4: WhatsApp Sharing ---
with tab4:
    low_stock = [f"{d['name']} (Qty: {d['qty']})" for d in st.session_state.inventory.values()]
    if low_stock:
        msg = urllib.parse.quote("🛒 *Shopping List from Pantry Genius:*\n" + "\n".join(low_stock))
        st.markdown(f'''<a href="https://wa.me/?text={msg}" target="_blank">
            <button style="width:100%; height:50px; border-radius:10px; background-color:#25D366; color:white; border:none; font-weight:bold;">
            SEND TO WHATSAPP</button></a>''', unsafe_allow_html=True)
    else:
        st.write("Nothing to buy!")
