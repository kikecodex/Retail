import requests
import json
import os
from flask import Flask, request, jsonify
from src.core.heart import LlamitaHeart

class EvolutionService:
    def __init__(self, app: Flask = None):
        self.app = app if app else Flask(__name__)
        self.heart = LlamitaHeart()
        self.api_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
        
        if self.app:
            self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/")
        def index():
            return jsonify({"status": "online", "message": "Llamita API is running"}), 200

        @self.app.route("/webhook", methods=["POST"])
        def evolution_webhook():
            data = request.json
            print(f"Webhook recibido de Evolution: {json.dumps(data, indent=2)}")
            
            # Evolution API envía diferentes tipos de eventos
            if data.get("event") == "messages.upsert":
                message_data = data.get("data", {})
                
                # Evitar procesar mensajes enviados por el propio bot
                if message_data.get("key", {}).get("fromMe"):
                    return "Ignored self message", 200
                
                sender = message_data.get("key", {}).get("remoteJid")
                message_content = ""
                
                # Extraer texto según el tipo de mensaje
                msg = message_data.get("message", {})
                if "conversation" in msg:
                    message_content = msg["conversation"]
                elif "extendedTextMessage" in msg:
                    message_content = msg["extendedTextMessage"].get("text", "")
                
                if message_content and sender:
                    print(f"Mensaje de {sender}: {message_content}")
                    response_text = self.heart.process_message(message_content, sender)
                    self.send_whatsapp_message(sender, response_text)
            
            return "OK", 200

        @self.app.route("/api/chat", methods=["POST"])
        def web_chat():
            data = request.json
            message = data.get("message")
            sender = data.get("sender", "guest_web")
            
            if not message:
                return jsonify({"error": "No message provided"}), 400
            
            print(f"Chat Web de {sender}: {message}")
            response_text = self.heart.process_message(message, sender)
            return jsonify({"response": response_text})

    def send_whatsapp_message(self, remote_jid, text):
        if not self.api_url or not self.api_key or not self.instance_name:
            print("Error: Evolution API config missing")
            return None
            
        url = f"{self.api_url}/message/sendText/{self.instance_name}"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        payload = {
            "number": remote_jid,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": True
            },
            "textMessage": {
                "text": text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            print(f"Respuesta de Evolution API al enviar: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"Error enviando mensaje a Evolution API: {e}")
            return None
