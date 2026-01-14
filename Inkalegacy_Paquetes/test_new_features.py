import sys
import os

# Agregar el directorio raíz al path para importar módulos correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita')))

from src.core.heart import LlamitaHeart

def test_new_features():
    """Test para verificar las nuevas funcionalidades implementadas"""
    bot = LlamitaHeart()
    sender = "test_new_features"
    
    # Reset del usuario para asegurar estado limpio
    bot.memory.reset_user(sender)
    
    print("=" * 60)
    print("TEST 1: DETECCIÓN AVANZADA DE TOURS CON SINÓNIMOS")
    print("=" * 60)
    
    # Probar sinónimos de Machu Picchu
    msg1 = "quiero ver la ciudadela"
    resp1 = bot.process_message(msg1, sender)
    print(f"\nUser: {msg1}")
    print(f"Bot: {resp1[:150]}...")
    
    # Verificar que detectó Machu Picchu
    state1 = bot.memory.get_user_state(sender)
    print(f"Estado actual: {state1}")
    
    # Reset para siguiente test
    bot.memory.reset_user(sender)
    
    print("\n" + "=" * 60)
    print("TEST 2: SECRETO LOCAL - MONTAÑA DE COLORES")
    print("=" * 60)
    
    # Ir al menú primero
    bot.process_message("hola", sender)
    bot.memory.update_user_state(sender, "MENU")
    
    # Probar secreto local cuando pregunta por montaña colores
    msg2 = "4"
    resp2 = bot.process_message(msg2, sender)
    print(f"\nUser: {msg2}")
    print(f"Bot: {resp2[:200]}...")
    
    # Verificar que activó el secreto o mostró los detalles
    has_secret = "secreto local" in resp2.lower() or "palcoyo" in resp2.lower() or "90%" in resp2
    has_details = "MONTAÑA" in resp2 or "7 COLORES" in resp2.upper()
    print(f"¿Activó secreto local o mostró detalles? {has_secret or has_details}")
    
    # Reset para siguiente test
    bot.memory.reset_user(sender)
    
    print("\n" + "=" * 60)
    print("TEST 3: FALLBACK INTELIGENTE CONTEXTUAL")
    print("=" * 60)
    
    # Poner usuario en estado MENU
    bot.memory.update_user_state(sender, "MENU")
    
    # Enviar mensaje que no se entiende
    msg3 = "xyz asdfgh 12345"
    resp3 = bot.process_message(msg3, sender)
    print(f"\nUser: {msg3}")
    print(f"Bot: {resp3}")
    
    # Verificar que el fallback tiene opciones claras
    has_options = "*1*" in resp3 or "1 →" in resp3 or "1️⃣" in resp3
    print(f"¿Fallback tiene opciones numéricas? {has_options}")
    
    # Reset para siguiente test
    bot.memory.reset_user(sender)
    
    print("\n" + "=" * 60)
    print("TEST 4: IMAGINEMOS JUNTOS (después de 5+ interacciones)")
    print("=" * 60)
    
    # Simular múltiples interacciones
    for i in range(6):
        bot.memory.add_message_to_history(sender, f"mensaje {i}", "user")
    
    bot.memory.update_user_state(sender, "MENU")
    
    # Enviar mensaje que active el fallback
    msg4 = "xyz no entiendo"
    resp4 = bot.process_message(msg4, sender)
    print(f"\nUser: {msg4}")
    print(f"Bot: {resp4[:300]}...")
    
    # Verificar si activó Imaginemos Juntos
    has_imaginemos = "imaginemos" in resp4.lower() or "cierra los ojos" in resp4.lower() or "amanecer" in resp4.lower()
    print(f"¿Activó Imaginemos Juntos? {has_imaginemos}")
    
    # Reset para siguiente test  
    bot.memory.reset_user(sender)
    
    print("\n" + "=" * 60)
    print("TEST 5: VALIDACIÓN DE DATOS DE BOOKING")
    print("=" * 60)
    
    # Poner usuario en estado de booking
    bot.memory.update_user_state(sender, "BOOKING_MACHU_PICCHU")
    
    # Enviar datos incompletos
    msg5 = "Juan Pérez"
    resp5 = bot.process_message(msg5, sender)
    print(f"\nUser: {msg5}")
    print(f"Bot: {resp5}")
    
    # Verificar que pide datos faltantes
    asks_for_more = "falta" in resp5.lower() or "teléfono" in resp5.lower() or "fecha" in resp5.lower()
    print(f"¿Pide datos faltantes? {asks_for_more}")
    
    # Ahora enviar datos completos
    msg6 = "Juan Pérez, 987654321, 15 de febrero"
    resp6 = bot.process_message(msg6, sender)
    print(f"\nUser: {msg6}")
    print(f"Bot: {resp6[:200]}...")
    
    # Verificar confirmación
    confirms = "gracias" in resp6.lower() or "recibido" in resp6.lower() or "resumen" in resp6.lower()
    print(f"¿Confirmó la reserva? {confirms}")
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS EJECUTADOS")
    print("=" * 60)

if __name__ == "__main__":
    test_new_features()
