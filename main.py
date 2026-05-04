import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse

st.set_page_config(page_title="Pantry Genius", layout="wide")

if 'inventory' not in st.session_state: st.session_state.inventory = {}

st.title("🥘 Smart Pantry Auto-Scanner")

# --- CSS for UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    iframe { border-radius: 15px; border: 2px solid #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# --- Scanner Section ---
st.subheader("📷 Scan Barcode Below")

# JavaScript with Auto-Focus and Faster FPS
scanner_html = """
<div id="reader" style="width: 100%;"></div>
<script src="https://unpkg.com/html5-qrcode"></script>
<script>
    function onScanSuccess(decodedText) {
        // Send to Streamlit URL as query parameter
        const url = new URL(window.location.href);
        url.searchParams.set('scanned', decodedText);
        window.parent.location.href = url.toString();
    }

    let config = { fps: 20, qrbox: {width: 280, height: 180}, rememberLastUsedCamera: true };
    let html5QrcodeScanner = new html5QrcodeScanner("reader", config);
    html5QrcodeScanner.render(onScanSuccess);
</script>
"""

# HTML component height increase for better visibility
components.html(scanner_html, height=500)

# Catch the scanned value from URL
query_params = st.query_params
if "scanned" in query_params:
    barcode = query_params["scanned"]
    
    # Process only if not already processed in this session
    res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json")
    name = res.json().get('product', {}).get('product_name', f"Item {barcode}") if res.status_code == 200 else f"Item {barcode}"
    
    st.session_state.inventory[barcode] = st.session_state.inventory.get(barcode, {"name": name, "qty": 0})
    st.session_state.inventory[barcode]['qty'] += 1
    
    st.success(f"✅ Added: {name}")
    # Clear URL to prevent infinite loop
    st.query_params.clear()
    st.rerun()

# --- Stock Section ---
st.divider()
st.subheader("📊 Current Stock")
if st.session_state.inventory:
    for code, item in list(st.session_state.inventory.items()):
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{item['name']}**")
        col2.write(f"Qty: {item['qty']}")
        if col3.button("➖", key=code):
            st.session_state.inventory[code]['qty'] -= 1
            if st.session_state.inventory[code]['qty'] <= 0: del st.session_state.inventory[code]
            st.rerun()
else:
    st.info("Pantry khali hai. Barcode scan karein!")
