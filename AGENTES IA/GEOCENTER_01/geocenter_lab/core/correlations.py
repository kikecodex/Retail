"""
Empirical Correlations Module
Estimates soil parameters using established geotechnical correlations

References:
- Terzaghi & Peck (1967)
- Bowles (1996)
- Das (2002)
"""
import math

def estimate_friction_angle_from_cu(cu, soil_type='sand'):
    """
    Estimate friction angle φ from coefficient of uniformity Cu
    For granular soils (sands and gravels)
    
    φ ≈ 27.5 + 10·log10(Cu)  (for sands, Meyerhof)
    
    Args:
        cu: Coefficient of uniformity (D60/D10)
        soil_type: 'sand' or 'gravel'
    
    Returns:
        dict with estimated φ and confidence
    """
    if cu <= 0:
        return {'phi': None, 'confidence': 0, 'formula': 'N/A'}
    
    if soil_type == 'sand':
        phi = 27.5 + 10 * math.log10(cu)
        confidence = 70
    else:  # gravel
        phi = 30 + 8 * math.log10(cu)
        confidence = 65
    
    # Limit to reasonable range
    phi = max(25, min(45, phi))
    
    return {
        'phi': round(phi, 1),
        'confidence': confidence,
        'formula': 'φ = 27.5 + 10·log₁₀(Cu)',
        'source': 'Meyerhof (1956)'
    }


def estimate_cohesion_from_pi(pi, ll=None):
    """
    Estimate undrained cohesion from plasticity index
    For cohesive soils
    
    cu ≈ 0.01 × PI × σv'  (simplified for surface)
    c ≈ 0.006 × PI × γ × z
    
    For quick estimate at shallow depth:
    c ≈ 0.01 × PI  (in kg/cm², for PI < 50)
    
    Args:
        pi: Plasticity Index (%)
        ll: Liquid Limit (%) - optional for better estimate
    
    Returns:
        dict with estimated c and confidence
    """
    if pi <= 0:
        return {'cohesion': 0, 'confidence': 50, 'formula': 'N/A (PI≤0)'}
    
    # Simple correlation for remolded cohesion
    c = 0.01 * pi
    
    # Adjust based on LL if available (higher LL = weaker soil)
    if ll and ll > 50:
        c *= 0.8  # Reduce for high plasticity
    
    # Limit to reasonable range
    c = max(0.01, min(0.5, c))
    
    return {
        'cohesion': round(c, 3),
        'confidence': 60,
        'formula': 'c ≈ 0.01 × PI',
        'source': 'Skempton (1957)',
        'note': 'Valor aproximado para suelo remoldeado'
    }


def estimate_saturated_density(gamma_d, gs=2.65):
    """
    Estimate saturated unit weight from dry density
    
    γsat = γd + (Gs × γw × n)/(1 + e)
    Simplified: γsat ≈ γd + 0.5 × (1 - γd/Gs)
    
    Args:
        gamma_d: Dry unit weight (g/cm³)
        gs: Specific gravity (default 2.65)
    
    Returns:
        dict with estimated γsat
    """
    if gamma_d <= 0:
        return {'gamma_sat': None, 'confidence': 0}
    
    # Calculate void ratio
    e = (gs * 1.0 / gamma_d) - 1  # assuming γw = 1 g/cm³
    
    # Saturated density
    gamma_sat = (gs + e) * 1.0 / (1 + e)
    
    return {
        'gamma_sat': round(gamma_sat, 3),
        'void_ratio': round(e, 3),
        'confidence': 80,
        'formula': 'γsat = (Gs + e)/(1 + e)',
        'source': 'Teoría de fases'
    }


def estimate_compression_index(ll):
    """
    Estimate compression index Cc from Liquid Limit
    For settlement calculations
    
    Cc ≈ 0.009 × (LL - 10)  (Terzaghi & Peck)
    Cc ≈ 0.007 × (LL - 10)  (Skempton)
    
    Args:
        ll: Liquid Limit (%)
    
    Returns:
        dict with estimated Cc
    """
    if ll <= 10:
        return {'cc': 0, 'confidence': 0}
    
    cc_terzaghi = 0.009 * (ll - 10)
    cc_skempton = 0.007 * (ll - 10)
    
    cc_avg = (cc_terzaghi + cc_skempton) / 2
    
    return {
        'cc': round(cc_avg, 3),
        'cc_range': (round(cc_skempton, 3), round(cc_terzaghi, 3)),
        'confidence': 70,
        'formula': 'Cc = 0.009(LL - 10)',
        'source': 'Terzaghi & Peck (1967)'
    }


def estimate_permeability(d10_mm, cu=None):
    """
    Estimate coefficient of permeability k from D10
    Hazen's formula for clean sands
    
    k = C × D10²  (cm/s)
    C ≈ 100 for clean uniform sands
    
    Args:
        d10_mm: Effective grain size D10 (mm)
        cu: Coefficient of uniformity (optional, for adjustment)
    
    Returns:
        dict with estimated k in cm/s
    """
    if d10_mm <= 0:
        return {'k': None, 'confidence': 0}
    
    # Base Hazen constant
    c = 100
    
    # Adjust for gradation
    if cu and cu > 5:
        c *= 0.8  # Reduce for well-graded soils
    
    k = c * (d10_mm ** 2)  # D10 in cm
    k_cm_per_s = k * 0.01  # Convert if D10 was in mm
    
    # Classify permeability
    if k_cm_per_s > 0.1:
        class_name = 'Alta (grava/arena gruesa)'
    elif k_cm_per_s > 0.001:
        class_name = 'Media (arena fina/limo)'
    else:
        class_name = 'Baja (arcilla/limo)'
    
    return {
        'k': round(k_cm_per_s, 6),
        'k_unit': 'cm/s',
        'class': class_name,
        'confidence': 50,
        'formula': 'k = C × D10² (Hazen)',
        'source': 'Hazen (1911)',
        'note': 'Solo válido para arenas limpias'
    }


def get_all_correlations(test_data):
    """
    Calculate all applicable correlations based on available data
    
    Args:
        test_data: dict with granulometry, limits, proctor data
    
    Returns:
        dict with all estimations
    """
    results = {}
    
    gran = test_data.get('granulometry', {})
    limits = test_data.get('limits', {})
    proctor = test_data.get('proctor', {})
    
    # Friction angle from Cu (for granular soils)
    cu = gran.get('cu', 0)
    if cu > 1:
        results['phi_estimated'] = estimate_friction_angle_from_cu(cu)
    
    # Cohesion from PI (for fine soils)
    pi = limits.get('PI', 0)
    ll = limits.get('LL', 0)
    if pi > 0:
        results['cohesion_estimated'] = estimate_cohesion_from_pi(pi, ll)
    
    # Saturated density from MDD
    mdd = proctor.get('mdd', 0)
    if mdd > 0:
        results['gamma_sat_estimated'] = estimate_saturated_density(mdd)
    
    # Compression index from LL
    if ll > 10:
        results['cc_estimated'] = estimate_compression_index(ll)
    
    # Permeability from D10
    d10 = gran.get('d10', 0)
    if d10 > 0:
        results['permeability_estimated'] = estimate_permeability(d10, cu)
    
    return results
