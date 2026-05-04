import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

st.set_page_config(page_title="Pantry Genius Pro", layout="wide", page_icon="🥘")

if 'inventory' not in st.session_state: st.session_state.inventory = {}

st.title("🥘 Smart Pantry: Name & Photo Manager")

tab1, tab2, tab3 = st.tabs(["📷 Scan & Add", "📊 My Stock", "🛒 Share"])

with tab1:
    st.info("Barcode scan karein. Agar info nahi aati, toh niche manual add karein.")
    img_file = st.camera_input("Scanner")
    
    if img_file:
        img = Image.open(img_file)
        barcodes = decode(img)
        
        if barcodes:
            for b in barcodes:
                code = b.data.decode('utf-8')
                st.write(f"🔍 Searching Barcode: {code}...")
                
                # API Call
                try:
                    res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json", timeout=5)
                    data = res.json()
                    if data.get('status') == 1:
                        p = data['product']
                        name = p.get('product_name', f"New Item ({code})")
                        photo = p.get('image_url', None)
                        st.success(f"Found: {name}")
                    else:
                        name = f"Unknown Item ({code})"
                        photo = None
                        st.warning("Database mein info nahi mili. Aap naam badal sakte hain.")
                except:
                    name = f"Item {code}"
                    photo = None
                    st.error("API Connection Error!")

                # Add to State
                if code not in st.session_state.inventory:
                    st.session_state.inventory[code] = {"name": name, "qty": 1, "photo": photo}
                else:
                    st.session_state.inventory[code]['qty'] += 1
                st.rerun()
        else:
            st.error("Barcode detected nahi hua. Light check karein!")

with tab2:
    st.subheader("Manage Inventory")
    if not st.session_state.inventory:
        st.write("Abhi koi item nahi hai.")
    else:
        for code, item in list(st.session_state.inventory.items()):
            with st.expander(f"📦 {item['name']} (Qty: {item['qty']})", expanded=True):
                c1, c2 = st.columns([1, 3])
                
                # Photo Management
                with c1:
                    if item['photo']:
                        st.image(item['photo'], width=120)
                    else:
                        new_photo = st.file_uploader("Add Photo", type=['jpg', 'png'], key=f"pic_{code}")
                        if new_photo:
                            st.session_state.inventory[code]['photo'] = new_photo
                            st.rerun()

                # Name & Qty Management
                with c2:
                    # Manual Name Edit
                    updated_name = st.text_input("Product Name", value=item['name'], key=f"nm_{code}")
                    st.session_state.inventory[code]['name'] = updated_name
                    
                    col_a, col_b = st.columns(2)
                    col_a.write(f"**Barcode:** {code}")
                    if col_b.button("Delete Item", key=f"del_{code}"):
                        del st.session_state.inventory[code]
                        st.rerun()

with tab3:
    list_items = [f"- {i['name']} (Qty: {i['qty']})" for i in st.session_state.inventory.values()]
    if list_items:
        msg = urllib.parse.quote("🛒 *Pantry Shopping List:*\n" + "\n".join(list_items))
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; padding:10px; background:#25D366; color:white; border:none; border-radius:10px; cursor:pointer;">SHARE ON WHATSAPP</button></a>', unsafe_allow_html=True)
