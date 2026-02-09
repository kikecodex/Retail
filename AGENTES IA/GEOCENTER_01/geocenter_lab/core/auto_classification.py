"""
Auto-Classification SUCS Module
Based on ASTM D2487 - Standard Practice for Classification of Soils

This module automatically determines SUCS classification based on:
- Granulometry: % passing #200, #4, #10 sieves
- Atterberg Limits: LL, PL, PI
- Coefficients: Cu, Cc
"""

def get_sucs_classification(granulometry, limits, coefficients=None):
    """
    Auto-classify soil according to SUCS (ASTM D2487)
    
    Args:
        granulometry: dict with keys 'p200', 'p4', 'p10' (percent passing)
        limits: dict with keys 'LL', 'PL', 'PI' (Atterberg limits)
        coefficients: dict with keys 'Cu', 'Cc' (uniformity, curvature)
    
    Returns:
        dict with 'symbol', 'name', 'group', 'description', 'confidence'
    """
    p200 = granulometry.get('p200', 0)  # % passing #200
    p4 = granulometry.get('p4', 100)    # % passing #4
    p10 = granulometry.get('p10', 100)  # % passing #10
    
    ll = limits.get('LL', 0)
    pl = limits.get('PL', 0)
    pi = limits.get('PI', ll - pl if ll and pl else 0)
    
    cu = coefficients.get('Cu', 0) if coefficients else 0
    cc = coefficients.get('Cc', 0) if coefficients else 0
    
    # Calculate derived values
    gravel_percent = 100 - p4  # % retained on #4
    sand_percent = p4 - p200   # Between #4 and #200
    fines_percent = p200       # Passing #200
    
    # Determine if above or below Line A on Plasticity Chart
    # Line A: PI = 0.73 * (LL - 20)
    line_a = 0.73 * (ll - 20) if ll > 20 else 0
    above_line_a = pi > line_a
    
    result = {
        'symbol': '',
        'name': '',
        'group': '',
        'description': '',
        'confidence': 0,
        'details': {
            'gravel_percent': round(gravel_percent, 1),
            'sand_percent': round(sand_percent, 1),
            'fines_percent': round(fines_percent, 1),
            'above_line_a': above_line_a,
            'line_a_value': round(line_a, 1)
        }
    }
    
    # ========== CLASSIFICATION ALGORITHM ==========
    
    # 1. COARSE-GRAINED SOILS (< 50% passing #200)
    if fines_percent < 50:
        result['group'] = 'SUELO GRUESO'
        
        # 1.1 GRAVEL (> 50% of coarse fraction retained on #4)
        coarse_fraction = 100 - fines_percent
        gravel_of_coarse = (gravel_percent / coarse_fraction * 100) if coarse_fraction > 0 else 0
        
        if gravel_of_coarse > 50:
            # GRAVEL classifications
            result['group'] = 'GRAVA'
            
            if fines_percent < 5:
                # Clean gravel
                if cu >= 4 and 1 <= cc <= 3:
                    result['symbol'] = 'GW'
                    result['name'] = 'Grava bien graduada'
                    result['confidence'] = 95
                else:
                    result['symbol'] = 'GP'
                    result['name'] = 'Grava mal graduada'
                    result['confidence'] = 90
                    
            elif fines_percent > 12:
                # Gravel with fines
                if pi < 4 or not above_line_a:
                    result['symbol'] = 'GM'
                    result['name'] = 'Grava limosa'
                    result['confidence'] = 85
                else:
                    result['symbol'] = 'GC'
                    result['name'] = 'Grava arcillosa'
                    result['confidence'] = 85
                    
            else:  # 5-12% fines (borderline)
                if cu >= 4 and 1 <= cc <= 3:
                    if pi < 4 or not above_line_a:
                        result['symbol'] = 'GW-GM'
                        result['name'] = 'Grava bien graduada con limo'
                    else:
                        result['symbol'] = 'GW-GC'
                        result['name'] = 'Grava bien graduada con arcilla'
                else:
                    if pi < 4 or not above_line_a:
                        result['symbol'] = 'GP-GM'
                        result['name'] = 'Grava mal graduada con limo'
                    else:
                        result['symbol'] = 'GP-GC'
                        result['name'] = 'Grava mal graduada con arcilla'
                result['confidence'] = 75
                
        else:
            # SAND classifications
            result['group'] = 'ARENA'
            
            if fines_percent < 5:
                # Clean sand
                if cu >= 6 and 1 <= cc <= 3:
                    result['symbol'] = 'SW'
                    result['name'] = 'Arena bien graduada'
                    result['confidence'] = 95
                else:
                    result['symbol'] = 'SP'
                    result['name'] = 'Arena mal graduada'
                    result['confidence'] = 90
                    
            elif fines_percent > 12:
                # Sand with fines
                if pi < 4 or not above_line_a:
                    result['symbol'] = 'SM'
                    result['name'] = 'Arena limosa'
                    result['confidence'] = 85
                else:
                    result['symbol'] = 'SC'
                    result['name'] = 'Arena arcillosa'
                    result['confidence'] = 85
                    
            else:  # 5-12% fines (borderline)
                if cu >= 6 and 1 <= cc <= 3:
                    if pi < 4 or not above_line_a:
                        result['symbol'] = 'SW-SM'
                        result['name'] = 'Arena bien graduada con limo'
                    else:
                        result['symbol'] = 'SW-SC'
                        result['name'] = 'Arena bien graduada con arcilla'
                else:
                    if pi < 4 or not above_line_a:
                        result['symbol'] = 'SP-SM'
                        result['name'] = 'Arena mal graduada con limo'
                    else:
                        result['symbol'] = 'SP-SC'
                        result['name'] = 'Arena mal graduada con arcilla'
                result['confidence'] = 75
    
    # 2. FINE-GRAINED SOILS (≥ 50% passing #200)
    else:
        result['group'] = 'SUELO FINO'
        
        # Check if organic (simplified - would need color/smell test in reality)
        is_organic = False  # TODO: Add organic detection
        
        if ll < 50:
            # Low plasticity
            if is_organic:
                result['symbol'] = 'OL'
                result['name'] = 'Limo o arcilla orgánica de baja plasticidad'
                result['confidence'] = 70
            elif pi < 4 or not above_line_a:
                result['symbol'] = 'ML'
                result['name'] = 'Limo'
                result['confidence'] = 90
            elif 4 <= pi <= 7 and above_line_a:
                result['symbol'] = 'CL-ML'
                result['name'] = 'Arcilla limosa'
                result['confidence'] = 80
            else:
                result['symbol'] = 'CL'
                result['name'] = 'Arcilla de baja plasticidad'
                result['confidence'] = 90
        else:
            # High plasticity (LL ≥ 50)
            if is_organic:
                result['symbol'] = 'OH'
                result['name'] = 'Limo o arcilla orgánica de alta plasticidad'
                result['confidence'] = 70
            elif above_line_a:
                result['symbol'] = 'CH'
                result['name'] = 'Arcilla de alta plasticidad'
                result['confidence'] = 90
            else:
                result['symbol'] = 'MH'
                result['name'] = 'Limo elástico'
                result['confidence'] = 85
    
    # Generate description
    result['description'] = generate_description(result, granulometry, limits)
    
    return result


