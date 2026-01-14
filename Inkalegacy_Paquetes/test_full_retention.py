import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita')))

from src.core.heart import LlamitaHeart

def test_full_retention():
    """Test del sistema de retención para todos los tours"""
    bot = LlamitaHeart()
    sender = "test_ret_full"
    
    print("=" * 60)
    print("TEST COMPLETO DE RETENCIÓN CON MENSAJES SUBLIMES")
    print("=" * 60)
    
    # Lista de tests: (Estado, Mensaje usuario, Palabra clave esperada)
    tests = [
        ("VIEWING_MACHU_PICCHU", "no me gusta", "secreto"),
        ("VIEWING_MONTANA_7_COLORES", "muy difícil", "solución perfecta"),
        ("VIEWING_VALLE_SAGRADO", "aburrido", "adrenalina"),
        ("VIEWING_OLLANTAYTAMBO", "no me interesa", "alternativas fascinantes"),
        ("VIEWING_WACRAPUCARA", "muy lejos", "vivir la magia"),
        ("VIEWING_HUMANTAY", "no quiero", "otras maravillas"),
        ("VIEWING_PALCOYO", "no me convence", "icónico")
    ]
    
    for state, msg, keyword in tests:
        print(f"\n--- Probando {state} con '{msg}' ---")
        bot.memory.reset_user(sender)
        bot.memory.update_user_state(sender, state)
        
        resp = bot.process_message(msg, sender)
        print(f"Bot: {resp[:150]}...")
        
        passed = keyword.lower() in resp.lower()
        print(f"✅ ¿Mensaje contiene '{keyword}'? {passed}")
        
    print("\n" + "=" * 60)
    print("✅ TODO LISTO")
    print("=" * 60)

if __name__ == "__main__":
    test_full_retention()
