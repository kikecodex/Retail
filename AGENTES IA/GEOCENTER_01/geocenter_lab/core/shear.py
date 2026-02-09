"""
Direct Shear Test Calculation Module
Based on ASTM D3080 and calibrated to match ENSAYOS.xlsx 'CORTE DIRECTO' sheets
"""
import numpy as np

def calculate_direct_shear(data):
    """
    Calculates cohesion (c) and friction angle (φ) from direct shear test data.
    Uses Mohr-Coulomb failure criterion: τ = c + σ·tan(φ)
    
    Expected Data:
    {
        'specimen_side_cm': 6,
        'specimen_height_cm': 2.544,
        'specimens': [
            {
                'normal_stress': 0.5,  # σn (kg/cm²)
                'shear_stress_max': 0.27  # τmax (kg/cm²) - peak value
            },
            ...
        ]
    }
    
    Or with full stress-strain data:
    {
        'specimens': [
            {
                'normal_stress': 0.5,
                'curve': [
                    {'strain_pct': 0.5, 'shear_stress': 0},
                    {'strain_pct': 1, 'shear_stress': 0.02},
                    ...
                ]
            },
            ...
        ]
    }
    """
    try:
        side = float(data.get('specimen_side_cm', 6))
        height = float(data.get('specimen_height_cm', 2.5))
        specimens = data.get('specimens', [])
        
        # Calculate area (cm²)
        area = side * side
        
        # Extract normal stress (σ) and max shear stress (τ) pairs
        sigma_tau_pairs = []
        specimen_results = []
        
        for i, spec in enumerate(specimens):
            normal_stress = float(spec.get('normal_stress', 0))
            
            # If curve data is provided, find peak shear stress
            if 'curve' in spec:
                curve = spec['curve']
                shear_values = [float(p.get('shear_stress', 0)) for p in curve]
                max_shear = max(shear_values) if shear_values else 0
            else:
                # Direct max value provided
                max_shear = float(spec.get('shear_stress_max', 0))
            
            if normal_stress > 0 and max_shear > 0:
                sigma_tau_pairs.append((normal_stress, max_shear))
            
            specimen_results.append({
                'specimen_num': i + 1,
                'normal_stress': normal_stress,
                'max_shear_stress': round(max_shear, 4)
            })
        
        # Linear regression: τ = c + σ·tan(φ)
        # y = a + b·x  where y=τ, x=σ, a=c, b=tan(φ)
        
        c = 0
        phi = 0
        
        if len(sigma_tau_pairs) >= 2:
            x = np.array([p[0] for p in sigma_tau_pairs])  # σ values
            y = np.array([p[1] for p in sigma_tau_pairs])  # τ values
            
            # Linear fit: y = a + b*x
            b, a = np.polyfit(x, y, 1)  # Note: polyfit returns [b, a] for 1st degree
            
            # c = a (intercept) — clamp to ≥ 0 (physically impossible negative cohesion)
            c = max(0, a)
            
            # φ = atan(b) — clamp to reasonable range [0, 50°]
            phi = np.degrees(np.arctan(b))
            phi = max(0, min(50, phi))
            
        elif len(sigma_tau_pairs) == 1:
            # Single point - can't determine both c and φ
            # Assume φ = 0 and c = τmax (purely cohesive soil assumption)
            c = sigma_tau_pairs[0][1]
            phi = 0
        
        return {
            'success': True,
            'results': {
                'specimen_area_cm2': round(area, 2),
                'specimens': specimen_results,
                'sigma_tau_points': [{'sigma': p[0], 'tau': p[1]} for p in sigma_tau_pairs],
                'cohesion': round(c, 4),       # c (kg/cm²)
                'friction_angle': round(phi, 2) # φ (degrees)
            }
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_shear_stress_from_force(force_kg, area_cm2):
    """Helper: Calculate shear stress from force and area"""
    if area_cm2 > 0:
        return force_kg / area_cm2
    return 0