def generate_description(classification, granulometry, limits):
    """Generate a human-readable description of the soil"""
    desc = f"{classification['name']} ({classification['symbol']}). "
    
    p200 = granulometry.get('p200', 0)
    ll = limits.get('LL', 0)
    pi = limits.get('PI', 0)
    
    if p200 < 50:
        desc += f"Suelo grueso con {p200:.1f}% de finos. "
    else:
        desc += f"Suelo fino con {p200:.1f}% pasando malla #200. "
    
    if ll > 0:
        desc += f"LL={ll:.1f}%, IP={pi:.1f}%. "
    
    if classification['confidence'] < 80:
        desc += "⚠️ Clasificación con incertidumbre moderada."
    
    return desc


def get_plasticity_chart_position(ll, pi):
    """
    Calculate position on Casagrande Plasticity Chart
    
    Returns dict with:
        - position: (ll, pi) coordinates
        - line_a: PI value on Line A at this LL
        - line_u: PI value on Line U at this LL
        - zone: 'CL', 'CH', 'ML', 'MH', 'CL-ML', 'OL', 'OH'
    """
    line_a = 0.73 * (ll - 20) if ll > 20 else 0
    line_u = 0.9 * (ll - 8) if ll > 8 else 0
    
    zone = ''
    if ll < 50:
        if pi > line_a and pi >= 4:
            zone = 'CL'
        elif 4 <= pi <= 7 and pi > line_a:
            zone = 'CL-ML'
        else:
            zone = 'ML'
    else:
        if pi > line_a:
            zone = 'CH'
        else:
            zone = 'MH'
    
    return {
        'position': {'x': ll, 'y': pi},
        'line_a': round(line_a, 2),
        'line_u': round(line_u, 2),
        'zone': zone,
        'above_line_a': pi > line_a
    }
