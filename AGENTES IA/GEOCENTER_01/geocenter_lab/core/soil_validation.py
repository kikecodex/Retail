"""
Soil Parameter Validation Module
Based on CARTILLA DE PROMEDIOS POR TIPO DE SUELO - GEOCENTER

Validates test results against expected ranges for each SUCS soil type.
"""

# Parameter ranges extracted from CARTILLA DE PROMEDIOS
# Format: (min, max) or None if not applicable
# Units: φ in degrees, c in kg/cm², LL/LP/IP in %, γ in g/cm³

SOIL_PARAMETERS = {
    # ============== GRAVAS ==============
    'GW': {
        'name': 'Grava bien Graduada',
        'category': 'GRAVA',
        'finos_percent': (0, 5),
        'cu': (4, None),  # Cu ≥ 4
        'cc': (1, 3),     # 1 ≤ Cc ≤ 3
        'll': None,
        'lp': None,
        'ip': None,
        'peso_especifico': (2.65, 2.75),
        'gamma_seco': (1.75, 2.05),
        'gamma_compacta': (1.9, 2.35),
        'humedad': (3, 10),
        'phi': (38, 45),
        'cohesion': (0, 0),
        'qa_range': (4, 6)  # kg/cm²
    },
    'GP': {
        'name': 'Grava mal Graduada',
        'category': 'GRAVA',
        'finos_percent': (0, 5),
        'cu': (None, 4),  # Cu < 4
        'll': None,
        'lp': None,
        'ip': None,
        'peso_especifico': (2.65, 2.73),
        'gamma_seco': (1.65, 1.9),
        'gamma_compacta': (1.75, 2.02),
        'humedad': (3, 10),
        'phi': (30, 38),
        'cohesion': (0, 0),
    },
    'GM': {
        'name': 'Grava Limosa',
        'category': 'GRAVA',
        'finos_percent': (8, 15),
        'cu': (30, 300),
        'll': (20, 35),
        'lp': (17, 25),
        'ip': (0, 4),
        'peso_especifico': (2.65, 2.72),
        'gamma_seco': (1.5, 1.95),
        'gamma_compacta': (1.8, 2.35),
        'humedad': (6, 18),
        'phi': (32, 40),
        'cohesion': (0.05, 0.2),
    },
    'GC': {
        'name': 'Grava Arcillosa',
        'category': 'GRAVA',
        'finos_percent': (20, 40),
        'cu': (100, 1000),
        'll': (20, 40),
        'lp': (15, 20),
        'ip': (7, 20),
        'peso_especifico': (2.66, 2.74),
        'gamma_seco': (1.59, 2),
        'gamma_compacta': (1.75, 2.12),
        'humedad': (10, 18),
        'phi': (28, 35),
        'cohesion': (0.2, 0.5),
    },
    
    # ============== ARENAS ==============
    'SW': {
        'name': 'Arena bien Graduada',
        'category': 'ARENA',
        'finos_percent': (0, 5),
        'cu': (6, None),  # Cu ≥ 6
        'cc': (1, 3),
        'll': None,
        'lp': None,
        'ip': None,
        'peso_especifico': (2.63, 2.70),
        'gamma_seco': (1.6, 2),
        'gamma_compacta': (1.75, 2.25),
        'humedad': (5, 15),
        'phi': (33, 40),
        'cohesion': (0, 0.05),
    },
    'SP': {
        'name': 'Arena mal Graduada',
        'category': 'ARENA',
        'finos_percent': (0, 5),
        'cu': (1.2, 3),
        'll': None,
        'lp': None,
        'ip': None,
        'peso_especifico': (2.63, 2.68),
        'gamma_seco': (1.5, 1.9),
        'gamma_compacta': (1.63, 2.05),
        'humedad': (5, 15),
        'phi': (28, 35),
        'cohesion': (0, 0),
    },
    'SM': {
        'name': 'Arena Limosa',
        'category': 'ARENA',
        'finos_percent': (20, 40),
        'cu': (30, 500),
        'll': (20, 35),
        'lp': (18, 28),
        'ip': (4, 10),
        'peso_especifico': (2.64, 2.70),
        'gamma_seco': (1.35, 1.4),
        'gamma_compacta': (1.41, 1.65),
        'humedad': (10, 25),
        'phi': (24, 28),
        'cohesion': (0.2, 0.44),
    },
    'SC': {
        'name': 'Arena Arcillosa',
        'category': 'ARENA',
        'finos_percent': (20, 40),
        'cu': (30, 500),
        'll': (20, 35),
        'lp': (18, 27),
        'ip': (7, 18),
        'peso_especifico': (2.65, 2.72),
        'gamma_seco': (1.35, 1.45),
        'gamma_compacta': (1.41, 1.65),
        'humedad': (10, 22),
        'phi': (24, 28),
        'cohesion': (0.2, 0.44),
    },
    
    # ============== LIMOS Y ARCILLAS (LL < 50) ==============
    'ML': {
        'name': 'Limo',
        'category': 'FINOS',
        'finos_percent': (50, 100),
        'cu': (5, 50),
        'll': (25, 35),
        'lp': (21, 28),
        'ip': (4, 11),
        'peso_especifico': (2.65, 2.72),
        'gamma_seco': (1.35, 1.4),
        'gamma_compacta': (1.41, 1.65),
        'humedad': (15, 28),
        'phi': (24, 28),
        'cohesion': (0.01, 0.1),
    },
    'CL': {
        'name': 'Arcilla de Baja Plasticidad',
        'category': 'FINOS',
        'finos_percent': (80, 100),
        'cu': (6, 20),
        'll': (25, 35),
        'lp': (10, 22),
        'ip': (7, 16),
        'peso_especifico': (2.68, 2.78),
        'gamma_seco': (1.44, 1.92),
        'gamma_compacta': (1.93, 2.2),
        'humedad': (14, 28),
        'phi': (20, 28),
        'cohesion': (0.15, 0.19),
    },
    'OL': {
        'name': 'Arcilla o Limo Orgánico',
        'category': 'FINOS',
        'finos_percent': (80, 100),
        'cu': (5, 30),
        'll': (45, 70),
        'lp': (30, 45),
        'ip': (10, 30),
        'peso_especifico': (2.40, 2.65),
        'humedad': (26, 60),
        'phi': (15, 20),
        'cohesion': (0.02, 0.05),
    },
    
    # ============== LIMOS Y ARCILLAS (LL ≥ 50) ==============
    'MH': {
        'name': 'Limo Elástico',
        'category': 'FINOS',
        'finos_percent': (80, 100),
        'cu': (5, 50),
        'll': (35, 60),
        'lp': (22, 25),
        'ip': (7, 25),
        'peso_especifico': (2.65, 2.75),
        'humedad': (20, 35),
        'phi': (22, 29),
        'cohesion': (0.007, 0.02),
    },
    'CH': {
        'name': 'Arcilla de Alta Plasticidad',
        'category': 'FINOS',
        'finos_percent': (100, 100),
        'cu': (5, 40),
        'll': (60, 85),
        'lp': (20, 35),
        'ip': (33, 55),
        'peso_especifico': (2.70, 2.80),
        'humedad': (20, 55),
        'phi': (6, 15),
        'cohesion': (0.03, 0.1),
    },
    'OH': {
        'name': 'Arcilla o Limo Orgánico (Alta LL)',
        'category': 'FINOS',
        'finos_percent': (80, 100),
        'cu': (5, 30),
        'll': (45, 70),
        'lp': (30, 45),
        'ip': (10, 30),
        'peso_especifico': (2.40, 2.65),
        'humedad': (26, 60),
        'phi': (15, 22),
        'cohesion': (0.02, 0.05),
    },
    'PT': {
        'name': 'Turba',
        'category': 'ORGANICO',
        'finos_percent': (100, 100),
        'll': (100, 250),
        'lp': (30, 80),
        'ip': (50, 170),
        'peso_especifico': (1.50, 2.20),
        'humedad': (80, 800),
        'phi': (24, 30),
        'cohesion': (0.008, 0.025),
    },
}


