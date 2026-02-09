import numpy as np

def calculate_limits(data):
    """
    Calculates Liquid Limit (LL), Plastic Limit (PL), and Plasticity Index (PI).
    
    Expected Data:
    {
        'll_data': [
            {'blows': 15, 'wet_tare': 45.2, 'dry_tare': 40.1, 'tare': 20.0},
            ...
        ],
        'pl_data': [
            {'wet_tare': 30.1, 'dry_tare': 28.5, 'tare': 20.0},
            ...
        ]
    }
    """
    try:
        # 2. Calculate Liquid Limit (LL)
        ll_points = []
        blows = []
        moistures = []

        for p in data.get('ll_data', []):
            b = p.get('blows', 0)
            wt, dt, t = p.get('wet_tare', 0), p.get('dry_tare', 0), p.get('tare', 0)
            
            p_res = p.copy()
            if b > 0 and wt > dt > t > 0:
                water = wt - dt
                solid = dt - t
                wc = (water / solid) * 100
                
                blows.append(b)
                moistures.append(wc)
                p_res['moisture'] = round(wc, 2)
                ll_points.append(p_res)
            else:
                p_res['moisture'] = 0
                ll_points.append(p_res)

        # 1. Calculate Plastic Limit (PL) (Moved after to match structure if needed, but keeping order ok)
        pl_points_raw = []
        pl_values = []
        for p in data.get('pl_data', []):
            wt, dt, t = p.get('wet_tare', 0), p.get('dry_tare', 0), p.get('tare', 0)
            p_res = p.copy()
            if wt > dt > t > 0:
                water = wt - dt
                solid = dt - t
                wc = (water / solid) * 100
                pl_values.append(wc)
                p_res['moisture'] = round(wc, 2)
            else:
                 p_res['moisture'] = 0
            pl_points_raw.append(p_res)
        
        pl = round(sum(pl_values) / len(pl_values), 2) if pl_values else 0

        # ... Regression Logic ...
        ll = 0
        slope, intercept = 0, 0
        if len(blows) >= 2:
            x_log = np.log10(blows)
            y = np.array(moistures)
            slope, intercept = np.polyfit(x_log, y, 1)
            # Excel uses ln(x) in equation display sometimes but standard soil mech uses log10 or semilog.
            # User image: y = -3.137ln(x) + 48.238. ln is natural log.
            # If user wants EXACT equation match, I should use np.log (ln).
            # Let's check: -3.137 * ln(25) + 48.238 = -3.137 * 3.218 + 48.238 = -10.09 + 48.238 = 38.14.
            # MATCHES! So I must use np.log (natural log), NOT log10.
            
            x_ln = np.log(blows)
            slope, intercept = np.polyfit(x_ln, y, 1)
            
            ll_val = slope * np.log(25) + intercept
            ll = round(ll_val, 2)
            
        elif len(blows) == 1:
             ll_val = moistures[0] * (blows[0]/25)**0.121
             ll = round(ll_val, 2)

        # 3. Plasticity Index
        pi = round(ll - pl, 2) if ll > 0 and pl > 0 else 0
        if pi < 0: pi = 0 

        return {
            'success': True,
            'results': {
                'LL': ll,
                'PL': pl,
                'PI': pi,
                'll_points': ll_points, 
                'll_data_raw': ll_points, # Alias for consistency
                'pl_data_raw': pl_points_raw,
                'equation': {'slope': slope, 'intercept': intercept} if len(blows) >=2 else None
            }
        }

    except Exception as e:
        return {'error': str(e)}
