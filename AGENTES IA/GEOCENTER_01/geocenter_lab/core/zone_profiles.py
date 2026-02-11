"""
GEOCENTER LAB — Perfiles Regionales de Suelo (Perú)
Costa / Sierra / Selva × SUCS

Cada perfil contiene rangos (min, max) diferenciados por la geología,
clima y condiciones típicas de cada región del Perú.

Fuentes:
- CARTILLA GEOCENTER (parámetros nacionales)
- Bowles (Foundation Analysis & Design)
- NTE E.050 (Suelos y Cimentaciones)
- Experiencia de laboratorios regionales
- Datos verificados Yunguyo (Sierra, Puno)
"""

ZONE_PROFILES = {
    # ================================================================
    #  COSTA — Clima árido, suelos arenosos/gravas bien graduadas,
    #  baja humedad, alta densidad, nivel freático profundo.
    #  Referencia: Lima, Ica, Arequipa-Costa, Tacna, Tumbes
    # ================================================================
    'COSTA': {
        'label': 'Costa',
        'emoji': '🏖️',
        'color': '#F59E0B',  # amber
        'description': 'Suelos áridos, arenosos, baja humedad, alta densidad',

        'GW': {
            'phi': (36, 42), 'cohesion': (0, 0),
            'humedad': (2, 6), 'peso_especifico': (2.68, 2.72),
            'mdd': (1.80, 2.10), 'omc': (6, 10),
            'll': None, 'lp': None, 'finos_percent': (0, 4),
        },
        'GP': {
            'phi': (33, 38), 'cohesion': (0, 0),
            'humedad': (2, 6), 'peso_especifico': (2.66, 2.70),
            'mdd': (1.65, 1.95), 'omc': (7, 11),
            'll': None, 'lp': None, 'finos_percent': (0, 4),
        },
        'GM': {
            'phi': (30, 36), 'cohesion': (0.05, 0.20),
            'humedad': (3, 8), 'peso_especifico': (2.67, 2.72),
            'mdd': (1.70, 2.05), 'omc': (7, 11),
            'll': (20, 28), 'lp': (17, 22), 'finos_percent': (8, 14),
        },
        'GC': {
            'phi': (28, 34), 'cohesion': (0.10, 0.35),
            'humedad': (4, 10), 'peso_especifico': (2.68, 2.72),
            'mdd': (1.70, 2.00), 'omc': (8, 13),
            'll': (22, 32), 'lp': (14, 20), 'finos_percent': (12, 15),
        },
        'SW': {
            'phi': (33, 38), 'cohesion': (0, 0),
            'humedad': (2, 6), 'peso_especifico': (2.66, 2.70),
            'mdd': (1.70, 1.92), 'omc': (8, 13),
            'll': None, 'lp': None, 'finos_percent': (0, 4),
        },
        'SP': {
            'phi': (30, 36), 'cohesion': (0, 0),
            'humedad': (2, 5), 'peso_especifico': (2.65, 2.68),
            'mdd': (1.55, 1.82), 'omc': (10, 15),
            'll': None, 'lp': None, 'finos_percent': (0, 4),
        },
        'SM': {
            'phi': (30, 36), 'cohesion': (0.01, 0.10),
            'humedad': (4, 8), 'peso_especifico': (2.66, 2.70),
            'mdd': (1.70, 1.85), 'omc': (8, 12),
            'll': (20, 28), 'lp': (18, 23), 'finos_percent': (15, 35),
        },
        'SC': {
            'phi': (28, 34), 'cohesion': (0.10, 0.30),
            'humedad': (5, 10), 'peso_especifico': (2.67, 2.72),
            'mdd': (1.65, 1.85), 'omc': (9, 14),
            'll': (22, 30), 'lp': (14, 20), 'finos_percent': (20, 38),
        },
        'ML': {
            'phi': (28, 34), 'cohesion': (0.01, 0.08),
            'humedad': (6, 12), 'peso_especifico': (2.65, 2.70),
            'mdd': (1.55, 1.80), 'omc': (12, 18),
            'll': (22, 35), 'lp': (18, 26), 'finos_percent': (55, 80),
        },
        'CL': {
            'phi': (20, 28), 'cohesion': (0.15, 0.45),
            'humedad': (8, 16), 'peso_especifico': (2.68, 2.74),
            'mdd': (1.55, 1.80), 'omc': (12, 18),
            'll': (22, 38), 'lp': (12, 20), 'finos_percent': (80, 100),
        },
        'MH': {
            'phi': (22, 30), 'cohesion': (0.02, 0.15),
            'humedad': (12, 25), 'peso_especifico': (2.55, 2.65),
            'mdd': (1.25, 1.55), 'omc': (20, 32),
            'll': (50, 65), 'lp': (35, 48), 'finos_percent': (85, 100),
        },
        'CH': {
            'phi': (14, 22), 'cohesion': (0.25, 0.60),
            'humedad': (15, 30), 'peso_especifico': (2.60, 2.70),
            'mdd': (1.35, 1.60), 'omc': (18, 28),
            'll': (50, 70), 'lp': (22, 32), 'finos_percent': (90, 100),
        },
    },

    # ================================================================
    #  SIERRA — Clima frío/templado, suelos glaciales/volcánicos,
    #  humedad moderada-alta, arcillas y limos comunes.
    #  Referencia: Puno (Yunguyo), Cusco, Junín, Huaraz, Cajamarca
    # ================================================================
    'SIERRA': {
        'label': 'Sierra',
        'emoji': '🏔️',
        'color': '#8B5CF6',  # violet
        'description': 'Suelos glaciales/volcánicos, humedad moderada, arcillas comunes',

        'GW': {
            'phi': (32, 38), 'cohesion': (0, 0.05),
            'humedad': (4, 10), 'peso_especifico': (2.65, 2.70),
            'mdd': (1.70, 2.00), 'omc': (8, 12),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'GP': {
            'phi': (30, 36), 'cohesion': (0, 0.05),
            'humedad': (4, 10), 'peso_especifico': (2.63, 2.68),
            'mdd': (1.60, 1.90), 'omc': (9, 13),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'GM': {
            'phi': (26, 33), 'cohesion': (0.15, 0.40),
            'humedad': (8, 16), 'peso_especifico': (2.63, 2.68),
            'mdd': (1.55, 1.90), 'omc': (10, 15),
            'll': (24, 35), 'lp': (18, 25), 'finos_percent': (8, 15),
        },
        'GC': {
            'phi': (24, 30), 'cohesion': (0.05, 0.50),
            'humedad': (4, 18), 'peso_especifico': (2.62, 2.70),
            'mdd': (1.55, 1.90), 'omc': (7, 15),
            'll': (26, 40), 'lp': (15, 25), 'finos_percent': (12, 15),
        },
        'SW': {
            'phi': (28, 34), 'cohesion': (0, 0.05),
            'humedad': (5, 10), 'peso_especifico': (2.64, 2.68),
            'mdd': (1.60, 1.82), 'omc': (10, 16),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'SP': {
            'phi': (26, 32), 'cohesion': (0, 0.05),
            'humedad': (5, 10), 'peso_especifico': (2.62, 2.66),
            'mdd': (1.50, 1.75), 'omc': (12, 18),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'SM': {
            'phi': (24, 30), 'cohesion': (0.15, 0.45),
            'humedad': (10, 18), 'peso_especifico': (2.60, 2.68),
            'mdd': (1.55, 1.75), 'omc': (11, 16),
            'll': (28, 40), 'lp': (20, 28), 'finos_percent': (18, 40),
        },
        'SC': {
            'phi': (22, 28), 'cohesion': (0.20, 0.50),
            'humedad': (12, 20), 'peso_especifico': (2.62, 2.70),
            'mdd': (1.50, 1.78), 'omc': (12, 18),
            'll': (28, 38), 'lp': (16, 24), 'finos_percent': (20, 40),
        },
        'ML': {
            'phi': (24, 32), 'cohesion': (0.02, 0.12),
            'humedad': (12, 22), 'peso_especifico': (2.60, 2.68),
            'mdd': (1.40, 1.70), 'omc': (15, 24),
            'll': (28, 45), 'lp': (22, 32), 'finos_percent': (55, 85),
        },
        'CL': {
            'phi': (16, 24), 'cohesion': (0.25, 0.60),
            'humedad': (14, 25), 'peso_especifico': (2.62, 2.72),
            'mdd': (1.45, 1.70), 'omc': (15, 22),
            'll': (28, 45), 'lp': (14, 22), 'finos_percent': (80, 100),
        },
        'MH': {
            'phi': (18, 26), 'cohesion': (0.05, 0.22),
            'humedad': (20, 38), 'peso_especifico': (2.50, 2.62),
            'mdd': (1.15, 1.48), 'omc': (24, 38),
            'll': (52, 72), 'lp': (36, 50), 'finos_percent': (85, 100),
        },
        'CH': {
            'phi': (10, 18), 'cohesion': (0.35, 0.80),
            'humedad': (22, 40), 'peso_especifico': (2.58, 2.68),
            'mdd': (1.25, 1.52), 'omc': (22, 32),
            'll': (55, 80), 'lp': (24, 35), 'finos_percent': (90, 100),
        },
    },

    # ================================================================
    #  SELVA — Clima tropical, suelos aluviales/orgánicos,
    #  alta humedad, NF superficial, arcillas plásticas.
    #  Referencia: Tarapoto, Iquitos, Pucallpa, Tingo María
    # ================================================================
    'SELVA': {
        'label': 'Selva',
        'emoji': '🌿',
        'color': '#10B981',  # emerald
        'description': 'Suelos aluviales/orgánicos, alta humedad, NF superficial',

        'GW': {
            'phi': (30, 36), 'cohesion': (0, 0.08),
            'humedad': (6, 14), 'peso_especifico': (2.62, 2.68),
            'mdd': (1.60, 1.90), 'omc': (10, 15),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'GP': {
            'phi': (28, 34), 'cohesion': (0, 0.08),
            'humedad': (6, 14), 'peso_especifico': (2.60, 2.66),
            'mdd': (1.55, 1.85), 'omc': (11, 16),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'GM': {
            'phi': (22, 30), 'cohesion': (0.15, 0.50),
            'humedad': (12, 22), 'peso_especifico': (2.58, 2.66),
            'mdd': (1.50, 1.80), 'omc': (13, 18),
            'll': (28, 42), 'lp': (20, 28), 'finos_percent': (8, 15),
        },
        'GC': {
            'phi': (20, 28), 'cohesion': (0.25, 0.60),
            'humedad': (14, 24), 'peso_especifico': (2.60, 2.68),
            'mdd': (1.50, 1.78), 'omc': (14, 20),
            'll': (30, 45), 'lp': (16, 25), 'finos_percent': (12, 15),
        },
        'SW': {
            'phi': (26, 32), 'cohesion': (0, 0.08),
            'humedad': (8, 15), 'peso_especifico': (2.60, 2.66),
            'mdd': (1.55, 1.78), 'omc': (12, 18),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'SP': {
            'phi': (24, 30), 'cohesion': (0, 0.08),
            'humedad': (8, 15), 'peso_especifico': (2.58, 2.64),
            'mdd': (1.45, 1.70), 'omc': (14, 20),
            'll': None, 'lp': None, 'finos_percent': (0, 5),
        },
        'SM': {
            'phi': (18, 25), 'cohesion': (0.20, 0.60),
            'humedad': (18, 30), 'peso_especifico': (2.55, 2.65),
            'mdd': (1.45, 1.65), 'omc': (15, 22),
            'll': (32, 48), 'lp': (22, 32), 'finos_percent': (20, 45),
        },
        'SC': {
            'phi': (16, 24), 'cohesion': (0.25, 0.65),
            'humedad': (18, 30), 'peso_especifico': (2.58, 2.68),
            'mdd': (1.45, 1.68), 'omc': (15, 22),
            'll': (35, 48), 'lp': (18, 27), 'finos_percent': (22, 42),
        },
        'ML': {
            'phi': (20, 28), 'cohesion': (0.03, 0.15),
            'humedad': (20, 35), 'peso_especifico': (2.55, 2.65),
            'mdd': (1.30, 1.60), 'omc': (18, 28),
            'll': (35, 52), 'lp': (25, 38), 'finos_percent': (60, 90),
        },
        'CL': {
            'phi': (12, 20), 'cohesion': (0.30, 0.75),
            'humedad': (22, 38), 'peso_especifico': (2.58, 2.70),
            'mdd': (1.35, 1.60), 'omc': (18, 26),
            'll': (35, 50), 'lp': (16, 25), 'finos_percent': (85, 100),
        },
        'MH': {
            'phi': (14, 22), 'cohesion': (0.08, 0.28),
            'humedad': (28, 50), 'peso_especifico': (2.45, 2.58),
            'mdd': (1.05, 1.40), 'omc': (28, 42),
            'll': (55, 78), 'lp': (38, 55), 'finos_percent': (88, 100),
        },
        'CH': {
            'phi': (8, 16), 'cohesion': (0.40, 1.00),
            'humedad': (30, 55), 'peso_especifico': (2.55, 2.65),
            'mdd': (1.15, 1.45), 'omc': (25, 38),
            'll': (58, 85), 'lp': (26, 38), 'finos_percent': (92, 100),
        },
    },
}


def get_zone_defaults(zone, sucs):
    """
    Retorna promedios (punto medio de cada rango) para auto-fill del formulario.

    Args:
        zone: 'COSTA', 'SIERRA', o 'SELVA'
        sucs: Código SUCS, e.g. 'SM', 'CL'

    Returns:
        dict con promedios: phi, cohesion, humedad, peso_especifico, mdd, omc, ll, lp, finos_percent
        o None si la combinación no existe.
    """
    zone_data = ZONE_PROFILES.get(zone)
    if not zone_data or sucs not in zone_data:
        return None

    profile = zone_data[sucs]
    result = {}

    for key in ('phi', 'cohesion', 'humedad', 'peso_especifico', 'mdd', 'omc',
                'll', 'lp', 'finos_percent'):
        rng = profile.get(key)
        if rng and isinstance(rng, tuple) and len(rng) == 2:
            result[key] = round((rng[0] + rng[1]) / 2, 3)
        else:
            result[key] = None

    return result


def get_zone_ranges(zone, sucs):
    """
    Retorna los rangos completos (min, max) para validación en el frontend.

    Returns:
        dict con rangos o None
    """
    zone_data = ZONE_PROFILES.get(zone)
    if not zone_data or sucs not in zone_data:
        return None

    profile = zone_data[sucs]
    result = {}

    for key in ('phi', 'cohesion', 'humedad', 'peso_especifico', 'mdd', 'omc',
                'll', 'lp', 'finos_percent'):
        rng = profile.get(key)
        if rng and isinstance(rng, tuple) and len(rng) == 2:
            result[key] = list(rng)
        else:
            result[key] = None

    return result


def get_zone_info(zone):
    """Retorna label, emoji, color, description de una zona."""
    z = ZONE_PROFILES.get(zone)
    if not z:
        return None
    return {
        'label': z['label'],
        'emoji': z['emoji'],
        'color': z['color'],
        'description': z['description'],
    }


# ================================================================
#  DEPARTAMENTOS DEL PERÚ — Zona default y rango de altitud típico
#  Permite auto-seleccionar zona + aplicar factor de altitud
# ================================================================
PERU_DEPARTMENTS = {
    # COSTA
    'TUMBES':       {'zone': 'COSTA',  'alt_range': (0, 100),   'capital_alt': 7},
    'PIURA':        {'zone': 'COSTA',  'alt_range': (0, 400),   'capital_alt': 29},
    'LAMBAYEQUE':   {'zone': 'COSTA',  'alt_range': (0, 300),   'capital_alt': 18},
    'LA LIBERTAD':  {'zone': 'COSTA',  'alt_range': (0, 4000),  'capital_alt': 34},
    'LIMA':         {'zone': 'COSTA',  'alt_range': (0, 1500),  'capital_alt': 154},
    'ICA':          {'zone': 'COSTA',  'alt_range': (0, 500),   'capital_alt': 406},
    'AREQUIPA':     {'zone': 'COSTA',  'alt_range': (0, 4500),  'capital_alt': 2335},
    'MOQUEGUA':     {'zone': 'COSTA',  'alt_range': (0, 4600),  'capital_alt': 1410},
    'TACNA':        {'zone': 'COSTA',  'alt_range': (0, 4500),  'capital_alt': 562},
    # SIERRA
    'CAJAMARCA':    {'zone': 'SIERRA', 'alt_range': (1000, 4000), 'capital_alt': 2750},
    'AMAZONAS':     {'zone': 'SIERRA', 'alt_range': (200, 3500),  'capital_alt': 2335},
    'ANCASH':       {'zone': 'SIERRA', 'alt_range': (0, 6768),    'capital_alt': 3052},
    'HUANUCO':      {'zone': 'SIERRA', 'alt_range': (200, 4600),  'capital_alt': 1894},
    'PASCO':        {'zone': 'SIERRA', 'alt_range': (300, 4800),  'capital_alt': 4380},
    'JUNIN':        {'zone': 'SIERRA', 'alt_range': (400, 5000),  'capital_alt': 3271},
    'HUANCAVELICA': {'zone': 'SIERRA', 'alt_range': (1500, 5000), 'capital_alt': 3676},
    'AYACUCHO':     {'zone': 'SIERRA', 'alt_range': (500, 5000),  'capital_alt': 2761},
    'APURIMAC':     {'zone': 'SIERRA', 'alt_range': (1000, 5000), 'capital_alt': 2378},
    'CUSCO':        {'zone': 'SIERRA', 'alt_range': (500, 6372),  'capital_alt': 3399},
    'PUNO':         {'zone': 'SIERRA', 'alt_range': (3800, 5500), 'capital_alt': 3827},
    # SELVA
    'LORETO':       {'zone': 'SELVA',  'alt_range': (70, 220),   'capital_alt': 106},
    'SAN MARTIN':   {'zone': 'SELVA',  'alt_range': (200, 3000), 'capital_alt': 356},
    'UCAYALI':      {'zone': 'SELVA',  'alt_range': (100, 500),  'capital_alt': 154},
    'MADRE DE DIOS':{'zone': 'SELVA',  'alt_range': (150, 500),  'capital_alt': 186},
    # MIXTOS — default zone but can be overridden
    'CALLAO':       {'zone': 'COSTA',  'alt_range': (0, 50),     'capital_alt': 7},
}


def altitude_adjust(defaults, altitude_msnm, zone='SIERRA'):
    """
    Ajusta parámetros de suelo según altitud (m.s.n.m.).
    
    A mayor altitud en Sierra/Selva:
    - Mayor humedad natural (más precipitación, menos evapotranspiración)
    - Menor peso específico (suelos volcánicos, pumicitas)
    - Menor densidad seca (mayor porosidad por meteorización)
    - Mayor contenido de finos (meteorización intensa)
    - Mayor OMC (fluidos capilares en suelos porosos)
    
    Factores basados en correlaciones empíricas de laboratorios peruanos.
    
    Args:
        defaults: dict con los valores promedio del perfil base
        altitude_msnm: altitud en m.s.n.m.
        zone: zona geográfica
    
    Returns:
        dict con valores ajustados (copia, no modifica el original)
    """
    if not defaults or altitude_msnm is None:
        return defaults
    
    result = dict(defaults)  # copy
    alt = float(altitude_msnm)
    
    # Factores de ajuste según altitud (referencia: 2500 msnm = neutro)
    # Por cada 1000m sobre 2500: aplicar factor
    delta_km = (alt - 2500) / 1000.0
    
    # Humedad: +1.5% por cada 1000m sobre 2500
    if result.get('humedad') is not None:
        result['humedad'] = round(result['humedad'] * (1 + 0.08 * delta_km), 2)
    
    # Peso específico: -0.01 por cada 1000m sobre 2500 (pumicitas, cenizas)
    if result.get('peso_especifico') is not None:
        result['peso_especifico'] = round(result['peso_especifico'] - 0.01 * delta_km, 4)
    
    # MDD: -0.02 g/cm³ por cada 1000m sobre 2500
    if result.get('mdd') is not None:
        result['mdd'] = round(result['mdd'] * (1 - 0.015 * delta_km), 3)
    
    # OMC: +0.5% por cada 1000m sobre 2500
    if result.get('omc') is not None:
        result['omc'] = round(result['omc'] * (1 + 0.05 * delta_km), 2)
    
    # LL y LP: slight increase with altitude (more weathering)
    if result.get('ll') is not None:
        result['ll'] = round(result['ll'] * (1 + 0.02 * delta_km), 1)
    if result.get('lp') is not None:
        result['lp'] = round(result['lp'] * (1 + 0.02 * delta_km), 1)
    
    return result


def get_department_zone(department):
    """
    Retorna la zona default y altitud de un departamento.
    
    Args:
        department: nombre del departamento en MAYÚSCULAS (e.g., 'PUNO', 'LIMA')
    
    Returns:
        dict con zone, alt_range, capital_alt o None
    """
    return PERU_DEPARTMENTS.get(department.upper() if department else '')
