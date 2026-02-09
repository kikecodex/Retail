"""
Terzaghi Bearing Capacity Calculation Module
Based on ORIGINAL Terzaghi (1943) formulas - calibrated to match ENSAYOS.xlsx exactly
"""
import math

# Terzaghi's original Nγ table (empirical values)
# Key: φ (degrees), Value: Nγ
TERZAGHI_NG_TABLE = {
    0: 0, 1: 0.01, 2: 0.04, 3: 0.06, 4: 0.1, 5: 0.14,
    6: 0.2, 7: 0.27, 8: 0.35, 9: 0.44, 10: 0.56,
    11: 0.69, 12: 0.85, 13: 1.04, 14: 1.26, 15: 1.52,
    16: 1.82, 17: 2.18, 18: 2.59, 19: 3.07, 20: 3.64,
    21: 4.31, 22: 5.09, 23: 6.00, 24: 7.08, 25: 8.34,
    26: 9.84, 27: 11.6, 28: 13.7, 29: 16.18, 30: 19.13,
    31: 22.65, 32: 26.87, 33: 31.94, 34: 38.04, 35: 45.41,
    36: 54.36, 37: 65.27, 38: 78.61, 39: 95.03, 40: 115.31,
    41: 140.51, 42: 171.99, 43: 211.56, 44: 261.60, 45: 325.34
}

def interpolate_ng(phi_deg):
    """Interpolate Nγ from Terzaghi's original table"""
    if phi_deg <= 0:
        return 0
    if phi_deg >= 45:
        return TERZAGHI_NG_TABLE[45]
    
    phi_low = int(phi_deg)
    phi_high = phi_low + 1
    
    ng_low = TERZAGHI_NG_TABLE.get(phi_low, 0)
    ng_high = TERZAGHI_NG_TABLE.get(phi_high, ng_low)
    
    # Linear interpolation
    fraction = phi_deg - phi_low
    return ng_low + (ng_high - ng_low) * fraction

def calculate_bearing_capacity_factors(phi_deg):
    """
    Calculate Terzaghi bearing capacity factors Nc, Nq, Nγ.
    Uses ORIGINAL Terzaghi (1943) formulas as used in ENSAYOS.xlsx:
    
    Nq = exp(2*(3π/4 - φ/2)*tan(φ)) / (2*cos²(45+φ/2))
    Nc = (Nq - 1) * cot(φ)
    Nγ = Table lookup with interpolation
    """
    phi_rad = math.radians(phi_deg)
    
    if phi_deg == 0:
        Nq = 1.0
        Nc = 5.7
        Ng = 0.0
    else:
        # TERZAGHI (1943) Original Formula:
        # Nq = exp(2*(3π/4 - φ/2)*tan(φ)) / (2*cos²(45+φ/2))
        exponent = 2 * (3 * math.pi / 4 - phi_rad / 2) * math.tan(phi_rad)
        Nq = math.exp(exponent) / (2 * (math.cos(math.radians(45 + phi_deg/2)) ** 2))
        
        # Nc = (Nq - 1) * cot(φ)
        Nc = (Nq - 1) / math.tan(phi_rad)
        
        # Nγ from Terzaghi's empirical table with interpolation
        Ng = interpolate_ng(phi_deg)
    
    return {
        'Nc': round(Nc, 2),
        'Nq': round(Nq, 2),
        'Ng': round(Ng, 2)
    }

