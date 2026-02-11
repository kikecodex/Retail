"""
CBR (California Bearing Ratio) Calculation Module
NTP 339.145 / ASTM D1883

Inputs: penetration-load readings for 3 specimens (10, 25, 56 blows)
Outputs: CBR at 0.1" and 0.2", corrected curves, CBR at 95%/100% MDD
"""
import math
import numpy as np


# Standard loads (lbf) at key penetrations — ASTM D1883 reference crushed stone
STANDARD_LOADS = {
    2.54: 3000,   # 0.1" → 1000 psi × 3 in²
    5.08: 4500,   # 0.2" → 1500 psi × 3 in²
}

# Standard penetration depths (mm) for readings
STANDARD_PENETRATIONS = [0.64, 1.27, 1.91, 2.54, 3.81, 5.08, 7.62, 10.16, 12.70]

# Piston area: diameter 1.954 in → area ≈ 3.0 in²
PISTON_AREA_IN2 = math.pi * (1.954 / 2) ** 2  # ≈ 2.998 in²


def correct_curve(penetrations, loads):
    """
    Apply concave-upward correction per ASTM D1883.
    
    If the initial portion of the curve is concave upward, draw a tangent
    to the steepest part and shift the origin to where it intersects zero load.
    
    Args:
        penetrations: list of penetration values (mm)
        loads: list of load values (lbf)
    
    Returns:
        (corrected_penetrations, corrected_loads, correction_mm)
    """
    if len(penetrations) < 3 or len(loads) < 3:
        return penetrations, loads, 0.0
    
    # Calculate slopes between consecutive points
    slopes = []
    for i in range(len(loads) - 1):
        dp = penetrations[i + 1] - penetrations[i]
        dl = loads[i + 1] - loads[i]
        slopes.append(dl / dp if dp > 0 else 0)
    
    # Find the maximum slope (steepest part)
    max_slope_idx = max(range(len(slopes)), key=lambda i: slopes[i])
    max_slope = slopes[max_slope_idx]
    
    # Check if correction is needed: slope should increase then decrease
    # If the first few slopes are increasing, the curve is concave upward
    needs_correction = False
    if max_slope_idx > 0:
        for i in range(max_slope_idx):
            if slopes[i] < slopes[i + 1]:
                needs_correction = True
                break
    
    if not needs_correction or max_slope <= 0:
        return list(penetrations), list(loads), 0.0
    
    # Tangent line through the steepest segment: y = max_slope * (x - x0) + y0
    x0 = penetrations[max_slope_idx]
    y0 = loads[max_slope_idx]
    
    # Find where tangent crosses zero: 0 = max_slope * (x - x0) + y0
    x_intercept = x0 - y0 / max_slope
    correction = max(0, x_intercept)
    
    # Shift penetrations
    corrected_pen = [p - correction for p in penetrations]
    corrected_loads = list(loads)
    
    return corrected_pen, corrected_loads, round(correction, 3)


def interpolate_load_at_penetration(penetrations, loads, target_pen):
    """Linear interpolation to get load at a specific penetration depth."""
    if target_pen <= penetrations[0]:
        return loads[0]
    if target_pen >= penetrations[-1]:
        return loads[-1]
    
    for i in range(len(penetrations) - 1):
        if penetrations[i] <= target_pen <= penetrations[i + 1]:
            t = (target_pen - penetrations[i]) / (penetrations[i + 1] - penetrations[i])
            return loads[i] + t * (loads[i + 1] - loads[i])
    
    return loads[-1]


def calculate_cbr_single(penetrations, loads):
    """
    Calculate CBR for a single specimen.
    
    Returns:
        dict with CBR at 0.1" and 0.2", corrected curve, and selected CBR
    """
    # Apply correction
    corr_pen, corr_loads, correction = correct_curve(penetrations, loads)
    
    # Get corrected loads at standard penetrations
    load_01 = interpolate_load_at_penetration(corr_pen, corr_loads, 2.54)
    load_02 = interpolate_load_at_penetration(corr_pen, corr_loads, 5.08)
    
    # CBR = (test load / standard load) × 100
    cbr_01 = (load_01 / STANDARD_LOADS[2.54]) * 100
    cbr_02 = (load_02 / STANDARD_LOADS[5.08]) * 100
    
    # Per ASTM: normally use CBR at 0.1"; if CBR at 0.2" > CBR at 0.1", recheck
    # If confirmed, report CBR at 0.2"
    cbr_selected = max(cbr_01, cbr_02)
    
    return {
        'cbr_01': round(cbr_01, 1),
        'cbr_02': round(cbr_02, 1),
        'cbr_selected': round(cbr_selected, 1),
        'correction_mm': correction,
        'load_at_01': round(load_01, 1),
        'load_at_02': round(load_02, 1),
        'corrected_penetrations': [round(p, 3) for p in corr_pen],
        'corrected_loads': [round(l, 1) for l in corr_loads],
    }


