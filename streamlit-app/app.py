import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Bot IA - Interface", layout="centered")

st.title("🤖 Chat avec l'IA")

API_BASE_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")
API_CHAT_URL = f"{API_BASE_URL}/chat"
API_HEALTH_URL = f"{API_BASE_URL}/health"
API_CONFIG_URL = f"{API_BASE_URL}/config"

def send_request(url, method="GET", payload=None):
    try:
        if method == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Erreur API ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return None

# 📌 **Section Chat**
message = st.text_input("Pose ta question ici...")

if st.button("Envoyer"):
    if message:
        with st.spinner("🔄 En attente de la réponse..."):
            response_data = send_request(API_CHAT_URL, method="POST", payload={"message": message})
            if response_data:
                st.success("✅ Réponse de l'IA :")
                st.write(response_data.get("response", "Aucune réponse reçue."))
    else:
        st.warning("⚠️ Le message ne peut pas être vide !")

# 📌 **Section Statut API**
st.subheader("🔍 Vérifier l'état de l'API")

if st.button("Vérifier l'API"):
    with st.spinner("🔄 Vérification en cours..."):
        health_data = send_request(API_HEALTH_URL)
        if health_data:
            st.success("✅ L'API est en ligne et fonctionne correctement.")

# 📌 **Section Configuration du Bot**
st.subheader("🎭 Personnalité du bot")

if "current_personality" not in st.session_state:
    config_data = send_request(API_CONFIG_URL)
    st.session_state.current_personality = config_data.get("personality", "neutre") if config_data else "neutre"

st.write(f"Personnalité actuelle : **{st.session_state.current_personality}**")

# Sélecteur de personnalités
new_personality = st.selectbox(
    "Choisissez la personnalité du bot :",
    ["neutre", "sombre", "bienveillant", "drôle"],
    index=["neutre", "sombre", "bienveillant", "drôle"].index(st.session_state.current_personality)
)

if st.button("Mettre à jour"):
    with st.spinner("🔄 Mise à jour de la personnalité..."):
        response_data = send_request(API_CONFIG_URL, method="POST", payload={"personality": new_personality})
        if response_data:
            st.success(f"✅ Personnalité mise à jour en : **{new_personality}**")
            st.session_state.current_personality = new_personality  
