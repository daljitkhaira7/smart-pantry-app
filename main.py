import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

# --- Page Config ---
st.set_page_config(page_title="Pantry Genius", page_icon="📦")

# Inventory State
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}

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

st.title("📦 Smart Pantry")

tab1, tab2, tab3 = st.tabs(["📷 Scan", "📊 Stock", "🛒 List"])

with tab1:
    st.subheader("Barcode Scanner")
    img_file = st.camera_input("Take a clear photo of the barcode")
    
    if img_file:
        img = Image.open(img_file)
        # Barcode decode logic
        barcodes = decode(img)
        
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                name = get_product_name(code)
                
                # Update Inventory
                if code in st.session_state.inventory:
                    st.session_state.inventory[code]['qty'] += 1
                else:
                    st.session_state.inventory[code] = {"name": name, "qty": 1}
                
                st.success(f"Detected & Added: {name} ({code})")
        else:
            st.error("❌ Barcode nahi mila. Thoda door se ya achhi light mein photo kheenchein.")
            st.info("Tip: Barcode photo mein bilkul saaf (clear) hona chahiye.")

with tab2:
    st.subheader("Current Stock")
    if not st.session_state.inventory:
        st.write("Pantry khali hai.")
    else:
        for code, details in list(st.session_state.inventory.items()):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{details['name']}**")
            col2.write(f"Qty: {details['qty']}")
            if col3.button("➖", key=f"del_{code}"):
                st.session_state.inventory[code]['qty'] -= 1
                if st.session_state.inventory[code]['qty'] <= 0:
                    del st.session_state.inventory[code]
                st.rerun()

with tab3:
    st.subheader("Shopping List")
    low_stock = [d['name'] for d in st.session_state.inventory.values() if d['qty'] < 2]
    if low_stock:
        for item in low_stock:
            st.write(f"- {item}")
        msg = urllib.parse.quote("🛒 *Shopping List:*\n" + "\n".join([f"- {i}" for i in low_stock]))
        st.markdown(f'[📲 WhatsApp par bhejein](https://wa.me/?text={msg})')
    else:
        st.write("Sab kuch stock mein hai! ✅")
