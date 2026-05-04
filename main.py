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

if 'inventory' not in st.session_state: st.session_state.inventory = {}
if 'lang' not in st.session_state: st.session_state.lang = "English"

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.lang = st.selectbox("Language", ["English", "Hindi", "Punjabi"])
    L = {"English": "Scan", "Hindi": "स्कैन", "Punjabi": "ਸਕੈਨ"}

st.title("🥘 Pantry Genius")

tab1, tab2, tab3 = st.tabs(["📷 Scanner", "📊 Stock", "🛒 Share"])

with tab1:
    st.info("Barcode ki saaf photo kheenchiye")
    img_file = st.camera_input("Scanner")
    
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                # OpenFoodFacts API
                res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json")
                name = res.json().get('product', {}).get('product_name', f"Item {code}") if res.status_code == 200 else f"Item {code}"
                
                if code in st.session_state.inventory:
                    st.session_state.inventory[code]['qty'] += 1
                else:
                    st.session_state.inventory[code] = {"name": name, "qty": 1}
                st.success(f"Added: {name}")
        else:
            st.warning("Barcode detected nahi hua. Light aur focus check karein.")

with tab2:
    if not st.session_state.inventory: st.write("Stock is empty.")
    for code, item in list(st.session_state.inventory.items()):
        c1, c2, c3 = st.columns([3,1,1])
        c1.write(f"**{item['name']}**")
        c2.write(f"Qty: {item['qty']}")
        if c3.button("➖", key=code):
            st.session_state.inventory[code]['qty'] -= 1
            if st.session_state.inventory[code]['qty'] <= 0: del st.session_state.inventory[code]
            st.rerun()

with tab3:
    list_items = [f"- {i['name']} (Qty: {i['qty']})" for i in st.session_state.inventory.values()]
    if list_items:
        msg = urllib.parse.quote("🛒 *Shopping List:*\n" + "\n".join(list_items))
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; height:50px; border-radius:10px; background-color:#25D366; color:white; border:none; font-weight:bold;">WHATSAPP PAR BHEJEIN</button></a>', unsafe_allow_html=True)