def validate_parameter(value, range_tuple, param_name):
    """
    Validate a single parameter against expected range.
    Returns: (status, message)
    status: 'ok', 'warning', 'error'
    """
    if range_tuple is None:
        return ('ok', f'{param_name}: No aplica para este tipo de suelo')
    
    if value is None:
        return ('warning', f'{param_name}: Valor no disponible')
    
    min_val, max_val = range_tuple
    
    if min_val is not None and max_val is not None:
        if min_val <= value <= max_val:
            return ('ok', f'{param_name}: {value} ✓ (rango esperado: {min_val} - {max_val})')
        
        # Check if slightly outside (within 10%)
        range_size = max_val - min_val
        tolerance = range_size * 0.15  # 15% tolerance
        
        if (min_val - tolerance) <= value <= (max_val + tolerance):
            return ('warning', f'{param_name}: {value} ⚠️ ligeramente fuera (esperado: {min_val} - {max_val})')
        else:
            return ('error', f'{param_name}: {value} ❌ fuera del rango (esperado: {min_val} - {max_val})')
    
    elif min_val is not None:
        if value >= min_val:
            return ('ok', f'{param_name}: {value} ✓ (mínimo esperado: {min_val})')
        else:
            return ('error', f'{param_name}: {value} ❌ menor al mínimo ({min_val})')
    
    elif max_val is not None:
        if value <= max_val:
            return ('ok', f'{param_name}: {value} ✓ (máximo esperado: {max_val})')
        else:
            return ('error', f'{param_name}: {value} ❌ mayor al máximo ({max_val})')
    
    return ('ok', f'{param_name}: {value}')


