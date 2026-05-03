import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

# --- Page Settings ---
st.set_page_config(page_title="Pantry Genius", page_icon="📦")

# App ki Styling (Mobile look ke liye)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #4CAF50; color: white; }
    .whatsapp-btn { background-color: #25D366; color: white; border-radius: 10px; padding: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 Smart Pantry Manager")

# Inventory Storage (Temporary)
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}

# Product Info Function
def get_product_name(barcode):
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:
                return data['product'].get('product_name', f"Item {barcode}")
    except:
        pass
    return f"Item {barcode}"

# --- App Tabs ---
tab1, tab2, tab3 = st.tabs(["📷 Scan", "📊 Stock", "🛒 List"])

# TAB 1: Barcode Scanner
with tab1:
    st.subheader("Add Items")
    img_file = st.camera_input("Scan Barcode")
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                name = get_product_name(code)
                if code in st.session_state.inventory:
                    st.session_state.inventory[code]['qty'] += 1
                else:
                    st.session_state.inventory[code] = {"name": name, "qty": 1}
                st.success(f"Added: {name}")
        else:
            st.warning("Barcode nahi mila. Light check karein.")

# TAB 2: Inventory View
with tab2:
    st.subheader("Pantry Stock")
    if not st.session_state.inventory:
        st.write("Abhi pantry khali hai.")
    else:
        for code, details in list(st.session_state.inventory.items()):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{details['name']}**")
            c2.write(f"Qty: {details['qty']}")
            if c3.button("➖", key=f"del_{code}"):
                st.session_state.inventory[code]['qty'] -= 1
                if st.session_state.inventory[code]['qty'] <= 0:
                    del st.session_state.inventory[code]
                st.rerun()

# TAB 3: Shopping List & WhatsApp
with tab3:
    st.subheader("Shopping List")
    low_stock = [d['name'] for d in st.session_state.inventory.values() if d['qty'] < 2]
    
    if not low_stock:
        st.success("Sab kuch stock mein hai! ✅")
    else:
        for item in low_stock:
            st.write(f"- {item}")
        
        # WhatsApp logic
        msg = "🛒 *Shopping List:* \n\n" + "\n".join([f"- {item}" for item in low_stock])
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/?text={encoded_msg}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">📲 WhatsApp par bhejein</a>', unsafe_allow_html=True)
