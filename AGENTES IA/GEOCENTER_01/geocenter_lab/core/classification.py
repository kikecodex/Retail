def calculate_sucs(data):
    """
    Determines USCS (SUCS) Classification based on ASTM D2487.
    
    Inputs:
    - fines (% Passing #200)
    - sand (% Passing #4 - % Passing #200) - OR derived from %Pass4
    - gravel (100 - % Passing #4)
    - ll (Liquid Limit)
    - pi (Plasticity Index)
    - cu (Uniformity Coefficient) - optional for GW/SW
    - cc (Curvature Coefficient) - optional for GW/SW
    """
    try:
        fines = float(data.get('p200', 100))
        p4 = float(data.get('p4', 100))
        ll = float(data.get('ll', 0))
        pi = float(data.get('pi', 0))
        cu = float(data.get('cu', 0)) # D60/D10
        cc = float(data.get('cc', 0)) # (D30^2)/(D10*D60)

        gravel = 100 - p4
        sand = p4 - fines
        
        # Helper: A-Line PI value at given LL
        aline_pi = 0.73 * (ll - 20)

        symbol = "??"
        name = "Suelo No Identificado"

        # 1. FINE-GRAINED SOILS (>= 50% pass #200)
        if fines >= 50:
            if ll < 50:
                # Low Plasticity (L)
                if pi > 7 and pi >= aline_pi:
                    symbol = "CL"
                    name = "Arcilla magra (Low Plasticity Clay)"
                elif pi < 4 or pi < aline_pi:
                    symbol = "ML"
                    name = "Limo (Silt)"
                    # Special Case: ML or OL? Usually ML unless organic. 
                    # Special Dual Case CL-ML
                    if 4 <= pi <= 7 and pi >= aline_pi:
                        symbol = "CL-ML"
                        name = "Arcilla limosa"
                else:
                     # Above A-Line but PI check ambiguous?
                     symbol = "CL"
                     name = "Arcilla magra"
            else:
                # High Plasticity (H)
                if pi >= aline_pi:
                    symbol = "CH"
                    name = "Arcilla grasa (High Plasticity Clay)"
                else:
                    symbol = "MH"
                    name = "Limo elástico (Elastic Silt)"

        # 2. COARSE-GRAINED SOILS (< 50% pass #200)
        else:
            # Gravel or Sand?
            # Coarse fraction = 100 - fines
            # % Gravel of Coarse Frac = (Gravel / Coarse) * 100
            if gravel > sand:
                # GRAVEL (G)
                prefix = "G"
                base_name = "Grava"
            else:
                # SAND (S)
                prefix = "S"
                base_name = "Arena"

            # Clean or Dirty?
            if fines < 5:
                # Clean (W or P)
                # Need Cu and Cc
                well_graded = False
                if prefix == "G": # GW criteria: Cu>=4 and 1<=Cc<=3
                    if cu >= 4 and 1 <= cc <= 3: well_graded = True
                elif prefix == "S": # SW criteria: Cu>=6 and 1<=Cc<=3
                    if cu >= 6 and 1 <= cc <= 3: well_graded = True
                
                suffix = "W" if well_graded else "P"
                symbol = f"{prefix}{suffix}"
                name = f"{base_name} {'bien graduada' if well_graded else 'mal graduada'}"

            elif fines > 12:
                # Dirty (M or C)
                # Check fines plasticity (uses A-Line)
                is_clayey = False
                if pi > 7 and pi >= aline_pi: is_clayey = True
                elif pi < 4 or pi < aline_pi: is_clayey = False
                else: is_clayey = True # CL-ML range usually treated as GC-GM? 
                
                # Check for dual symbols in 4-7 range? complex. Simplified:
                suffix = "C" if is_clayey else "M"
                symbol = f"{prefix}{suffix}"
                term = "arcillosa" if is_clayey else "limosa"
                name = f"{base_name} {term}"
                
                if 4 <= pi <= 7 and pi >= aline_pi: # Dual
                     symbol = f"{prefix}C-{prefix}M"
                     name = f"{base_name} arcillo-limosa"
            
            else:
                # Dual Symbols (5% to 12% fines)
                # Requires both grading (W/P) and plasticity (M/C)
                # Simplified dual logic for tool
                w_p = "W"
                # Recheck grading
                well_graded = False
                if prefix == "G": 
                    if cu >= 4 and 1 <= cc <= 3: well_graded = True
                elif prefix == "S":
                    if cu >= 6 and 1 <= cc <= 3: well_graded = True
                w_p = "W" if well_graded else "P"

                is_clayey = False
                if pi >= aline_pi: is_clayey = True # Simplified
                m_c = "C" if is_clayey else "M"

                symbol = f"{prefix}{w_p}-{prefix}{m_c}"
                name = f"{base_name} {'bien' if well_graded else 'mal'} graduada con {'arcilla' if is_clayey else 'limo'}"

        return {
            'success': True,
            'results': {
                'symbol': symbol,
                'name': name,
                'params': {'fines': fines, 'sand': sand, 'gravel': gravel, 'll': ll, 'pi': pi}
            }
        }

    except Exception as e:
        return {'error': str(e)}
