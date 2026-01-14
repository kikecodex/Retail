import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita')))

from src.core.heart import LlamitaHeart

def test_retention():
    """Test del sistema de retención cuando el usuario está insatisfecho"""
    bot = LlamitaHeart()
    sender = "test_retention"
    
    # Reset usuario
    bot.memory.reset_user(sender)
    
    print("=" * 60)
    print("TEST DE RETENCIÓN - ALTERNATIVAS PARA ENGANCHAR")
    print("=" * 60)
    
    # Test 1: Usuario en Machu Picchu dice "no me gusta"
    print("\n--- Test 1: Usuario viendo Machu Picchu dice 'no me gusta' ---")
    bot.memory.update_user_state(sender, "VIEWING_MACHU_PICCHU")
    resp1 = bot.process_message("no me gusta", sender)
    print(f"Bot: {resp1[:300]}...")
    has_alternatives = "alternativas" in resp1.lower() or "7 colores" in resp1.lower() or "humantay" in resp1.lower()
    print(f"✅ ¿Ofreció alternativas? {has_alternatives}")
    
    # Test 2: Usuario en Montaña 7 Colores dice "muy difícil"
    print("\n--- Test 2: Usuario viendo Montaña 7 Colores dice 'muy difícil' ---")
    bot.memory.reset_user(sender)
    bot.memory.update_user_state(sender, "VIEWING_MONTANA_7_COLORES")
    resp2 = bot.process_message("muy difícil", sender)
    print(f"Bot: {resp2[:300]}...")
    has_palcoyo = "palcoyo" in resp2.lower()
    print(f"✅ ¿Sugirió Palcoyo? {has_palcoyo}")
    
    # Test 3: Usuario dice "otra cosa"
    print("\n--- Test 3: Usuario en Valle Sagrado dice 'busco algo diferente' ---")
    bot.memory.reset_user(sender)
    bot.memory.update_user_state(sender, "VIEWING_VALLE_SAGRADO")
    resp3 = bot.process_message("busco algo diferente", sender)
    print(f"Bot: {resp3[:300]}...")
    has_options = "machu picchu" in resp3.lower() or "waqrapukara" in resp3.lower()
    print(f"✅ ¿Ofreció otras opciones? {has_options}")
    
    # Test 4: Error message mejorado
    print("\n--- Test 4: Mensaje de error con enganche ---")
    bot.memory.reset_user(sender)
    bot.memory.update_user_state(sender, "MENU")
    resp4 = bot.process_message("xyz123", sender)
    print(f"Bot: {resp4[:400]}...")
    has_hook = "popular" in resp4.lower() or "sabías" in resp4.lower()
    print(f"✅ ¿Tiene gancho de retención? {has_hook}")
    
    print("\n" + "=" * 60)
    print("✅ TESTS DE RETENCIÓN COMPLETADOS")
    print("=" * 60)

if __name__ == "__main__":
    test_retention()
