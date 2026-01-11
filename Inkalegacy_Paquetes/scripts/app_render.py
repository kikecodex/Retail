import os
import traceback
from flask import Flask
from dotenv import load_dotenv

try:
    # Cargar variables de entorno
    load_dotenv()
    
    # Intentar importar el nuevo servicio de Evolution
    from src.integrations.evolution import EvolutionService
    
    # Instanciar Flask y el servicio
    app = Flask(__name__)
    service = EvolutionService(app)
    
except Exception as e:
    # Si algo falla al iniciar, crear una app de respaldo que muestre el error
    app = Flask(__name__)
    error_msg = f"Error starting app:\n{traceback.format_exc()}"
    print(error_msg)

    @app.route('/')
    def index():
        return f"<pre>{error_msg}</pre>", 500

    @app.route('/webhook', methods=['POST'])
    def webhook():
        return "Internal Server Error: App failed to start", 500

if __name__ == "__main__":
    # Obtener puerto del entorno o usar 5000 por defecto
    port = int(os.getenv("PORT", 5000))
    # En local usamos app.run, en prod usa Gunicorn con 'app'
    app.run(port=port, host='0.0.0.0')
