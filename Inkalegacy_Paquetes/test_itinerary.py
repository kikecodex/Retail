import sys
import os

# Agregar el directorio raíz al path para importar módulos correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita')))

from src.core.heart import LlamitaHeart

def test_itinerary_flow():
    bot = LlamitaHeart()
    sender = "test_user_itinerary"
    
    # Reset del usuario para asegurar estado limpio
    bot.memory.reset_user(sender)
    
    print("--- INICIANDO TEST DE ITINERARIO 7 DÍAS ---")
    
    # 1. Solicitud inicial
    msg1 = "quisiera que me organices un tours en Cusco, Valle sagrado y Machu Picchu durante una semana"
    resp1 = bot.process_message(msg1, sender)
    print(f"\nUser: {msg1}")
    print(f"Bot: {resp1[:100]}...") # Mostrar solo inicio para no llenar consola
    
    assert "Una semana es ideal" in resp1, "Fallo en paso 1: No detectó intención de semana"
    assert "Te gustaría que te presente una propuesta" in resp1, "Fallo en paso 1: No pidió confirmación"
    
    # 2. Confirmación
    msg2 = "si"
    resp2 = bot.process_message(msg2, sender)
    print(f"\nUser: {msg2}")
    print(f"Bot: {resp2[:100]}...")
    
    assert "DÍA 1" in resp2 or "Día 1" in resp2, "Fallo en paso 2: No mostró itinerario"
    assert "DÍA 7" in resp2 or "Día 7" in resp2, "Fallo en paso 2: Itinerario incompleto"
    assert "fecha" in resp2.lower(), "Fallo en paso 2: No preguntó fecha al final"

    # 3. Fecha
    msg3 = "deseo viajar el 15 de febrero"
    resp3 = bot.process_message(msg3, sender)
    print(f"\nUser: {msg3}")
    print(f"Bot: {resp3}")
    
    assert "alojamiento" in resp3.lower(), "Fallo en paso 3: No preguntó alojamiento"
    assert "Económico" in resp3 or "económico" in resp3.lower(), "Fallo en paso 3: No mostró opciones"

    # 4. Alojamiento
    msg4 = "2"
    resp4 = bot.process_message(msg4, sender)
    print(f"\nUser: {msg4}")
    print(f"Bot: {resp4}")
    
    assert "asesor" in resp4.lower() or "confirmación" in resp4.lower() or "propuesta" in resp4.lower(), "Fallo en paso 4: No dio cierre final"
    
    print("\n✅ TEST PASADO EXITOSAMENTE")

if __name__ == "__main__":
    test_itinerary_flow()
