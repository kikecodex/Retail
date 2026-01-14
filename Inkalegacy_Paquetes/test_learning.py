import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita')))

from src.core.heart import LlamitaHeart

def test_auto_learning():
    """Test del sistema de aprendizaje automático"""
    bot = LlamitaHeart()
    sender = "test_learning_user"
    
    print("=" * 60)
    print("TEST DE APRENDIZAJE AUTOMÁTICO")
    print("=" * 60)
    
    # 1. Enviar consulta desconocida (gibberish para asegurar fallback)
    msg1 = "quiero ir a la luna de jupiter x99"
    print(f"\nUsuario: {msg1}")
    resp1 = bot.process_message(msg1, sender)
    print(f"Bot: {resp1[:100]}...")
    
    # 2. Enviar otra consulta desconocida clara
    msg2 = "tour a la atlántida perdida costo"
    print(f"\nUsuario: {msg2}")
    resp2 = bot.process_message(msg2, sender)
    print(f"Bot: {resp2[:100]}...")
    
    # Esperar un momento para asegurar escritura en disco
    time.sleep(1)
    
    # 3. Verificar archivo unknown_queries.json
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Llamita'))
    queries_file = os.path.join(base_dir, "src", "data", "unknown_queries.json")
    print(f"\nVerificando archivo {queries_file}...")
    
    if os.path.exists(queries_file):
        with open(queries_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        user_queries = data.get(sender, [])
        print(f"Consultas guardadas para el usuario: {len(user_queries)}")
        
        found_jupiter = any("jupiter" in q["message"].lower() for q in user_queries)
        found_atlantida = any("atlántida" in q["message"].lower() or "atlan" in q["message"].lower() for q in user_queries)
        
        print(f"✅ ¿Guardó 'Jupiter'? {found_jupiter}")
        print(f"✅ ¿Guardó 'Atlantida'? {found_atlantida}")
        
        if user_queries:
            last_query = user_queries[-1]
            print(f"Última ubicación detectada: {last_query.get('location')}")
    else:
        print(f"❌ El archivo de consultas desconocidas no se creó en {queries_file}")
        
    # 4. Verificar archivo knowledge_base.json
    kb_file = os.path.join(base_dir, "src", "data", "knowledge_base.json")
    print(f"\nVerificando archivo {kb_file}...")
    
    if os.path.exists(kb_file):
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
            
        stats = kb_data.get("statistics", {})
        print(f"Estadísticas KB: {stats}")
        
        top_locations = [loc["name"] for loc in stats.get("top_unknown_locations", [])]
        print(f"Top ubicaciones desconocidas: {top_locations}")
        
        has_kb_entry = any("Atlántida" in loc or "Júpiter" in loc or "Jupiter" in loc for loc in top_locations)
        print(f"✅ ¿Aparece Jupiter/Atlantida en top locations? {has_kb_entry}")
        
        # 3. Probar comando de reporte
        print("\n--------- Probar Reporte ---------")
        msg3 = "stats aprendizaje"
        bot.memory.update_user_state(sender, "MENU") # Asegurar estado MENU
        print(f"Usuario: {msg3}")
        resp3 = bot.process_message(msg3, sender)
        print(f"Bot: {resp3[:200]}...")
        
        has_report_data = "ESTADÍSTICAS DE APRENDIZAJE" in resp3
        print(f"✅ ¿Mostró reporte? {has_report_data}")
        
    else:
        print("❌ El archivo de base de conocimiento no se creó.")

    print("\n" + "=" * 60)
    print("✅ TEST DE APRENDIZAJE COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_auto_learning()
