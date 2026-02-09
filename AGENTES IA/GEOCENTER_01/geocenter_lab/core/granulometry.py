import pandas as pd

import math

def interpolate_d_value(percent, sieves_sorted):
    """
    Finds the Diameter (mm) corresponding to a specific Percent Passing (percent)
    using Log-Linear interpolation.
    sieves_sorted: List of dicts [{'opening_mm': float, 'percent_passing': float}, ...]
                   sorted by opening_mm descending (usually).
    """
    # Filter only sieves with data
    points = [s for s in sieves_sorted if s['percent_passing'] is not None]
    
    # Sort by opening_mm descending (standard sieve Analysis: bigger holes first)
    points.sort(key=lambda x: x['opening_mm'], reverse=True)
    
    # Check boundaries
    if not points: return None
    if percent >= points[0]['percent_passing']: return points[0]['opening_mm'] # Exceeds max
    if percent <= points[-1]['percent_passing']: return points[-1]['opening_mm'] # Below min
    
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        
        # We look for the interval where percent lies
        if p1['percent_passing'] >= percent >= p2['percent_passing']:
            # Log-Linear Interpolation
            # log(D) = log(D1) + (P - P1) * (log(D2) - log(D1)) / (P2 - P1)
            # Y = log(D), X = P
            
            d1 = p1['opening_mm']
            d2 = p2['opening_mm']
            pct1 = p1['percent_passing']
            pct2 = p2['percent_passing']
            
            if pct1 == pct2: return d1
            
            log_d = math.log10(d1) + (percent - pct1) * (math.log10(d2) - math.log10(d1)) / (pct2 - pct1)
            return 10 ** log_d
            
    return None

