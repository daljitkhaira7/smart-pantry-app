import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

st.set_page_config(page_title="Pantry Genius", layout="centered")

if 'inventory' not in st.session_state:
    st.session_state.inventory = {}

def get_product_info(barcode):
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

tab1, tab2, tab3 = st.tabs(["📷 Scan", "📊 Stock", "🛒 List"])

with tab1:
    img_file = st.camera_input("Scan Barcode")
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                name = get_product_info(code)
                if code in st.session_state.inventory:
                    st.session_state.inventory[code]['qty'] += 1
                else:
                    st.session_state.inventory[code] = {"name": name, "qty": 1}
                st.success(f"Added: {name}")

with tab2:
    if not st.session_state.inventory:
        st.write("Pantry khali hai.")
    else:
        for code, details in list(st.session_state.inventory.items()):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(details['name'])
            c2.write(f"Qty: {details['qty']}")
            if c3.button("➖", key=code):
                st.session_state.inventory[code]['qty'] -= 1
                if st.session_state.inventory[code]['qty'] <= 0:
                    del st.session_state.inventory[code]
                st.rerun()

with tab3:
    low_stock = [d['name'] for d in st.session_state.inventory.values() if d['qty'] < 2]
    if low_stock:
        msg = urllib.parse.quote("🛒 Shopping List:\n" + "\n".join(low_stock))
        st.markdown(f'[📲 WhatsApp Share](https://wa.me/?text={msg})')
