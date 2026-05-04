import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse

# --- Layout ---
st.set_page_config(page_title="Auto-Pantry", layout="wide")

if 'inventory' not in st.session_state: st.session_state.inventory = {}

# --- Custom UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .scan-container { border: 2px solid #4CAF50; border-radius: 15px; padding: 10px; background: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🥘 Smart Pantry: Auto-Scan")

# --- Language Settings ---
lang = st.sidebar.selectbox("Language", ["English", "Punjabi", "Hindi"])

# --- Tab System ---
tab1, tab2, tab3 = st.tabs(["📷 Auto-Scanner", "📊 My Stock", "🛒 Shopping List"])

with tab1:
    st.subheader("Place Barcode in front of Camera")
    
    # JavaScript Auto-Scanner Component
    scanner_html = """
    <div id="reader" style="width: 100%; border-radius: 10px; overflow: hidden;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Send the scanned code back to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
        }

        let html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: {width: 250, height: 150} }
        );
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """
    
    # HTML Component to catch the barcode
    scanned_code = components.html(scanner_html, height=450)

    # Logic to handle scanned code
    # Note: Scanned code logic runs when the JS sends a value
    query_params = st.query_params
    last_scanned = st.session_state.get('last_scanned', "")

    # Check if a new scan happened (Using a button to process for now as Streamlit updates)
    scanned_barcode = st.text_input("Last Scanned Barcode (Auto-filled)", key="barcode_input")
    
    if scanned_barcode and scanned_barcode != last_scanned:
        res = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{scanned_barcode}.json")
        name = res.json().get('product', {}).get('product_name', f"Item {scanned_barcode}") if res.status_code == 200 else f"Item {scanned_barcode}"
        
        st.session_state.inventory[scanned_barcode] = st.session_state.inventory.get(scanned_barcode, {"name": name, "qty": 0})
        st.session_state.inventory[scanned_barcode]['qty'] += 1
        st.session_state.last_scanned = scanned_barcode
        st.success(f"Added: {name}")
        st.rerun()

with tab2:
    if not st.session_state.inventory: st.info("Stock is empty")
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
        msg = urllib.parse.quote(f"🛒 *Pantry List:*\n" + "\n".join(list_items))
        st.markdown(f'<a href="https://wa.me/?text={msg}" target="_blank"><button style="width:100%; padding:10px; background:#25D366; color:white; border:none; border-radius:5px;">Share on WhatsApp</button></a>', unsafe_allow_html=True)
