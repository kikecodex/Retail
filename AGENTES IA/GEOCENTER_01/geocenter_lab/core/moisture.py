def calculate_moisture(data):
    """
    Calculates Water Content (Contenido de Humedad).
    
    Expected Data: List of samples
    [
        {'wet_tare': 120.3, 'dry_tare': 110.1, 'tare': 10.1},
        ...
    ]
    """
    try:
        samples = data.get('samples', [])
        results = []
        total_w = 0
        valid_count = 0

        for s in samples:
            wt = float(s.get('wet_tare', 0))
            dt = float(s.get('dry_tare', 0))
            t = float(s.get('tare', 0))
            
            w_percent = 0
            
            if wt > dt > t:
                water = wt - dt
                solid = dt - t
                if solid > 0:
                    w_percent = (water / solid) * 100
                    total_w += w_percent
                    valid_count += 1
            
            results.append({
                'wet_tare': wt,
                'dry_tare': dt,
                'tare': t,
                'w_percent': round(w_percent, 2)
            })
            
        average_w = round(total_w / valid_count, 2) if valid_count > 0 else 0

        return {
            'success': True,
            'results': {
                'average': average_w,
                'samples': results
            }
        }

    except Exception as e:
        return {'error': str(e)}