def calculate_cbr(data):
    """
    Full CBR calculation for 3 specimens at different compaction efforts.
    
    Expected data:
    {
        'specimens': [
            {
                'blows': 56,            # blows per layer
                'layers': 5,
                'mold_volume_cm3': 2124, 
                'wet_weight_g': 4250,
                'mold_weight_g': 2050,
                'moisture_pct': 12.3,
                'initial_height_mm': 116.43,
                'final_height_mm': 116.85,  # after soaking
                'soak_hours': 96,
                'penetration': [0.64, 1.27, 1.91, 2.54, 3.81, 5.08, 7.62, 10.16, 12.70],
                'loads_lbf': [45, 120, 230, 350, 520, 650, 830, 940, 1020],
            },
            ...  # 2 more specimens at 25 and 10 blows
        ],
        'proctor_mdd': 1.85,   # g/cm³ from Proctor test
        'proctor_omc': 12.0,   # % from Proctor test
    }
    
    Returns:
        dict with results for each specimen, CBR at 95% and 100% MDD
    """
    try:
        specimens = data.get('specimens', [])
        proctor_mdd = float(data.get('proctor_mdd', 0))
        proctor_omc = float(data.get('proctor_omc', 0))
        
        results = []
        
        for spec in specimens:
            blows = int(spec.get('blows', 56))
            layers = int(spec.get('layers', 5))
            mold_vol = float(spec.get('mold_volume_cm3', 2124))
            wet_weight = float(spec.get('wet_weight_g', 0))
            mold_weight = float(spec.get('mold_weight_g', 0))
            moisture = float(spec.get('moisture_pct', 0))
            
            # Density calculations
            wet_soil = wet_weight - mold_weight
            wet_density = wet_soil / mold_vol if mold_vol > 0 else 0
            dry_density = wet_density / (1 + moisture / 100) if moisture > 0 else wet_density
            
            # Swelling
            h_initial = float(spec.get('initial_height_mm', 116.43))
            h_final = float(spec.get('final_height_mm', h_initial))
            swell_pct = ((h_final - h_initial) / h_initial) * 100 if h_initial > 0 else 0
            
            # CBR calculation
            penetrations = spec.get('penetration', STANDARD_PENETRATIONS)
            loads = spec.get('loads_lbf', [])
            
            cbr_result = calculate_cbr_single(penetrations, loads)
            
            results.append({
                'blows': blows,
                'layers': layers,
                'dry_density': round(dry_density, 3),
                'wet_density': round(wet_density, 3),
                'moisture_pct': round(moisture, 1),
                'swell_pct': round(swell_pct, 2),
                'compaction_pct': round((dry_density / proctor_mdd) * 100, 1) if proctor_mdd > 0 else 0,
                **cbr_result,
            })
        
        # Sort by dry_density for interpolation
        results.sort(key=lambda r: r['dry_density'])
        
        # CBR at 95% and 100% MDD via linear interpolation
        cbr_95 = None
        cbr_100 = None
        
        if proctor_mdd > 0 and len(results) >= 2:
            densities = [r['dry_density'] for r in results]
            cbrs = [r['cbr_selected'] for r in results]
            
            target_95 = proctor_mdd * 0.95
            target_100 = proctor_mdd
            
            # Interpolate
            try:
                cbr_95 = round(float(np.interp(target_95, densities, cbrs)), 1)
            except:
                cbr_95 = None
            
            try:
                cbr_100 = round(float(np.interp(target_100, densities, cbrs)), 1)
            except:
                cbr_100 = None
        
        return {
            'success': True,
            'results': {
                'specimens': results,
                'proctor_mdd': proctor_mdd,
                'proctor_omc': proctor_omc,
                'cbr_95_mdd': cbr_95,
                'cbr_100_mdd': cbr_100,
                'design_cbr': cbr_95,  # Typically use 95% MDD for design
                'method': 'NTP 339.145 / ASTM D1883',
                'soak_condition': 'Saturado (96 h)',
            }
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
