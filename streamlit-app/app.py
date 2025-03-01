import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Bot IA - Interface", layout="centered")

st.title("🤖 Chat avec l'IA (via API)")

API_URL = "http://127.0.0.1:8000/chat"

message = st.text_input("Pose ta question ici...")

if st.button("Envoyer"):
    if message:
        response = requests.post(API_URL, json={"message": message}, timeout=10)

        if response.status_code == 200:
            data = response.json()
            st.success("✅ Réponse de l'IA :")
            st.write(data["response"])
        else:
            st.error(f"❌ Erreur API : {response.status_code} - {response.text}")
    else:
        st.warning("⚠️ Le message ne peut pas être vide !")

st.subheader("🔍 Vérifier l'état de l'API")
API_HEALTH_URL = os.getenv("FASTAPI_HEALTH_URL", "http://localhost:8000/health")

if st.button("Vérifier l'API"):
    try:
        health_response = requests.get(API_HEALTH_URL, timeout=10)
        if health_response.status_code == 200:
            st.success("✅ L'API est en ligne et fonctionne correctement.")
        else:
            st.error(f"❌ Problème avec l'API ({health_response.status_code})")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur : {e}")
              
st.title("🤖 Configuration du Bot")

API_CONFIG_URL = "http://127.0.0.1:8000/config"

response = requests.get(API_CONFIG_URL, timeout=10)
if response.status_code == 200:
    current_config = response.json()
else:
    st.error("❌ Impossible de récupérer la configuration actuelle.")
    current_config = {"personality": "neutre"}

st.subheader("🎭 Personnalité actuelle du bot")
st.write(f"Personnalité : **{current_config['personality']}**")

new_personality = st.selectbox(
    "Choisissez la personnalité du bot :",
    ["neutre", "sombre", "bienveillant", "drôle"]
)

if st.button("Mettre à jour"):
    response = requests.post(API_CONFIG_URL, json={"personality": new_personality}, timeout=10)
    if response.status_code == 200:
        st.success(f"✅ Personnalité mise à jour en : **{new_personality}**")
    else:
        st.error("❌ Erreur lors de la mise à jour.")