def classify_sucs_from_granulometry(gravel_pct, sand_pct, fines_pct, cu, cc, has_d10):
    """
    Classifies soil according to ASTM D2487 (SUCS) based on granulometry data.
    
    Returns dict with:
      - symbol: SUCS symbol (e.g., 'GW', 'SP', 'ML-CL')
      - name: Full name in Spanish
      - description: Detailed description
      - needs_limits: Whether LL/PL are needed for full classification
    """
    gravel_pct = max(0, gravel_pct)
    sand_pct = max(0, sand_pct)
    fines_pct = max(0, fines_pct)
    
    # Step 1: Is it COARSE-GRAINED (>50% retained on #200) or FINE-GRAINED?
    coarse_pct = gravel_pct + sand_pct
    
    if fines_pct >= 50:
        # FINE-GRAINED SOIL — needs LL/PL for full classification
        return {
            'symbol': 'ML / CL',
            'name': 'Suelo Fino (Limo o Arcilla)',
            'description': f'Suelo de grano fino ({fines_pct:.1f}% pasa el tamiz #200). Se requieren Límites de Atterberg (LL, LP) para clasificación completa.',
            'needs_limits': True,
            'group': 'FINOS',
            'fines_pct': round(fines_pct, 1)
        }
    
    # COARSE-GRAINED SOIL
    # Step 2: Is it GRAVEL or SAND?
    is_gravel = gravel_pct > sand_pct
    
    if is_gravel:
        # GRAVEL group
        if fines_pct <= 5:
            # Clean gravel — classify by Cu and Cc
            if has_d10 and cu > 0 and cc > 0:
                if cu >= 4 and 1 <= cc <= 3:
                    return {
                        'symbol': 'GW',
                        'name': 'Grava Bien Graduada',
                        'description': f'Grava limpia bien graduada. Grava={gravel_pct:.1f}%, Arena={sand_pct:.1f}%, Finos={fines_pct:.1f}%. Cu={cu}, Cc={cc}.',
                        'needs_limits': False,
                        'group': 'GRAVA',
                        'fines_pct': round(fines_pct, 1)
                    }
                else:
                    return {
                        'symbol': 'GP',
                        'name': 'Grava Mal Graduada',
                        'description': f'Grava limpia mal graduada. Grava={gravel_pct:.1f}%, Arena={sand_pct:.1f}%, Finos={fines_pct:.1f}%. Cu={cu}, Cc={cc}. (Requiere Cu≥4 y 1≤Cc≤3 para GW)',
                        'needs_limits': False,
                        'group': 'GRAVA',
                        'fines_pct': round(fines_pct, 1)
                    }
            else:
                return {
                    'symbol': 'GP',
                    'name': 'Grava Mal Graduada',
                    'description': f'Grava limpia (finos={fines_pct:.1f}%). No se pudo calcular Cu/Cc. Clasificada como GP por defecto.',
                    'needs_limits': False,
                    'group': 'GRAVA',
                    'fines_pct': round(fines_pct, 1)
                }
        elif fines_pct <= 12:
            # Borderline — dual classification
            return {
                'symbol': 'GW-GM / GP-GC',
                'name': 'Grava con Finos (Caso Límite)',
                'description': f'Grava con finos entre 5-12% ({fines_pct:.1f}%). Se requieren Límites de Atterberg para clasificación definitiva (GM vs GC).',
                'needs_limits': True,
                'group': 'GRAVA',
                'fines_pct': round(fines_pct, 1)
            }
        else:
            # Gravel with fines > 12% — needs LL/PL
            return {
                'symbol': 'GM / GC',
                'name': 'Grava Limosa o Arcillosa',
                'description': f'Grava con finos significativos ({fines_pct:.1f}%). Grava={gravel_pct:.1f}%, Arena={sand_pct:.1f}%. Se requieren Límites de Atterberg: IP<4 → GM (limosa), IP≥7 → GC (arcillosa).',
                'needs_limits': True,
                'group': 'GRAVA',
                'fines_pct': round(fines_pct, 1)
            }
    else:
        # SAND group
        if fines_pct <= 5:
            # Clean sand
            if has_d10 and cu > 0 and cc > 0:
                if cu >= 6 and 1 <= cc <= 3:
                    return {
                        'symbol': 'SW',
                        'name': 'Arena Bien Graduada',
                        'description': f'Arena limpia bien graduada. Arena={sand_pct:.1f}%, Grava={gravel_pct:.1f}%, Finos={fines_pct:.1f}%. Cu={cu}, Cc={cc}.',
                        'needs_limits': False,
                        'group': 'ARENA',
                        'fines_pct': round(fines_pct, 1)
                    }
                else:
                    return {
                        'symbol': 'SP',
                        'name': 'Arena Mal Graduada',
                        'description': f'Arena limpia mal graduada. Arena={sand_pct:.1f}%, Grava={gravel_pct:.1f}%, Finos={fines_pct:.1f}%. Cu={cu}, Cc={cc}. (Requiere Cu≥6 y 1≤Cc≤3 para SW)',
                        'needs_limits': False,
                        'group': 'ARENA',
                        'fines_pct': round(fines_pct, 1)
                    }
            else:
                return {
                    'symbol': 'SP',
                    'name': 'Arena Mal Graduada',
                    'description': f'Arena limpia (finos={fines_pct:.1f}%). No se pudo calcular Cu/Cc. Clasificada como SP por defecto.',
                    'needs_limits': False,
                    'group': 'ARENA',
                    'fines_pct': round(fines_pct, 1)
                }
        elif fines_pct <= 12:
            return {
                'symbol': 'SW-SM / SP-SC',
                'name': 'Arena con Finos (Caso Límite)',
                'description': f'Arena con finos entre 5-12% ({fines_pct:.1f}%). Se requieren Límites de Atterberg para definir si es limosa (SM) o arcillosa (SC).',
                'needs_limits': True,
                'group': 'ARENA',
                'fines_pct': round(fines_pct, 1)
            }
        else:
            return {
                'symbol': 'SM / SC',
                'name': 'Arena Limosa o Arcillosa',
                'description': f'Arena con finos significativos ({fines_pct:.1f}%). Arena={sand_pct:.1f}%, Grava={gravel_pct:.1f}%. Se requieren Límites de Atterberg: IP<4 → SM (limosa), IP≥7 → SC (arcillosa).',
                'needs_limits': True,
                'group': 'ARENA',
                'fines_pct': round(fines_pct, 1)
            }

