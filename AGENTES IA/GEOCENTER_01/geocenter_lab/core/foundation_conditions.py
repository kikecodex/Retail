"""
Meyerhof Foundation Conditions Calculation Module
Based on Meyerhof (1963) and calibrated to match ENSAYOS.xlsx 'C-A-MEYE-CUADRADA'
Includes bearing capacity and elastic settlement calculations.
"""
import math

def calculate_foundation_conditions(data):
    """
    Calculates bearing capacity (Meyerhof) and elastic settlement.
    
    Expected Data:
    {
        'friction_angle': 25.17,      # φ (degrees)
        'cohesion_kpa': 126.5,        # c (kPa)
        'unit_weight_kn': 16.7,       # γ (kN/m³)
        'foundation_width': 2.17,     # B (m)
        'foundation_length': 2.17,    # L (m)
        'foundation_depth': 1.2,      # Df (m)
        'factor_of_safety': 3.0,      # FS
        'load_inclination': 0,        # β (degrees)
        'elastic_modulus_kpa': 22000, # E (kPa)
        'poisson_ratio': 0.25,        # ν
        'layer_thickness': 8,         # H (m) - soil layer below foundation
        'foundation_type': 'square'   # 'square', 'strip', 'circular'
    }
    """
    try:
        phi = float(data.get('friction_angle', 0))
        c = float(data.get('cohesion_kpa', 0))
        gamma = float(data.get('unit_weight_kn', 0))
        B = float(data.get('foundation_width', 1))
        L = float(data.get('foundation_length', 1))
        Df = float(data.get('foundation_depth', 1))
        FS = float(data.get('factor_of_safety', 3))
        beta = float(data.get('load_inclination', 0))
        E = float(data.get('elastic_modulus_kpa', 22000))
        nu = float(data.get('poisson_ratio', 0.25))
        H = float(data.get('layer_thickness', 8))
        
        phi_rad = math.radians(phi)
        
        # === BEARING CAPACITY FACTORS ===
        if phi == 0:
            Nc = 5.14
            Nq = 1.0
            Ng = 0.0
        else:
            Nq = math.tan(math.radians(45 + phi/2))**2 * math.exp(math.pi * math.tan(phi_rad))
            Nc = (Nq - 1) / math.tan(phi_rad)
            Ng = 2 * (Nq + 1) * math.tan(phi_rad)
        
        # === SHAPE FACTORS ===
        if phi == 0:
            Sc = 1 + (B * Nq) / (L * Nc) if Nc != 0 else 1
            Sq = 1
        else:
            Sc = 1 + (B * Nq) / (L * Nc)
            Sq = 1 + (B / L) * math.tan(phi_rad)
        Sg = 1 - 0.4 * (B / L)
        
        # === DEPTH FACTORS ===
        Df_B = Df / B
        if Df_B <= 1:
            Dc = 1 + 0.4 * Df_B
            if phi == 0:
                Dq = 1
            else:
                Dq = 1 + 2 * math.tan(phi_rad) * (1 - math.sin(phi_rad))**2 * Df_B
        else:
            Dc = 1 + 0.4 * math.atan(Df_B)
            if phi == 0:
                Dq = 1
            else:
                Dq = 1 + 2 * math.tan(phi_rad) * (1 - math.sin(phi_rad))**2 * math.atan(Df_B)
        Dg = 1
        
        # === INCLINATION FACTORS ===
        ic = (1 - beta / 90)**2 if beta < 90 else 0
        iq = ic
        if phi == 0:
            ig = 1
        else:
            ig = (1 - beta / phi)**2 if beta < phi else 0
        
        # === COMPRESSIBILITY FACTORS ===
        # Rigidity Index
        G = E / (2 * (1 + nu))  # Shear modulus
        q_prime = gamma * (Df + B/2)  # Effective surcharge
        
        if phi == 0:
            Ir = G / c if c > 0 else 1
        else:
            Ir = G / (c + q_prime * math.tan(phi_rad)) if (c + q_prime * math.tan(phi_rad)) > 0 else 1
        
        # Critical Rigidity Index
        if phi == 0:
            Ir_cr = 1
        else:
            cot_val = 1 / math.tan(math.radians(45 - phi/2)) if phi != 90 else 0
            Ir_cr = 0.5 * math.exp((3.3 - 0.45 * B/L) * cot_val)
        
        # Compressibility factors
        if Ir >= Ir_cr:
            Fc = Fq = Fg = 1
        else:
            if phi == 0:
                Fc = 0.32 + 0.12 * (B/L) + 0.6 * math.log10(Ir)
                Fq = Fg = 1
            else:
                exp_term = (-4.4 + 0.6 * B/L) * math.tan(phi_rad)
                log_term = (3.07 * math.sin(phi_rad) * math.log10(2 * Ir)) / (1 + math.sin(phi_rad))
                Fq = Fg = math.exp(exp_term + log_term)
                Fc = Fq - (1 - Fq) / (Nq * math.tan(phi_rad)) if Nq * math.tan(phi_rad) != 0 else 1
        
        # === EFFECTIVE COHESION (for local shear) ===
        c_prime = 2/3 * c  # Local shear adjustment
        
        # === SURCHARGE ===
        q = gamma * Df  # Effective overburden
        
        # === ULTIMATE BEARING CAPACITY ===
        term1 = c_prime * Nc * Sc * Dc * ic * Fc
        term2 = q * Nq * Sq * Dq * iq * Fq
        term3 = 0.5 * gamma * B * Ng * Sg * Dg * ig * Fg
        
        qu = term1 + term2 + term3  # kPa
        qa = qu / FS
        
        # Convert to kg/cm²
        qu_kgcm2 = qu / 98.1
        qa_kgcm2 = qa / 98.1
        
        # === ELASTIC SETTLEMENT ===
        # Pressure from structure (assumed equal to qa for design)
        delta_q = qa  # kPa
        
        # Influence factors (approximations for square footing)
        L_B = L / B
        H_B = H / B
        
        # Center influence factor (Ifc)
        Ifc = 1.12  # Standard value for rigid footing
        
        # Corner influence factor (Ife)
        Ife = 0.56  # Approximately Ifc/2
        
        # Settlement calculations (cm)
        Sc_cm = (delta_q * B * (1 - nu**2) * Ifc * 100) / E
        Se_cm = (delta_q * B * (1 - nu**2) * Ife * 100) / E
        Ds_cm = Sc_cm - Se_cm  # Differential settlement
        
        # Maximum allowable settlement (typically 2.5 cm)
        Smax = 2.5
        
        # Adjusted qa if settlement exceeds limit
        if Sc_cm > Smax:
            qa_adjusted_kpa = qa * Smax / Sc_cm
            qa_adjusted_kgcm2 = qa_adjusted_kpa / 98.1
        else:
            qa_adjusted_kpa = qa
            qa_adjusted_kgcm2 = qa_kgcm2
        
        return {
            'success': True,
            'results': {
                'inputs': {
                    'phi': phi,
                    'c_kpa': c,
                    'gamma_kn': gamma,
                    'B': B,
                    'L': L,
                    'Df': Df,
                    'FS': FS
                },
                'bearing_factors': {
                    'Nc': round(Nc, 2),
                    'Nq': round(Nq, 2),
                    'Ng': round(Ng, 2)
                },
                'shape_factors': {
                    'Sc': round(Sc, 4),
                    'Sq': round(Sq, 4),
                    'Sg': round(Sg, 4)
                },
                'depth_factors': {
                    'Dc': round(Dc, 4),
                    'Dq': round(Dq, 4),
                    'Dg': round(Dg, 4)
                },
                'inclination_factors': {
                    'ic': round(ic, 4),
                    'iq': round(iq, 4),
                    'ig': round(ig, 4)
                },
                'compressibility': {
                    'Ir': round(Ir, 2),
                    'Ir_cr': round(Ir_cr, 2),
                    'Fc': round(Fc, 4),
                    'Fq': round(Fq, 4),
                    'Fg': round(Fg, 4)
                },
                'bearing_capacity': {
                    'qu_kpa': round(qu, 2),
                    'qa_kpa': round(qa, 2),
                    'qu_kgcm2': round(qu_kgcm2, 2),
                    'qa_kgcm2': round(qa_kgcm2, 2)
                },
                'settlement': {
                    'Sc_cm': round(Sc_cm, 3),
                    'Se_cm': round(Se_cm, 3),
                    'Ds_cm': round(Ds_cm, 3),
                    'Smax_cm': Smax
                },
                'design': {
                    'qa_design_kpa': round(qa_adjusted_kpa, 2),
                    'qa_design_kgcm2': round(qa_adjusted_kgcm2, 2),
                    'settlement_ok': Sc_cm <= Smax
                }
            }
        }
        
    except Exception as e:
        return {'error': str(e)}
