import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Variables que configuras en Render (Settings > Environment)
TOKEN = os.getenv("TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

GRAPH_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def send_text(to: str, body: str):
    """Envía un texto por WhatsApp usando la Cloud API."""
    try:
        requests.post(
            GRAPH_URL,
            headers=HEADERS,
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": body}
            },
            timeout=15
        )
    except Exception as e:
        print("ERROR send_text:", e)

@app.route("/", methods=["GET"])
def health():
    return "ok", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Debe coincidir con el Verify Token en Meta
        verify_token = "ruralmedicos"
        if request.args.get("hub.verify_token") == verify_token:
            return request.args.get("hub.challenge")
        return "Error de verificación", 403

    data = request.json or {}
    try:
        entry = (data.get("entry") or [])[0]
        changes = (entry.get("changes") or [])[0]
        value = changes.get("value") or {}
        messages = value.get("messages") or []
        if not messages:
            return "no message", 200

        msg = messages[0]
        number = msg.get("from")
        text = ((msg.get("text") or {}).get("body") or "").strip().lower()

        # --- Respuestas educativas (multilínea con triple comillas, sin paréntesis) ---
        if text == "hola":
            reply = """Hola 👩‍⚕️👨‍⚕️
Soy el asistente de *entrenamiento* para médicos rurales.

Puedo ayudarte con:
1️⃣ Emergencias frecuentes
2️⃣ Protocolos clínicos
3️⃣ Guías rápidas
4️⃣ Casos prácticos

Escribe el número o el tema.
⚠️ Información educativa; no reemplaza la evaluación clínica."""
        elif text == "1":
            reply = """🆘 *Emergencias frecuentes*
- Vía aérea: A-B-C.
- Shock: IV/IO + cristaloides 30 ml/kg.
- Convulsión: diazepam/midazolam según protocolo local.
- Referir si no hay respuesta o recursos limitados."""
        elif text == "2":
            reply = """📋 *Protocolos clínicos*
- Preeclampsia: sulfato de magnesio (régimen Pritchard), control de PA, referencia oportuna.
- Sepsis: antibiótico precoz, fluidos, cultivos si posible."""
        elif text == "3":
            reply = """⚡ *Guías rápidas*
- Analgesia: escalera OMS.
- Asma exacerbada: SABA + esteroide sistémico.
- IAM sospecha: AAS si no contraindicado y referencia urgente."""
        elif text == "4":
            reply = """🧪 *Caso práctico*
Paciente con PA 170/110, cefalea intensa, 34 semanas.
Escribe *preeclampsia* para ver conducta inicial educativa."""
        elif "preeclampsia" in text:
            reply = """🟣 *Preeclampsia – manejo inicial (educativo)*
1) Monitorizar PA y signos de alarma.
2) Sulfato de magnesio: carga 4 g IV + 10 g IM (según protocolo); mantenimiento 5 g IM c/4 h alternando glúteos.
3) Antihipertensivo (hidralazina/labetalol) si disponible.
4) Referir a nivel superior.
⚠️ Adapta a guías locales."""
        else:
            reply = """Gracias por tu mensaje.
Escribe *hola* para ver el menú (1, 2, 3 o 4)."""

        send_text(number, reply)

    except Exception as e:
        print("ERROR webhook:", e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
