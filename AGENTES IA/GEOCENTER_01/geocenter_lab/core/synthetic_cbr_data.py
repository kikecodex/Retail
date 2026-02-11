"""
Synthetic CBR Data Generator — Ingeniería Inversa
Genera datos crudos de ensayo CBR realistas a partir de parámetros objetivo.

Inputs: SUCS type, Proctor MDD/OMC
Outputs: Raw penetration-load data for 3 specimens that, when processed
         by cbr.py, yield realistic CBR values.

Follows NTP 339.145 / ASTM D1883 procedure.
"""
import math
import random
import numpy as np


# =============================================================================
# CBR TYPICAL RANGES BY SUCS (empirical, from literature)
# =============================================================================
CBR_RANGES = {
    'GW': (40, 80),  'GP': (30, 60),  'GM': (20, 50),  'GC': (15, 40),
    'SW': (20, 50),  'SP': (15, 35),  'SM': (10, 40),  'SC': (5, 20),
    'ML': (5, 15),   'CL': (3, 15),   'OL': (3, 8),
    'MH': (3, 10),   'CH': (2, 8),    'OH': (1, 5),
    'SM-SC': (8, 25), 'CL-ML': (5, 12), 'GW-GM': (35, 70),
    'GP-GM': (25, 55), 'SW-SM': (15, 40), 'SP-SM': (12, 30),
}

# Typical swell ranges by SUCS (%)
SWELL_RANGES = {
    'GW': (0.0, 0.1), 'GP': (0.0, 0.2), 'GM': (0.1, 0.5), 'GC': (0.2, 1.0),
    'SW': (0.0, 0.2), 'SP': (0.0, 0.3), 'SM': (0.1, 0.5), 'SC': (0.3, 1.5),
    'ML': (0.2, 1.0), 'CL': (0.5, 3.0), 'OL': (0.3, 2.0),
    'MH': (1.0, 5.0), 'CH': (2.0, 8.0), 'OH': (1.0, 4.0),
}

# Standard penetrations for readings (mm)
STANDARD_PENETRATIONS = [0.64, 1.27, 1.91, 2.54, 3.81, 5.08, 7.62, 10.16, 12.70]


def _get_range(sucs, ranges_dict, default):
    """Get range for a SUCS type, with fallback."""
    if sucs in ranges_dict:
        return ranges_dict[sucs]
    # Try partial match
    for key in ranges_dict:
        if sucs.startswith(key) or key.startswith(sucs):
            return ranges_dict[key]
    return default


def _generate_penetration_curve(target_cbr, noise_level=0.03):
    """
    Generate a realistic penetration-load curve that yields the target CBR.
    
    Uses a hyperbolic model: Load = (penetration) / (a + b * penetration)
    This naturally produces the concave-downward shape typical of CBR curves.
    
    The target CBR determines the load at 2.54mm (0.1"):
        target_load = CBR/100 * 3000 lbf
    """
    # Target load at 2.54mm
    target_load_254 = (target_cbr / 100) * 3000  # lbf
    
    # Hyperbolic model: L(p) = p / (a + b*p)
    # At large p, L → 1/b (ultimate load)
    # At p=2.54: target_load = 2.54 / (a + b*2.54)
    
    # Set ultimate load ~2.5x the load at 2.54mm (typical for soils)
    ultimate_load = target_load_254 * random.uniform(2.0, 3.0)
    b = 1.0 / ultimate_load if ultimate_load > 0 else 0.01
    
    # Solve for a: target_load = 2.54 / (a + b*2.54)
    if target_load_254 > 0:
        a = (2.54 / target_load_254) - b * 2.54
    else:
        a = 1.0
    
    # Ensure a > 0 (physical meaning: initial stiffness)
    a = max(a, 0.001)
    
    loads = []
    for p in STANDARD_PENETRATIONS:
        base_load = p / (a + b * p)
        # Add realistic noise (±noise_level %)
        noise = random.gauss(1.0, noise_level)
        load = max(0, base_load * noise)
        loads.append(round(load, 1))
    
    # Optionally add slight concave-upward correction at start (30% chance)
    if random.random() < 0.3 and len(loads) > 3:
        # Reduce first 1-2 readings slightly
        loads[0] = round(loads[0] * random.uniform(0.5, 0.8), 1)
        if random.random() < 0.5:
            loads[1] = round(loads[1] * random.uniform(0.85, 0.95), 1)
    
    return loads


