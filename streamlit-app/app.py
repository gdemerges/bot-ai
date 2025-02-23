import streamlit as st
import requests
import os

st.set_page_config(page_title="Bot IA - Interface", layout="centered")

st.title("🤖 Chat avec l'IA (via API)")

API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/chat")

message = st.text_input("Pose ta question ici...")

if st.button("Envoyer"):
    if message:
        response = requests.post(API_URL, json={"message": message})

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
        health_response = requests.get(API_HEALTH_URL)
        if health_response.status_code == 200:
            st.success("✅ L'API est en ligne et fonctionne correctement.")
        else:
            st.error(f"❌ Problème avec l'API ({health_response.status_code})")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")