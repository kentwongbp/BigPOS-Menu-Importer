import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Setup the Webpage
st.set_page_config(page_title="BigPOS Menu Importer", page_icon="🍔")
st.title("BigPOS AI Menu Importer")
st.write("Drag and drop a menu image below to instantly generate a BigPOS-ready CSV file.")

# 2. Securely load the Google Gemini API Key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key missing. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# 3. Create the Upload Box
uploaded_file = st.file_uploader("Upload Menu Image (JPG/PNG)", type=["jpg", "jpeg", "png"])

# 4. The Hidden "Master Prompt"
prompt = """
You are a highly accurate data extraction assistant. Read the attached menu image and convert the items into a strict CSV structure.

Instructions:
1. Extract every food/drink item, its price, its category (e.g., Mains, Drinks), and a brief description.
2. Strip away all currency symbols (e.g., remove "RM"). Only output the raw number for the price.
3. The output MUST be in raw CSV format.
4. Use a comma as the delimiter. If an Item Name or Description contains a comma, enclose that field in double quotes.
5. The first row MUST be exactly: Category,Item Name,Price,Description
6. ONLY output the raw CSV data. Do not use markdown blocks like ```csv. No introductory text. Just the raw text.
"""

# 5. The Action Logic
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Menu Preview", use_container_width=True)
    
    if st.button("Generate CSV"):
        with st.spinner("AI is analyzing the menu (usually takes 10-20 seconds)..."):
            try:
                # Use Gemini 1.5 Flash (Fast, free, great at vision)
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content([prompt, image])
                
                csv_data = response.text.strip()
                
                # Failsafe: Clean up markdown if the AI accidentally includes it
                if csv_data.startswith("```"):
                    csv_data = "\n".join(csv_data.split("\n")[1:-1])
                
                st.success("Menu extracted successfully!")
                
                # 6. The Download Button
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="bigpos_menu_import.csv",
                    mime="text/csv"
                )
                
                # Let staff verify the data before downloading
                with st.expander("Preview CSV Data"):
                    st.text(csv_data)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
