"""
Proctor Modificado Calculation Module
Based on ASTM D1557 and calibrated to match ENSAYOS.xlsx
"""
import math
import numpy as np

def calculate_proctor(data):
    """
    Calculates compaction curve, MDD, and OMC.
    
    Expected Data:
    {
        'mold': {
            'height_cm': 11.65,
            'diameter_cm': 15.2,
            'weight_g': 4200  # Weight of empty mold
        },
        'points': [
            {
                'samples': [
                    {'tare': 53.24, 'wet_tare': 176.21, 'dry_tare': 172.58},
                    {'tare': 52.47, 'wet_tare': 166.84, 'dry_tare': ...}
                ],
                'mold_wet_g': 5890  # Mold + Wet Compacted Soil
            },
            ... (typically 5 points)
        ]
    }
    """
    try:
        mold = data.get('mold', {})
        height = float(mold.get('height_cm', 0))
        diameter = float(mold.get('diameter_cm', 0))
        mold_weight = float(mold.get('weight_g', 0))
        
        # Calculate mold volume (cm³) = π × (D/2)² × H
        volume = math.pi * ((diameter / 2) ** 2) * height
        volume = round(volume, 2)
        
        points_data = data.get('points', [])
        results = []
        
        for i, point in enumerate(points_data):
            # Calculate average moisture content from samples
            samples = point.get('samples', [])
            moistures = []
            
            for s in samples:
                tare = float(s.get('tare', 0))
                wet_tare = float(s.get('wet_tare', 0))
                dry_tare = float(s.get('dry_tare', 0))
                
                if wet_tare > dry_tare > tare > 0:
                    water = wet_tare - dry_tare
                    solid = dry_tare - tare
                    w = (water / solid) * 100
                    moistures.append(w)
            
            avg_moisture = sum(moistures) / len(moistures) if moistures else 0
            
            # Calculate densities
            mold_wet = float(point.get('mold_wet_g', 0))
            wet_soil = mold_wet - mold_weight
            
            wet_density = 0
            dry_density = 0
            
            if volume > 0:
                wet_density = wet_soil / volume  # g/cm³
                
                # Dry Density: γd = γw / (1 + w/100)
                if avg_moisture > 0:
                    dry_density = wet_density / (1 + avg_moisture / 100)
                else:
                    dry_density = wet_density
            
            results.append({
                'point_num': i + 1,
                'moisture_percent': round(avg_moisture, 2),
                'wet_density': round(wet_density, 3),
                'dry_density': round(dry_density, 3)
            })
        
        # Find MDD and OMC
        # Option 1: Simple max lookup
        # Option 2: Polynomial fit (better accuracy)
        
        if len(results) >= 3:
            w_values = [r['moisture_percent'] for r in results]
            d_values = [r['dry_density'] for r in results]
            
            # Fit 2nd degree polynomial: γd = a*w² + b*w + c
            coeffs = np.polyfit(w_values, d_values, 2)
            a, b, c = coeffs
            
            # OMC is at vertex: w_opt = -b / (2a)
            if a != 0 and a < 0:  # Must be concave down for a valid peak
                omc = -b / (2 * a)
                mdd = a * omc**2 + b * omc + c
                
                # Validate OMC is within measured range (prevent extrapolation)
                w_min, w_max = min(w_values), max(w_values)
                if omc < w_min or omc > w_max:
                    # Fallback to observed max
                    max_idx = d_values.index(max(d_values))
                    omc = w_values[max_idx]
                    mdd = d_values[max_idx]
            else:
                # Fallback to simple max
                max_idx = d_values.index(max(d_values))
                omc = w_values[max_idx]
                mdd = d_values[max_idx]
        else:
            # Not enough points for curve fitting
            max_idx = 0
            max_d = 0
            for i, r in enumerate(results):
                if r['dry_density'] > max_d:
                    max_d = r['dry_density']
                    max_idx = i
            omc = results[max_idx]['moisture_percent'] if results else 0
            mdd = max_d
        
        return {
            'success': True,
            'results': {
                'mold_volume_cm3': volume,
                'points': results,
                'mdd': round(mdd, 3),  # Maximum Dry Density (g/cm³)
                'omc': round(omc, 2),  # Optimum Moisture Content (%)
                'equation': {
                    'a': round(float(coeffs[0]), 6) if len(results) >= 3 else 0,
                    'b': round(float(coeffs[1]), 4) if len(results) >= 3 else 0,
                    'c': round(float(coeffs[2]), 4) if len(results) >= 3 else 0
                }
            }
        }
        
    except Exception as e:
        return {'error': str(e)}
