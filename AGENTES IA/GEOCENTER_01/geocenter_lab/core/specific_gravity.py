
def calculate_specific_gravity(data):
    """
    Calculates Specific Gravity for soil samples.
    Gs = Mo / (Mo + (Ma - Mb))
    
    Ma = Mass of pycnometer + water
    Mb = Mass of pycnometer + water + soil
    Mo = Mass of oven-dry soil
    """
    try:
        samples = []
        gs_values = []
        
        for s in data.get('samples', []):
            ma = s.get('ma', 0)
            mb = s.get('mb', 0)
            mo = s.get('mo', 0)
            
            # Gs = Mo / (Mo + Ma - Mb)
            denom = mo + ma - mb
            gs = 0
            if denom != 0:
                gs = mo / denom
                
            s_res = s.copy()
            s_res['gs'] = round(gs, 2)
            samples.append(s_res)
            
            if gs > 0:
                gs_values.append(gs)
                
        avg_gs = sum(gs_values) / len(gs_values) if gs_values else 0
        
        return {
            'success': True,
            'results': {
                'samples': samples,
                'average_gs': round(avg_gs, 2)
            }
        }
    except Exception as e:
        return {'error': str(e)}