def generate_cbr_data(params):
    """
    Generate complete synthetic CBR test data.
    
    Args:
        params: dict with:
            'sucs': str — SUCS classification
            'mdd': float — Maximum dry density from Proctor (g/cm³)
            'omc': float — Optimum moisture content from Proctor (%)
            'target_cbr': float (optional) — specific CBR to target
    
    Returns:
        dict with 3 specimens (56, 25, 10 blows) + proctor reference
    """
    sucs = params.get('sucs', 'CL')
    mdd = float(params.get('mdd', 1.75))
    omc = float(params.get('omc', 12.0))
    
    # Determine target CBR
    cbr_range = _get_range(sucs, CBR_RANGES, (5, 25))
    target_cbr = params.get('target_cbr')
    if target_cbr is None:
        # Pick a random value within the range, biased toward the middle
        mid = (cbr_range[0] + cbr_range[1]) / 2
        spread = (cbr_range[1] - cbr_range[0]) / 4
        target_cbr = max(cbr_range[0], min(cbr_range[1],
                         random.gauss(mid, spread)))
    
    # Determine swell range
    swell_range = _get_range(sucs, SWELL_RANGES, (0.2, 2.0))
    
    # Mold dimensions (standard CBR mold 6" × 7")
    mold_diameter_cm = 15.24  # 6 inches
    mold_height_cm = 17.78    # 7 inches (with collar)
    specimen_height_mm = 116.43  # Standard 4.584" = 116.43mm
    mold_volume_cm3 = 2124    # Standard volume
    mold_weight_g = round(random.uniform(5800, 6500), 0)
    
    specimens = []
    blow_configs = [
        {'blows': 56, 'density_factor': 1.00, 'cbr_factor': 1.00},
        {'blows': 25, 'density_factor': 0.95, 'cbr_factor': 0.70},
        {'blows': 10, 'density_factor': 0.90, 'cbr_factor': 0.45},
    ]
    
    for config in blow_configs:
        blows = config['blows']
        d_factor = config['density_factor']
        cbr_factor = config['cbr_factor']
        
        # Density at this compaction effort
        spec_dry_density = mdd * d_factor * random.uniform(0.98, 1.02)
        spec_moisture = omc * random.uniform(0.95, 1.05)
        spec_wet_density = spec_dry_density * (1 + spec_moisture / 100)
        
        # Wet weight in mold
        wet_weight_g = round(spec_wet_density * mold_volume_cm3 + mold_weight_g, 0)
        
        # CBR for this specimen
        spec_cbr = target_cbr * cbr_factor * random.uniform(0.90, 1.10)
        spec_cbr = max(1.0, spec_cbr)
        
        # Swelling
        swell_pct = random.uniform(swell_range[0], swell_range[1])
        # Higher compaction = less swell
        swell_pct *= (1.1 - d_factor * 0.1)
        final_height = specimen_height_mm * (1 + swell_pct / 100)
        
        # Generate penetration-load curve
        loads = _generate_penetration_curve(spec_cbr)
        
        specimens.append({
            'blows': blows,
            'layers': 5,
            'mold_volume_cm3': mold_volume_cm3,
            'wet_weight_g': round(wet_weight_g, 0),
            'mold_weight_g': round(mold_weight_g, 0),
            'moisture_pct': round(spec_moisture, 1),
            'dry_density': round(spec_dry_density, 3),
            'initial_height_mm': specimen_height_mm,
            'final_height_mm': round(final_height, 2),
            'soak_hours': 96,
            'penetration': list(STANDARD_PENETRATIONS),
            'loads_lbf': loads,
        })
    
    return {
        'specimens': specimens,
        'proctor_mdd': mdd,
        'proctor_omc': omc,
        'sucs': sucs,
        'mold_diameter_cm': mold_diameter_cm,
        'specimen_height_mm': specimen_height_mm,
        'mold_volume_cm3': mold_volume_cm3,
    }
