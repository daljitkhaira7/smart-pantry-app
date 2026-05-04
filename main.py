import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

st.set_page_config(page_title="Pantry Genius", layout="wide")

if 'inventory' not in st.session_state: st.session_state.inventory = {}

st.title("🥘 Smart Pantry: Scanner Fix")

# --- Scanner Tab ---
img_file = st.camera_input("Scanner (Scan Barcode)")

if img_file:
    try:
        img = Image.open(img_file)
        barcodes = decode(img)
        
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                st.info(f"Scanning: {code}...")
                
                # API Call for Info
                try:
                    res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json", timeout=5)
                    data = res.json()
                    name = data['product'].get('product_name', f"Item {code}") if data.get('status') == 1 else f"Item {code}"
                    photo = data['product'].get('image_url', None) if data.get('status') == 1 else None
                except:
                    name, photo = f"Item {code}", None

                # Update State
                if code not in st.session_state.inventory:
                    st.session_state.inventory[code] = {"name": name, "qty": 1, "photo": photo}
                else:
                    st.session_state.inventory[code]['qty'] += 1
                st.success(f"Added: {name}")
        else:
            st.warning("⚠️ Barcode nahi mila. Light mein dobara try karein.")
    except Exception as e:
        st.error(f"Scanner Error: {e}")
        st.info("Check if packages.txt has 'libzbar0' and requirements.txt has 'pyzbar'")

# --- Inventory Display ---
st.divider()
for code, item in list(st.session_state.inventory.items()):
    with st.container():
        c1, c2, c3 = st.columns([1, 3, 1])
        if item['photo']: c1.image(item['photo'], width=100)
        item['name'] = c2.text_input("Name", value=item['name'], key=f"n_{code}")
        c3.write(f"Qty: {item['qty']}")
        if st.button("Remove", key=f"r_{code}"):
            del st.session_state.inventory[code]
            st.rerun()