def validate_soil_parameters(sucs_symbol, params):
    """
    Validate all parameters for a given soil type.
    
    Args:
        sucs_symbol: SUCS classification (e.g., 'SM', 'CL')
        params: dict with keys like 'phi', 'cohesion', 'll', 'lp', 'ip', etc.
    
    Returns:
        dict with 'valid', 'warnings', 'errors', 'details'
    """
    if sucs_symbol not in SOIL_PARAMETERS:
        return {
            'valid': False,
            'error': f'Tipo de suelo "{sucs_symbol}" no encontrado en la cartilla',
            'warnings': [],
            'errors': [],
            'details': []
        }
    
    soil_info = SOIL_PARAMETERS[sucs_symbol]
    results = []
    warnings = []
    errors = []
    
    # Map input params to soil parameter keys
    param_map = {
        'phi': ('phi', 'Ángulo de fricción φ'),
        'friction_angle': ('phi', 'Ángulo de fricción φ'),
        'cohesion': ('cohesion', 'Cohesión c'),
        'c': ('cohesion', 'Cohesión c'),
        'll': ('ll', 'Límite Líquido LL'),
        'lp': ('lp', 'Límite Plástico LP'),
        'ip': ('ip', 'Índice de Plasticidad IP'),
        'pi': ('ip', 'Índice de Plasticidad IP'),
        'gamma': ('gamma_seco', 'Peso unitario γ'),
        'unit_weight': ('gamma_seco', 'Peso unitario γ'),
        'humidity': ('humedad', 'Humedad'),
        'moisture': ('humedad', 'Humedad'),
        'pe': ('peso_especifico', 'Peso Específico'),
        'gs': ('peso_especifico', 'Peso Específico'),
    }
    
    for param_key, value in params.items():
        if param_key in param_map:
            soil_key, display_name = param_map[param_key]
            if soil_key in soil_info:
                status, message = validate_parameter(value, soil_info[soil_key], display_name)
                results.append({
                    'param': display_name,
                    'value': value,
                    'status': status,
                    'message': message
                })
                if status == 'warning':
                    warnings.append(message)
                elif status == 'error':
                    errors.append(message)
    
    return {
        'valid': len(errors) == 0,
        'soil_type': sucs_symbol,
        'soil_name': soil_info['name'],
        'category': soil_info['category'],
        'warnings': warnings,
        'errors': errors,
        'details': results,
        'expected_ranges': {
            'phi': soil_info.get('phi'),
            'cohesion': soil_info.get('cohesion'),
            'll': soil_info.get('ll'),
            'lp': soil_info.get('lp'),
            'ip': soil_info.get('ip'),
        }
    }


def get_soil_info(sucs_symbol):
    """Get expected parameters for a soil type."""
    if sucs_symbol in SOIL_PARAMETERS:
        return SOIL_PARAMETERS[sucs_symbol]
    return None