def calculate_granulometry(data):
    try:
        total_dry_weight = float(data.get('total_dry_weight', 0))
        user_sieves = data.get('sieves', [])
        
        results = []
        
        # Standard ASTM Sieve Sizes needed for classification breakdown
        # We'll map User Inputs to these boundaries roughly or strictly
        # 3" (75mm), 3/4" (19mm), #4 (4.75mm), #10 (2.00mm), #40 (0.425mm), #200 (0.075mm)
        
        passing_map = {} # map opening_mm -> %passing

        for s in user_sieves:
            label = s.get('size_label', '')
            opening = float(s.get('opening_mm', 0))
            retained = float(s.get('weight_retained', 0))
            
            percent_retained = 0
            if total_dry_weight > 0:
                percent_retained = (retained / total_dry_weight) * 100
                
            # We calculate cumulative "on the fly" here, but usually it's ordered.
            # Let's assume input is ordered or we do a global cumulative sum after sorting?
            # Better: recalculate all cumulatives linearly.
            
            results.append({
                'size_label': label,
                'opening_mm': opening,
                'weight_retained': retained,
                'percent_retained': round(percent_retained, 2),
                'cumulative_retained': 0, # Placeholder
                'percent_passing': 0 # Placeholder
            })

        # Sort by size descending
        results.sort(key=lambda x: x['opening_mm'], reverse=True)
        
        # Validate total weight
        if total_dry_weight <= 0:
            total_dry_weight = sum(r['weight_retained'] for r in results)
            if total_dry_weight <= 0:
                return {'error': 'El peso total de la muestra debe ser mayor a 0', 'data': [], 'metrics': None}
        
        cumulative = 0
        for i, item in enumerate(results):
            cumulative += item['weight_retained']
            item['cumulative_retained'] = round((cumulative / total_dry_weight) * 100, 2)
            item['percent_passing'] = round(100 - item['cumulative_retained'], 2)
            passing_map[item['opening_mm']] = item['percent_passing']

        # Add Pan (0, 0) for interpolation if not present
        if results[-1]['percent_passing'] > 0:
            results.append({
                'size_label': 'Fondo',
                'opening_mm': 0.0,
                'weight_retained': 0,
                'percent_retained': 0,
                'cumulative_retained': 100,
                'percent_passing': 0.0
            })
            passing_map[0.0] = 0.0

        # --- CALCULATE METRICS (D10, D30, D60) ---
        # Using Log-Linear Interpolation (Standard for Soil)
        def interpolate_d(target_p, sieves):
            # Sort desc
            points = [s for s in sieves if s['percent_passing'] is not None and s['opening_mm'] > 0]
            if not points: return None
            
            # Check range
            if target_p > points[0]['percent_passing']: return None # Above max
            if target_p < points[-1]['percent_passing']: return None # Below min (in fines < #200)

            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1] # Large D, Small D
                pct1, pct2 = p1['percent_passing'], p2['percent_passing']
                d1, d2 = p1['opening_mm'], p2['opening_mm']
                
                if pct1 >= target_p >= pct2:
                    if pct1 == pct2: return d1
                    # Log-linear: log(D) = log(D1) + (P - P1)/(P2 - P1) * (log(D2)-log(D1))
                    val_log = math.log10(d1) + (target_p - pct1) / (pct2 - pct1) * (math.log10(d2) - math.log10(d1))
                    return 10 ** val_log
            return None

        d10 = interpolate_d(10, results)
        d30 = interpolate_d(30, results)
        d60 = interpolate_d(60, results)
        
        # Guard: If D10 is None (because P200 > 10%), Cu/Cc are invalid
        cu, cc = 0, 0
        if d10 and d30 and d60:
            cu = round(d60 / d10, 2)
            cc = round((d30 ** 2) / (d60 * d10), 2)
            d10, d30, d60 = round(d10, 3), round(d30, 3), round(d60, 3)
        else:
            # Check if we should return "-" or 0. Backend returns numbers usually.
            # Let's return None or 0 and handle presentation in Frontend?
            # Keeping 0/None for now.
            pass

        # --- FRACTION BREAKDOWN (ASTM D2487) ---
        # Gravel: > 4.75mm (#4)
        # Sand: 4.75mm (#4) to 0.075mm (#200)
        #   Coarse: 4.75 (#4) to 2.00 (#10)
        #   Medium: 2.00 (#10) to 0.425 (#40)
        #   Fine:   0.425 (#40) to 0.075 (#200)
        # Fines: < 0.075mm (#200)
        
        def get_pass_log(mm):
            if mm in passing_map: return passing_map[mm]
            # Log Linear Interp P from D
            points = [s for s in results if s['opening_mm'] > 0]
            # Handle max
            if mm >= points[0]['opening_mm']: return 100
            # Handle min (if below last sieve, assume linear to 0 or flat? Log linear to 0 is impossible)
            if mm <= points[-1]['opening_mm']: 
                # Linear from last point to (0,0) is best fallback
                last = points[-1]
                return (mm / last['opening_mm']) * last['percent_passing']
            
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i+1] # Large D, Small D
                d1, d2 = p1['opening_mm'], p2['opening_mm']
                pct1, pct2 = p1['percent_passing'], p2['percent_passing']
                
                if d1 >= mm >= d2:
                    # P = P1 + (logD - logD1)/(logD2 - logD1) * (P2 - P1)
                    ratio = (math.log10(mm) - math.log10(d1)) / (math.log10(d2) - math.log10(d1))
                    return pct1 + ratio * (pct2 - pct1)
            return 0

        p_4 = get_pass_log(4.75)
        p_200 = get_pass_log(0.075)
        p_10 = get_pass_log(2.00)
        p_40 = get_pass_log(0.425)
        p_34inch = get_pass_log(19.0)

        # Logic
        # GRAVA
        gravel_total = 100 - p_4
        gravel_coarse = 100 - p_34inch # > 3/4"
        gravel_fine = p_34inch - p_4   # 3/4" to #4
        
        # ARENA
        sand_total = p_4 - p_200
        # Coarse: #4 to #10
        sand_coarse = p_4 - p_10 
        # Medium: #10 to #40
        sand_medium = p_10 - p_40
        # Fine: #40 to #200
        sand_fine = p_40 - p_200
        
        fines = p_200

        metrics = {
            'd10': round(d10, 4) if d10 else '--',
            'd30': round(d30, 4) if d30 else '--',
            'd60': round(d60, 4) if d60 else '--',
            'cu': cu if d10 else '--',
            'cc': cc if d10 else '--',
            'fractions': {
                'gravel': {
                    'total': round(gravel_total, 2),
                    'coarse': round(gravel_coarse, 2),
                    'fine': round(gravel_fine, 2)
                },
                'sand': {
                    'total': round(sand_total, 2),
                    'coarse': round(sand_coarse, 2),
                    'medium': round(sand_medium, 2),
                    'fine': round(sand_fine, 2)
                },
                'fines': round(fines, 2)
            }
        }
        
        # --- CLASIFICACIÓN SUCS (ASTM D2487) ---
        classification = classify_sucs_from_granulometry(
            gravel_total, sand_total, fines, cu, cc, d10 is not None
        )
        metrics['classification'] = classification
        
        return {
            'success': True,
            'data': [r for r in results if r['size_label'] != 'Fondo'], 
            'metrics': metrics
        }
    except Exception as e:
        return {'error': str(e)}

