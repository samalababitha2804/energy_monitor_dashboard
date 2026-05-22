import streamlit as st
import os
from PIL import Image
from utils.summarizer import get_summary
from utils.geolocation import get_location
from utils.map_plot import plot_map
from models.inference import detect_waste_user_model
from api.llama_api import detect_waste_api
import streamlit_authenticator as stauth
import yaml
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Smart Waste Management", layout="wide")
st.title("🚮 Smart Waste Management Dashboard")

# Load login config
with open("auth/login_config.yaml") as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name}!")

    uploaded_file = st.file_uploader("Upload Image Frame for Waste Detection", type=["jpg", "png", "jpeg"])
    model_choice = st.selectbox("Select Model", ["User-trained Model", "Pretrained API Model"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Frame", use_column_width=True)

        with open(os.path.join("data/waste_images", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        if model_choice == "User-trained Model":
            detected, label = detect_waste_user_model(image)
        else:
            detected, label = detect_waste_api(image)

        if detected:
            st.success(f"Waste Detected: {label}")
            st.markdown("### ⚠️ Safety Precautions")
            st.write(get_summary(label))

            location = get_location()
            if location:
                st.markdown("### 📍 Waste Location on Map")
                m = plot_map(location['lat'], location['lon'])
                st_folium(m, width=700)

                st.markdown("### 🤖 Bot Cleanup Trigger")
                if st.button("Send Cleanup Bot"):
                    st.success("Cleanup Bot Triggered!")
        else:
            st.info("No Waste Detected.")

elif authentication_status is False:
    st.error("Username/password is incorrect.")
elif authentication_status is None:
    st.warning("Please enter your username and password.")