def calculate_bearing_capacity(data):
    """
    Calculates ultimate and allowable bearing capacity using Terzaghi's method.
    
    Expected Data:
    {
        'cohesion': 0.0563,          # c (kg/cm²)
        'friction_angle': 25.17,      # φ (degrees)
        'unit_weight': 1.86,          # γ (g/cm³ = t/m³)
        'foundation_width': 1.0,      # B (m)
        'foundation_length': 1.0,     # L (m)
        'foundation_depth': 1.3,      # Df (m)
        'foundation_type': 'strip',   # 'strip', 'square', 'circular'
        'failure_mode': 'general',    # 'general' or 'local'
        'factor_of_safety': 3.0       # FS
    }
    """
    try:
        c = float(data.get('cohesion', 0))  # kg/cm²
        phi = float(data.get('friction_angle', 0))  # degrees
        gamma = float(data.get('unit_weight', 0))  # g/cm³ ≈ t/m³
        B = float(data.get('foundation_width', 1))  # m
        L = float(data.get('foundation_length', 1))  # m
        Df = float(data.get('foundation_depth', 1))  # m
        foundation_type = data.get('foundation_type', 'strip')
        failure_mode = data.get('failure_mode', 'general')
        FS = float(data.get('factor_of_safety', 3.0))
        
        # Adjust for local shear failure
        c_eff = c
        phi_eff = phi
        
        if failure_mode == 'local':
            # c' = (2/3) · c
            c_eff = (2/3) * c
            # tan(φ') = (2/3) · tan(φ)  →  φ' = atan((2/3)·tan(φ))
            phi_eff = math.degrees(math.atan((2/3) * math.tan(math.radians(phi))))
        
        # Calculate bearing capacity factors
        factors = calculate_bearing_capacity_factors(phi_eff)
        Nc = factors['Nc']
        Nq = factors['Nq']
        Ng = factors['Ng']
        
        # Convert cohesion to t/m² (from kg/cm²)
        # 1 kg/cm² = 10 t/m²
        c_tm2 = c_eff * 10
        
        # Surcharge q = γ · Df (t/m²)
        q = gamma * Df
        
        # Calculate ultimate bearing capacity based on foundation type
        # Terzaghi formulas:
        if foundation_type == 'strip' or foundation_type == 'corrido':
            # qu = c·Nc + q·Nq + 0.5·γ·B·Nγ
            qu = c_tm2 * Nc + q * Nq + 0.5 * gamma * B * Ng
        
        elif foundation_type == 'square' or foundation_type == 'cuadrada':
            # qu = 1.3·c·Nc + q·Nq + 0.4·γ·B·Nγ
            qu = 1.3 * c_tm2 * Nc + q * Nq + 0.4 * gamma * B * Ng
        
        elif foundation_type == 'circular':
            # qu = 1.3·c·Nc + q·Nq + 0.3·γ·B·Nγ (B = diameter)
            qu = 1.3 * c_tm2 * Nc + q * Nq + 0.3 * gamma * B * Ng
        
        else:  # default: strip
            qu = c_tm2 * Nc + q * Nq + 0.5 * gamma * B * Ng
        
        # Allowable bearing capacity
        qa = qu / FS
        
        # Convert to kg/cm² for display (1 t/m² = 0.1 kg/cm²)
        qu_kgcm2 = qu * 0.1
        qa_kgcm2 = qa * 0.1
        
        return {
            'success': True,
            'results': {
                'inputs': {
                    'c': c,
                    'phi': phi,
                    'gamma': gamma,
                    'B': B,
                    'L': L,
                    'Df': Df,
                    'type': foundation_type,
                    'failure_mode': failure_mode,
                    'FS': FS
                },
                'effective_params': {
                    'c_eff': round(c_eff, 4),
                    'phi_eff': round(phi_eff, 2)
                },
                'factors': factors,
                'qu_tm2': round(qu, 2),
                'qa_tm2': round(qa, 2),
                'qu_kgcm2': round(qu_kgcm2, 2),
                'qa_kgcm2': round(qa_kgcm2, 2)
            }
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_meyerhof_capacity(data):
    """
    Calculates bearing capacity using Meyerhof (1963) method.
    Also estimates elastic settlement.
    
    Meyerhof factors:
        Nq = e^(π·tan(φ)) · tan²(45 + φ/2)
        Nc = (Nq - 1) · cot(φ)
        Nγ = 2·(Nq + 1)·tan(φ)
    
    Shape factors (sc, sq, sγ), Depth factors (dc, dq, dγ)
    """
    try:
        c = float(data.get('cohesion', 0))
        phi = float(data.get('friction_angle', 0))
        gamma = float(data.get('unit_weight', 0))
        B = float(data.get('foundation_width', 1))
        L = float(data.get('foundation_length', 1))
        Df = float(data.get('foundation_depth', 1))
        FS = float(data.get('factor_of_safety', 3.0))
        foundation_type = data.get('foundation_type', 'strip')
        
        phi_rad = math.radians(phi)
        
        # Meyerhof bearing capacity factors
        if phi == 0:
            Nq = 1.0
            Nc = 5.14
            Ng = 0.0
        else:
            Nq = math.exp(math.pi * math.tan(phi_rad)) * (math.tan(math.radians(45 + phi/2)) ** 2)
            Nc = (Nq - 1) / math.tan(phi_rad)
            Ng = 2 * (Nq + 1) * math.tan(phi_rad)
        
        factors = {
            'Nc': round(Nc, 2),
            'Nq': round(Nq, 2),
            'Ng': round(Ng, 2)
        }
        
        # Shape factors
        if foundation_type in ('square', 'cuadrada', 'circular'):
            sc = 1 + 0.2 * (B / L) if L > 0 else 1.2
            sq = 1 + 0.2 * (B / L) if L > 0 else 1.2
            sg = 1 - 0.4 * (B / L) if L > 0 else 0.6
        else:  # strip
            sc = sq = sg = 1.0
        
        # Depth factors
        Kp = math.tan(math.radians(45 + phi/2)) ** 2
        dc = 1 + 0.2 * math.sqrt(Kp) * (Df / B) if B > 0 else 1.0
        dq = 1 + 0.1 * math.sqrt(Kp) * (Df / B) if B > 0 else 1.0
        dg = dq
        
        # Inclination factors (no inclination)
        ic = iq = ig = 1.0
        
        # Convert c to t/m²
        c_tm2 = c * 10
        q = gamma * Df
        
        # qu = c·Nc·sc·dc·ic + q·Nq·sq·dq·iq + 0.5·γ·B·Nγ·sγ·dγ·iγ
        qu = (c_tm2 * Nc * sc * dc * ic +
              q * Nq * sq * dq * iq +
              0.5 * gamma * B * Ng * sg * dg * ig)
        
        qa = qu / FS
        qu_kgcm2 = qu * 0.1
        qa_kgcm2 = qa * 0.1
        
        # Elastic settlement estimation (Bowles 1996)
        # Si = q_applied * B * (1 - μ²) / Es * Is
        # Es and μ based on soil type (Bowles Table 5-6)
        soil_type = data.get('soil_type', '')
        
        # Es estimation by soil type (t/m²)
        es_table = {
            'soft_clay': (25, 40), 'medium_clay': (40, 80), 'hard_clay': (80, 200),
            'loose_sand': (100, 250), 'medium_sand': (250, 500), 'dense_sand': (500, 1000),
            'silt': (20, 200), 'gravel': (500, 1500),
        }
        
        # Auto-detect from phi
        if phi > 35:
            Es = 700  # Dense granular
            mu = 0.25
        elif phi > 28:
            Es = 350  # Medium granular
            mu = 0.30
        elif phi > 20:
            Es = 150  # Loose/silty
            mu = 0.35
        else:
            Es = 60   # Cohesive
            mu = 0.40
        
        Is = 0.82  # Influence factor for square foundation
        if Es > 0:
            settlement_m = qa * B * (1 - mu**2) / Es * Is
            settlement_cm = settlement_m * 100
        else:
            settlement_cm = 0
        
        return {
            'success': True,
            'results': {
                'factors': factors,
                'shape_factors': {'sc': round(sc, 3), 'sq': round(sq, 3), 'sg': round(sg, 3)},
                'depth_factors': {'dc': round(dc, 3), 'dq': round(dq, 3), 'dg': round(dg, 3)},
                'qu_tm2': round(qu, 2),
                'qa_tm2': round(qa, 2),
                'qu_kgcm2': round(qu_kgcm2, 2),
                'qa_kgcm2': round(qa_kgcm2, 2),
                'settlement_cm': round(settlement_cm, 2),
                'settlement_params': {
                    'Es_tm2': round(Es, 1),
                    'mu': mu,
                    'Is': Is,
                }
            }
        }
    except Exception as e:
        return {'error': str(e)}

