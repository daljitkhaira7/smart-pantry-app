import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

# --- Modern UI Configuration ---
st.set_page_config(page_title="Pantry Genius", layout="wide", page_icon="🥘")

# State Management
if 'inventory' not in st.session_state: st.session_state.inventory = {}

st.title("🥘 Smart Pantry Genius")

tab1, tab2, tab3 = st.tabs(["📷 Scan Item", "📊 My Stock", "🛒 Share List"])

with tab1:
    st.info("Barcode ki saaf photo kheenchiye")
    img_file = st.camera_input("Scanner")
    
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                
                # Fetch Name & Photo from API
                res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json")
                data = res.json() if res.status_code == 200 else {}
                
                if data.get('status') == 1:
                    name = data['product'].get('product_name', f"Item {code}")
                    photo = data['product'].get('image_url', None)
                else:
                    name = f"Item {code}"
                    photo = None
                
                # Add to Inventory with Photo support
                if code not in st.session_state.inventory:
                    st.session_state.inventory[code] = {"name": name, "qty": 1, "photo": photo}
                else:
                    st.session_state.inventory[code]['qty'] += 1
                
                st.success(f"Added: {name}")
                if photo:
                    st.image(photo, width=150, caption="Product Photo")
        else:
            st.warning("Barcode detected nahi hua. Light aur focus check karein.")

with tab2:
    st.subheader("Current Inventory")
    if not st.session_state.inventory: 
        st.write("Stock khali hai.")
    else:
        for code, item in list(st.session_state.inventory.items()):
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
                
                # Photo Display
                if item.get('photo'):
                    c1.image(item['photo'], width=80)
                else:
                    c1.write("🖼️ No Photo")
                
                # Name & Edit
                new_name = c2.text_input("Name", value=item['name'], key=f"name_{code}")
                st.session_state.inventory[code]['name'] = new_name
                
                c3.write(f"Qty: {item['qty']}")
                
                if c4.button("➖", key=f"del_{code}"):
                    st.session_state.inventory[code]['qty'] -= 1
                    if st.session_state.inventory[code]['qty'] <= 0: 
                        del st.session_state.inventory[code]
                    st.rerun()
            st.divider()

with tab3:
    list_items = [f"- {i['name']} (Qty: {i['qty']})" for i in st.session_state.inventory.values()]
    if list_items:
        msg = urllib.parse.quote("🛒 *Shopping List:*\n" + "\n".join(list_items))
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; height:50px; border-radius:10px; background-color:#25D366; color:white; border:none; font-weight:bold; cursor:pointer;">WHATSAPP PAR BHEJEIN</button></a>', unsafe_allow_html=True)
