import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import urllib.parse

st.set_page_config(page_title="Pantry Genius Pro", layout="wide", page_icon="🥘")

# State Management
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}

st.title("🥘 Smart Pantry: Manual & Auto Mode")

tab1, tab2, tab3 = st.tabs(["📷 Scan Item", "📊 My Stock", "🛒 Share List"])

with tab1:
    st.info("Barcode scan karein. Agar info nahi aati, toh Stock tab mein naam edit karein.")
    img_file = st.camera_input("Scanner")
    
    if img_file:
        try:
            img = Image.open(img_file)
            barcodes = decode(img)
            
            if barcodes:
                for b in barcodes:
                    code = b.data.decode('utf-8')
                    st.write(f"🔍 Searching: {code}...")
                    
                    # API Se data mangane ki koshish
                    try:
                        res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json", timeout=5)
                        data = res.json()
                        if data.get('status') == 1:
                            name = data['product'].get('product_name', f"New Item ({code})")
                            photo = data['product'].get('image_url', None)
                        else:
                            name = f"Unknown ({code})"
                            photo = None
                    except:
                        name, photo = f"Item {code}", None

                    # Inventory mein save karein
                    if code not in st.session_state.inventory:
                        st.session_state.inventory[code] = {"name": name, "qty": 1, "photo": photo}
                        st.success(f"Added: {name}")
                    else:
                        st.session_state.inventory[code]['qty'] += 1
                        st.info(f"Updated quantity for: {name}")
                    st.rerun()
            else:
                st.error("Barcode detected nahi hua. Light check karein!")
        except Exception as e:
            st.error(f"Error: {e}. Check if packages.txt has libzbar0.")

with tab2:
    st.subheader("Manage Your Stock")
    if not st.session_state.inventory:
        st.write("Abhi koi item nahi hai.")
    else:
        for code, item in list(st.session_state.inventory.items()):
            with st.expander(f"📦 {item['name']} (Qty: {item['qty']})", expanded=True):
                c1, c2 = st.columns([1, 3])
                
                with c1:
                    if item['photo']:
                        st.image(item['photo'], width=120)
                    else:
                        st.write("🖼️ No Image")
                
                with c2:
                    # Manual Name Edit (Sabse zaroori feature)
                    item['name'] = st.text_input("Edit Name", value=item['name'], key=f"nm_{code}")
                    
                    col_a, col_b = st.columns(2)
                    col_a.write(f"**Barcode:** {code}")
                    if col_b.button("Delete", key=f"del_{code}"):
                        del st.session_state.inventory[code]
                        st.rerun()
            st.divider()

with tab3:
    list_items = [f"- {i['name']} (Qty: {i['qty']})" for i in st.session_state.inventory.values()]
    if list_items:
        msg = urllib.parse.quote("🛒 *Shopping List:*\n" + "\n".join(list_items))
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; height:50px; border-radius:10px; background-color:#25D366; color:white; border:none; font-weight:bold; cursor:pointer;">WHATSAPP PAR BHEJEIN</button></a>', unsafe_allow_html=True)
