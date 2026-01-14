
FILE_PATH = r'c:\Users\Hp\Desktop\Inkalegacy_Paquetes\Llamita\src\core\heart.py'

def remove_duplication():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Identificar el bloque duplicado
    # Sabemos que está alrededor de las líneas 598-627
    # El contenido duplicado empieza con "        # ============ NUEVO: FLUJO ITINERARIO 7 DÍAS ============"
    
    start_marker = "        # ============ NUEVO: FLUJO ITINERARIO 7 DÍAS ============"
    end_marker = "        # ============ FIN NUEVO FLUJO ============"
    
    # Encontrar todas las ocurrencias
    occurrences = []
    for i, line in enumerate(lines):
        if start_marker in line:
            occurrences.append(i)
    
    if len(occurrences) < 2:
        print("No se encontraron duplicados o ya fue arreglado.")
        return

    # Mantener el primer bloque, borrar el segundo
    second_occurrence_index = occurrences[1]
    
    # Buscar el final del segundo bloque
    end_index = -1
    for i in range(second_occurrence_index, len(lines)):
        if end_marker in lines[i]:
            end_index = i
            break
            
    if end_index != -1:
        # Borrar desde second_occurrence_index hasta end_index (inclusive)
        # Nota: líneas son 0-indexed en la lista
        del lines[second_occurrence_index : end_index + 1]
        
        # Eliminar líneas vacías extra que puedan quedar
        while lines[second_occurrence_index].strip() == "":
            del lines[second_occurrence_index]

        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Duplicado eliminado exitosamente.")
    else:
        print("No se encontró el marcador de final para el segundo bloque.")

if __name__ == "__main__":
    remove_duplication()
