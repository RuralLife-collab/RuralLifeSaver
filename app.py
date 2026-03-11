import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Se leen desde variables de entorno que configurarás en Render
TOKEN = os.getenv("TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

@app.route("/", methods=["GET"])
def health():
    return "ok", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Debe coincidir con el Verify Token que pondrás en Meta
        verify_token = "ruralmedicos"
        if request.args.get("hub.verify_token") == verify_token:
            return request.args.get("hub.challenge")
        return "Error de verificación", 403

    data = request.json or {}
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "no message", 200

        msg = messages[0]
        number = msg.get("from")
        text = (msg.get("text") or {}).get("body", "").lower().strip()

        # --- Lógica educativa básica ---
        if text == "hola":
            reply = (
                "Hola 👩‍⚕️👨‍⚕️\n"
                "Soy el asistente de *entrenamiento* para médicos rurales.\n\n"
                "Puedo ayudarte con:\n"
                "1️⃣ Emergencias frecuentes\n"
                "2️⃣ Protocolos clínicos\n"
                "3️⃣ Guías rápidas\n"
                "4️⃣ Casos prácticos\n\n"
                "Escribe el número o el tema.\n\n"
                "⚠️ Información educativa; no reemplaza la evaluación clínica."
            )
        elif text == "1":
            reply = (
                "🆘 *Emergencias frecuentes*\n"
                "- Vía aérea: A-B-C.\n"
                "- Shock: IV/IO + cristaloides 30 ml/kg.\n"
                "- Convulsión: diazepam/midazolam según protocolo local.\n"
                "- Referir si no hay respuesta o recursos limitados."
            )
        elif text == "2":
            reply = (