def get_percent_passing_at(target_mm, sieves_sorted):
    """
    Interpolate % Passing for a specific diameter (target_mm).
    Sieves sorted Descending (Large -> Small).
    """
    if not sieves_sorted: return 0
    
    # Handle out of bounds
    if target_mm >= sieves_sorted[0]['opening_mm']: return sieves_sorted[0]['percent_passing'] # Close enough
    if target_mm <= sieves_sorted[-1]['opening_mm']: return sieves_sorted[-1]['percent_passing']
    
    for i in range(len(sieves_sorted) - 1):
        s1 = sieves_sorted[i]
        s2 = sieves_sorted[i+1]
        
        # Check if target is between s1 and s2
        if s1['opening_mm'] >= target_mm >= s2['opening_mm']:
            d1 = s1['opening_mm']
            d2 = s2['opening_mm']
            p1 = s1['percent_passing']
            p2 = s2['percent_passing']
            
            if d1 == d2: return p1
            
            # Linear Log Interpolation for P vs log(D)
            # P = P1 + (log(D) - log(D1)) * (P2 - P1) / (log(D2) - log(D1))
            
            val = p1 + (math.log10(target_mm) - math.log10(d1)) * (p2 - p1) / (math.log10(d2) - math.log10(d1))
            return val
            
    return 0
