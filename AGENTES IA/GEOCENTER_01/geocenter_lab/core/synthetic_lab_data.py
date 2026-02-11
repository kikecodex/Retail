"""
Synthetic Lab Data Generator — Ingeniería Inversa
Genera datos crudos de laboratorio realistas a partir de parámetros objetivo.
Los datos generados, al ser procesados por los módulos de cálculo existentes,
producen exactamente los resultados deseados.

Usa regresión matemáticamente correcta.
"""
import math
import random
import numpy as np


# =============================================================================
# HELPERS
# =============================================================================

def _rand_tare():
    """Peso de tarro realista entre 50-55g"""
    return round(random.uniform(50.0, 55.0), 2)

def _rand_solid(base=100, spread=20):
    """Peso de material seco realista"""
    return round(random.uniform(base - spread, base + spread), 2)


# =============================================================================
# 1. CONTENIDO DE HUMEDAD
# =============================================================================

def generate_moisture_data(target_w_percent, n_samples=3):
    """
    Genera datos crudos de humedad que producen el % objetivo.
    
    Inversa de: w = (wet_tare - dry_tare) / (dry_tare - tare) * 100
    
    Args:
        target_w_percent: Contenido de humedad objetivo (%)
        n_samples: Número de muestras (default 3)
    
    Returns:
        Dict compatible con calculate_moisture()
    """
    samples = []
    for _ in range(n_samples):
        tare = _rand_tare()
        solid = _rand_solid()
        # Agregar variación realista (±0.3% alrededor del target)
        w_actual = target_w_percent + random.uniform(-0.3, 0.3)
        water = solid * (w_actual / 100)
        
        dry_tare = round(tare + solid, 2)
        wet_tare = round(dry_tare + water, 2)
        
        samples.append({
            'tare': tare,
            'dry_tare': dry_tare,
            'wet_tare': wet_tare
        })
    
    return {'samples': samples}


# =============================================================================
# 2. PESO ESPECÍFICO (Gs)
# =============================================================================

def generate_specific_gravity_data(target_gs, n_samples=2):
    """
    Genera datos de picnómetro que producen el Gs objetivo.
    
    Inversa de: Gs = Mo / (Mo + Ma - Mb)
    → Mb = Mo + Ma - Mo/Gs
    
    Args:
        target_gs: Peso específico objetivo (e.g., 2.63)
    
    Returns:
        Dict compatible con calculate_specific_gravity()
    """
    samples = []
    for _ in range(n_samples):
        # Valores típicos de picnómetro
        mo = round(random.uniform(25.0, 35.0), 2)   # masa suelo seco
        ma = round(random.uniform(640.0, 660.0), 2)  # picnómetro + agua
        
        # Agregar variación realista
        gs_actual = target_gs + random.uniform(-0.02, 0.02)
        
        # Inversa: Mb = Mo + Ma - Mo/Gs
        mb = mo + ma - (mo / gs_actual)
        mb = round(mb, 2)
        
        samples.append({
            'mo': mo,
            'ma': ma,
            'mb': mb
        })
    
    return {'samples': samples}


# =============================================================================
# 3. LÍMITES DE CONSISTENCIA (LL, PL)
# =============================================================================

def generate_limits_data(target_ll, target_pl):
    """
    Genera datos de copa de Casagrande (LL) y rollitos (PL).
    
    LL usa regresión: humedad = slope * ln(golpes) + intercept
    A 25 golpes: LL = slope * ln(25) + intercept
    
    Inversa: dada la recta, generar 4 puntos sobre ella con ruido controlado.
    
    Args:
        target_ll: Límite líquido objetivo (%)
        target_pl: Límite plástico objetivo (%)
    
    Returns:
        Dict compatible con calculate_limits()
    """
    # --- Límite Líquido (LL) ---
    # Generar pendiente realista (entre -5 y -2, negativa porque a más golpes menos humedad)
    slope = random.uniform(-4.5, -2.0)
    # intercept = LL - slope * ln(25)
    intercept = target_ll - slope * math.log(25)
    
    # 4 puntos de golpes típicos
    blow_counts = [16, 22, 27, 34]
    ll_data = []
    
    for blows in blow_counts:
        # Humedad en la recta + ruido mínimo
        w_target = slope * math.log(blows) + intercept
        noise = random.uniform(-0.15, 0.15)
        w_actual = w_target + noise
        
        # Generar pesos de tarro → inversa de: w = (wet-dry)/(dry-tare)*100
        tare = _rand_tare()
        solid = _rand_solid(base=15, spread=3)  # LL usa poca muestra
        water = solid * (w_actual / 100)
        
        dry_tare = round(tare + solid, 2)
        wet_tare = round(dry_tare + water, 2)
        
        ll_data.append({
            'blows': blows,
            'tare': tare,
            'dry_tare': dry_tare,
            'wet_tare': wet_tare
        })
    
    # --- Límite Plástico (PL) ---
    pl_data = []
    for _ in range(2):
        w_actual = target_pl + random.uniform(-0.2, 0.2)
        tare = _rand_tare()
        solid = _rand_solid(base=8, spread=2)  # PL usa aún menos muestra
        water = solid * (w_actual / 100)
        
        dry_tare = round(tare + solid, 2)
        wet_tare = round(dry_tare + water, 2)
        
        pl_data.append({
            'tare': tare,
            'dry_tare': dry_tare,
            'wet_tare': wet_tare
        })
    
    return {
        'll_data': ll_data,
        'pl_data': pl_data
    }


# =============================================================================
# 4. GRANULOMETRÍA
# =============================================================================

# Perfiles de curva granulométrica típica por tipo SUCS
# Valores = % pasante para cada tamiz estándar
GRANULOMETRY_PROFILES = {
    # Tamices:  3"  2"  1.5"  1"  3/4" 1/2" 3/8"  #4  #10  #20  #40  #60  #100 #200
    'GW': [100, 95, 88, 75, 65, 52, 42, 30, 18, 12,  8,  5,  3,  2],
    'GP': [100, 97, 93, 82, 72, 58, 48, 35, 22, 15, 10,  7,  5,  3],
    'GM': [100, 96, 90, 78, 68, 55, 45, 33, 24, 19, 16, 14, 13, 13],
    'GC': [100, 97, 92, 80, 70, 58, 48, 36, 28, 23, 20, 18, 16, 15],
    'SW': [100,100,100,100,100, 98, 95, 88, 65, 42, 25, 14,  7,  3],
    'SP': [100,100,100,100,100, 99, 97, 92, 70, 48, 30, 18, 10,  4],
    'SM': [100,100,100,100, 99, 97, 95, 85, 68, 52, 40, 32, 25, 18],
    'SC': [100,100,100,100, 99, 98, 96, 88, 72, 58, 45, 38, 32, 25],
    'ML': [100,100,100,100,100,100,100, 98, 95, 90, 82, 72, 62, 55],
    'CL': [100,100,100,100,100,100,100, 97, 93, 88, 80, 70, 62, 58],
    'MH': [100,100,100,100,100,100,100, 99, 97, 94, 88, 80, 72, 68],
    'CH': [100,100,100,100,100,100,100, 98, 96, 92, 86, 78, 72, 70],
    'OL': [100,100,100,100,100,100, 99, 95, 88, 78, 65, 55, 48, 42],
    'OH': [100,100,100,100,100,100,100, 97, 93, 87, 80, 72, 65, 60],
}

# Aberturas de tamiz en mm (estándar ASTM)
SIEVE_OPENINGS = [
    75.0, 50.0, 37.5, 25.0, 19.0, 12.5, 9.5, 4.75,
    2.0, 0.85, 0.425, 0.25, 0.15, 0.075
]

SIEVE_NAMES = [
    '3"', '2"', '1 1/2"', '1"', '3/4"', '1/2"', '3/8"', 'N°4',
    'N°10', 'N°20', 'N°40', 'N°60', 'N°100', 'N°200'
]


def generate_granulometry_data(target_sucs, target_fines_pct=None, total_weight=500):
    """
    Genera datos granulométricos que producen la clasificación SUCS objetivo.
    
    Args:
        target_sucs: Tipo SUCS objetivo (e.g., 'SM', 'GC', 'CL')
        target_fines_pct: % pasante tamiz N°200 (si None, usa perfil)
        total_weight: Peso total de la muestra (g)
    
    Returns:
        Dict compatible con calculate_granulometry()
    """
    # Obtener perfil base
    sucs_key = target_sucs.upper()
    if sucs_key not in GRANULOMETRY_PROFILES:
        sucs_key = 'SM'  # default
    
    profile = GRANULOMETRY_PROFILES[sucs_key].copy()
    
    # Ajustar finos si se especifica
    if target_fines_pct is not None:
        current_fines = profile[-1]
        scale = target_fines_pct / current_fines if current_fines > 0 else 1
        # Ajustar solo los tamices finos (N°40 en adelante)
        for i in range(10, len(profile)):
            profile[i] = min(profile[i] * scale, profile[i-1])
        profile[-1] = target_fines_pct
    
    # Agregar ruido realista (±1-2%)
    for i in range(1, len(profile)):
        noise = random.uniform(-1.5, 1.5)
        profile[i] = max(0, min(profile[i] + noise, profile[i-1]))  # monotónicamente decreciente
    profile[0] = 100  # Siempre 100% en el tamiz más grande
    
    # Calcular pesos retenidos a partir de % pasante
    sieves = []
    for i, (opening, name, pct_pass) in enumerate(zip(SIEVE_OPENINGS, SIEVE_NAMES, profile)):
        pct_retained_accum = 100 - pct_pass
        if i == 0:
            weight_retained = total_weight * (pct_retained_accum / 100)
        else:
            prev_accum = 100 - profile[i-1]
            weight_retained = total_weight * ((pct_retained_accum - prev_accum) / 100)
        
        sieves.append({
            'sieve': name,
            'opening_mm': opening,
            'retained_g': round(max(0, weight_retained), 2)
        })
    
    return {
        'total_weight': total_weight,
        'sieves': sieves
    }


# =============================================================================
# 5. PROCTOR MODIFICADO
# =============================================================================

def generate_proctor_data(target_mdd, target_omc, n_points=5):
    """
    Genera datos de compactación que producen MDD y OMC objetivo.
    
    Inversa: genera 5 puntos sobre una parábola con vértice en (OMC, MDD).
    γd = a*w² + b*w + c, donde vértice = (-b/2a, c - b²/4a)
    
    Args:
        target_mdd: Densidad máxima seca objetivo (g/cm³)
        target_omc: Contenido de humedad óptimo objetivo (%)
    
    Returns:
        Dict compatible con calculate_proctor()
    """
    # Parábola: γd = a*(w - omc)² + mdd
    # a debe ser negativo (parábola invertida), típico: -0.002 a -0.004
    a = random.uniform(-0.004, -0.002)
    
    # Distribuir humedades simétricamente alrededor del OMC
    half_range = random.uniform(3.5, 4.5)  # ±3.5-4.5% del OMC
    moisture_targets = [
        target_omc - half_range,
        target_omc - half_range * 0.5,
        target_omc,
        target_omc + half_range * 0.5,
        target_omc + half_range
    ]
    
    # Datos del molde (valores típicos del ENSAYOS.xlsx)
    mold_height = 13.39
    mold_diameter = 10.1
    mold_weight = 1960
    volume = math.pi * ((mold_diameter / 2) ** 2) * mold_height  # ~1072.79 cm³
    
    points = []
    for w_target in moisture_targets:
        # Densidad seca en la parábola
        dd = a * (w_target - target_omc) ** 2 + target_mdd
        
        # Densidad húmeda: γw = γd * (1 + w/100)
        wet_density = dd * (1 + w_target / 100)
        
        # Peso suelo húmedo: peso = γw * V
        wet_soil = wet_density * volume
        mold_wet_g = round(mold_weight + wet_soil, 0)
        
        # Generar 2 muestras de humedad por punto
        samples = []
        for _ in range(2):
            w_actual = w_target + random.uniform(-0.15, 0.15)
            tare = _rand_tare()
            solid = _rand_solid()
            water = solid * (w_actual / 100)
            
            dry_tare = round(tare + solid, 2)
            wet_tare = round(dry_tare + water, 2)
            
            samples.append({
                'tare': tare,
                'wet_tare': wet_tare,
                'dry_tare': dry_tare
            })
        
        points.append({
            'samples': samples,
            'mold_wet_g': mold_wet_g
        })
    
    return {
        'mold': {
            'height_cm': mold_height,
            'diameter_cm': mold_diameter,
            'weight_g': mold_weight
        },
        'points': points
    }


# =============================================================================
# 6. CORTE DIRECTO — Con datos reales de referencia (Yunguyo 2015)
# =============================================================================

# Datos crudos REALES extraídos de corte_directo.xlsx (Yunguyo)
# Estos son las lecturas de dial VERIFICADAS que producen:
#   φ = 26.97° (regresión), C = 0.3349 kg/cm² (regresión)
#   τ_max = [0.4841, 0.6057, 0.9042] para σn = [0.278, 0.556, 1.111]
YUNGUYO_REFERENCE = {
    'project': 'Yunguyo I.E.I. Jirón Zepita (2015)',
    'phi_regression': 26.97,
    'c_regression': 0.3349,
    'calibration': {'a': 0.874778, 'b': 1.57003513, 'conv': 0.4535929094},
    'specimen_side_cm': 6,
    'specimen_height_cm': 2,
    'normal_forces_kg': [1, 2, 4],
    'mold_weight_g': 157.7,
    'specimen_weights_g': [281.7, 285.2, 282.9],
    'moisture_data': [
        {'container_num': 7, 'container_weight_g': 23.8, 'container_wet_g': 98.7, 'container_dry_g': 91.5},
        {'container_num': 8, 'container_weight_g': 22.9, 'container_wet_g': 80.6, 'container_dry_g': 74.9},
        {'container_num': 9, 'container_weight_g': 21.7, 'container_wet_g': 71.4, 'container_dry_g': 66.8},
    ],
    # 15 lecturas de dial por espécimen — PICO en deform=1.75
    'dial_readings': [
        # Espécimen 1 (1 kg, σn=0.278, τ_max=0.484)
        [0, 9, 13, 19, 25, 37, 39, 41, 41, 42, 42, 41, 40, 39, 39],
        # Espécimen 2 (2 kg, σn=0.556, τ_max=0.606)
        [0, 13, 17, 29, 37, 41, 46, 49, 52, 53, 53, 51, 51, 50, 50],
        # Espécimen 3 (4 kg, σn=1.111, τ_max=0.904)
        [0, 23, 34, 48, 57, 67, 74, 76, 78, 79, 80, 79, 77, 76, 75],
    ],
    'tau_max': [0.4841, 0.6057, 0.9042],
}

# Datos crudos REALES extraídos de ENSAYOS.xlsx (Carhuayoc, San Marcos, Huari, Ancash)
# Proyecto: "MEJORAMIENTO DEL SERVICIO...", Calicata C-04, Prof. 1.50m
# Suelo GC (Grava arcillosa), Sierra (Ancash)
# φ = 25.17° (regresión), C = 0.0563 kg/cm² (regresión)
CARHUAYOC_REFERENCE = {
    'project': 'Carhuayoc-San Marcos, Ancash (2025)',
    'sucs': 'GC',
    'zone': 'SIERRA',
    'phi_regression': 25.17,
    'c_regression': 0.0563,
    'specimen_side_cm': 6,
    'specimen_height_cm': 2,
    'normal_loads_kg': [0.5, 1.0, 2.0],  # 3 specimens
    # 14 strain readings per specimen (deformaciones ×10⁻²)
    'strain_sequence': [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15],
    'shear_readings': [
        # Espécimen 1 (0.5 kg) — τ values (kg/cm²)
        [0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.12, 0.13, 0.17, 0.19, 0.21, 0.23, 0.27],
        # Espécimen 2 (1.0 kg)
        [0.01, 0.03, 0.06, 0.08, 0.09, 0.10, 0.14, 0.15, 0.25, 0.35, 0.38, 0.45, 0.49, 0.51],
        # Espécimen 3 (2.0 kg)
        [0.02, 0.04, 0.08, 0.10, 0.12, 0.15, 0.26, 0.28, 0.38, 0.49, 0.58, 0.62, 0.69, 0.73],
    ],
    # Proctor data: 5 compaction points
    'proctor': {
        'humidity_pct': [3.095, 5.205, 7.107, 9.176, 11.378],
        'wet_density': [1.807, 1.860, 1.925, 1.948, 1.959],
        'dry_density': [1.753, 1.768, 1.797, 1.784, 1.759],
        'mdd': 1.797,
        'omc': 7.107,
        'mold_weight_g': 1960,
        'mold_volume_cc': 1072.79,
    },
    # Moisture content
    'moisture': {
        'w_pct': 4.45,
        'wet_weight_g': [203.6, 195.6],
        'dry_weight_g': [196.1, 188.2],
        'container_weight_g': [24.9, 24.5],
    },
    # Limits
    'limits': {
        'll': 38.14,
        'lp': 24.89,
        'ip': 13.25,
        'll_blows': [11, 17, 27, 37],
        'll_moisture_pct': [40.99, 38.80, 38.21, 36.88],
    },
    # Specific gravity
    'specific_gravity': {
        'gs': 2.6244,
        'gs_values': [2.5794, 2.6694],
    },
}

# Diccionario de referencia para selección automática
REFERENCE_DATASETS = {
    'SM': YUNGUYO_REFERENCE,    # Arena limosa — Puno (Sierra)
    'GC': CARHUAYOC_REFERENCE,  # Grava arcillosa — Ancash (Sierra)
}

# Secuencia estándar de deformaciones (mm × 10⁻²) — ASTM D3080
STD_DEFORMATIONS = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75]


# ======================== SUCS similarity for reference selection ========================
# Groups: G=gravas, S=arenas, M=limos, C=arcillas
_SUCS_GROUP = {
    'GW': 'G', 'GP': 'G', 'GM': 'G', 'GC': 'G',
    'SW': 'S', 'SP': 'S', 'SM': 'S', 'SC': 'S',
    'ML': 'M', 'MH': 'M', 'CL': 'C', 'CH': 'C',
}

def _select_reference(sucs):
    """
    Selecciona la referencia más cercana al SUCS objetivo.
    Prioridad: mismo SUCS > mismo grupo > fallback a YUNGUYO.
    """
    if not sucs:
        return YUNGUYO_REFERENCE
    sucs = sucs.upper()
    # Exact match
    if sucs in REFERENCE_DATASETS:
        return REFERENCE_DATASETS[sucs]
    # Same group (e.g., SC → GC or SM)
    target_group = _SUCS_GROUP.get(sucs, '')
    for ref_sucs, ref_data in REFERENCE_DATASETS.items():
        if _SUCS_GROUP.get(ref_sucs, '') == target_group:
            return ref_data
    # Fallback
    return YUNGUYO_REFERENCE


def _normalize_reference(ref):
    """
    Normaliza la referencia a formato uniforme con dial_readings y calibración.
    - YUNGUYO: ya tiene dial_readings + calibration → pass through
    - CARHUAYOC: tiene shear_readings (τ directos) → convertir a dial equivalentes
    """
    if 'dial_readings' in ref:
        # Yunguyo format — already has raw dials
        return {
            'dial_readings': ref['dial_readings'],
            'calibration': ref['calibration'],
            'normal_forces_kg': ref['normal_forces_kg'],
            'tau_max': ref['tau_max'],
            'moisture_data': ref['moisture_data'],
            'mold_weight_g': ref.get('mold_weight_g', 157.7),
            'specimen_weights_g': ref.get('specimen_weights_g', [281.7, 285.2, 282.9]),
            'deformations': STD_DEFORMATIONS,
        }
    
    if 'shear_readings' in ref:
        # Carhuayoc format — has direct τ values per strain point
        # Use standard calibration and reverse-engineer dial readings
        #   τ = F / A → F = τ × A → dial = (F/conv - b) / a
        cal_a = 0.874778
        cal_b = 1.57003513
        cal_conv = 0.4535929094
        side = ref.get('specimen_side_cm', 6)
        area = side * side
        
        dial_readings = []
        tau_maxes = []
        for specimen_tau in ref['shear_readings']:
            dials = []
            max_tau = 0
            for tau in specimen_tau:
                if tau <= 0:
                    dials.append(0)
                else:
                    force = tau * area
                    dial = (force / cal_conv - cal_b) / cal_a
                    dials.append(max(0, round(dial)))
                max_tau = max(max_tau, tau)
            dial_readings.append(dials)
            tau_maxes.append(round(max_tau, 4))
        
        # Build moisture_data from ref if available
        moisture_data = []
        if 'moisture' in ref:
            m = ref['moisture']
            for i in range(min(3, len(m.get('wet_weight_g', [])))):
                moisture_data.append({
                    'container_num': 7 + i,
                    'container_weight_g': m['container_weight_g'][i],
                    'container_wet_g': m['wet_weight_g'][i],
                    'container_dry_g': m['dry_weight_g'][i],
                })
        if not moisture_data:
            # Fallback synthetic moisture data
            moisture_data = YUNGUYO_REFERENCE['moisture_data']
        
        return {
            'dial_readings': dial_readings,
            'calibration': {'a': cal_a, 'b': cal_b, 'conv': cal_conv},
            'normal_forces_kg': ref.get('normal_loads_kg', [1, 2, 4]),
            'tau_max': tau_maxes,
            'moisture_data': moisture_data,
            'mold_weight_g': ref.get('moisture', {}).get('container_weight_g', [157.7])[0] if 'moisture' in ref else 157.7,
            'specimen_weights_g': [280, 283, 281],  # synthetic
            'deformations': ref.get('strain_sequence', STD_DEFORMATIONS),
        }
    
    # Unknown format — return Yunguyo as fallback
    return _normalize_reference(YUNGUYO_REFERENCE)


def generate_shear_data(target_phi, target_c, specimen_side=6, specimen_height=2,
                        moisture_pct=None, sucs=None):
    """
    Genera datos crudos de corte directo basados en curvas REALES de referencia,
    escaladas al φ y c objetivo.
    
    Selecciona automáticamente la referencia más cercana al SUCS:
      - SM → Yunguyo (Puno 2015)
      - GC → Carhuayoc (Ancash 2025)
      - Otros → interpolación o fallback
    
    Args:
        target_phi: Ángulo de fricción objetivo (grados)
        target_c: Cohesión objetivo (kg/cm²)
        specimen_side: Lado del espécimen (cm), default 6
        specimen_height: Altura del espécimen (cm), default 2
        moisture_pct: Humedad W(%), opcional
        sucs: Código SUCS (e.g., 'SM', 'GC') para selección de referencia
    
    Returns:
        Dict compatible con calculate_direct_shear() (raw dial mode)
    """
    # Auto-select reference based on SUCS type
    raw_ref = _select_reference(sucs)
    ref = _normalize_reference(raw_ref)
    
    cal_a = ref['calibration']['a']
    cal_b = ref['calibration']['b']
    cal_conv = ref['calibration']['conv']
    
    normal_forces_kg = ref['normal_forces_kg']
    area = specimen_side * specimen_side  # 36 cm²
    
    tan_phi = math.tan(math.radians(target_phi))
    
    # Generate mold and humidity data
    mold_weight = round(random.uniform(155, 160), 1)
    base_moisture = moisture_pct or round(random.uniform(9, 13), 1)
    
    specimens = []
    for i, force_kg in enumerate(normal_forces_kg):
        # Normal stress = (Force × 10) / Area
        sigma_n = (force_kg * 10) / area
        
        # Target peak shear stress: τ_max = c + σ·tan(φ)
        tau_target = target_c + sigma_n * tan_phi
        
        # Reference peak shear stress from selected dataset
        tau_ref = ref['tau_max'][i]
        
        # Scale factor: how much to scale the reference dial readings
        scale = tau_target / tau_ref if tau_ref > 0 else 1.0
        
        # Get reference dial readings for this specimen
        ref_dials = ref['dial_readings'][i]
        
        # Scale and add small noise
        curve = []
        deformations = ref.get('deformations', STD_DEFORMATIONS)
        for j, eps in enumerate(deformations):
            if j < len(ref_dials):
                ref_dial = ref_dials[j]
            else:
                ref_dial = ref_dials[-1]  # extend with last value
            scaled_dial = ref_dial * scale
            
            # Add small noise (±1 dial unit) for realism
            noise = random.uniform(-0.8, 0.8)
            dial_val = max(0, round(scaled_dial + noise))
            
            curve.append({
                'deform': eps,
                'dial': dial_val
            })
        
        # Ensure dial=0 at deformation=0
        curve[0]['dial'] = 0
        
        # Specimen moisture with small variation
        spec_moisture = round(base_moisture + random.uniform(-0.5, 0.5), 2)
        
        # Specimen weight (realistic range around reference values)
        specimen_weight = round(mold_weight + random.uniform(120, 130), 1)
        density = round((specimen_weight - mold_weight) / (area * specimen_height), 4)
        
        specimens.append({
            'normal_force_kg': force_kg,
            'curve': curve,
            'mold_weight_g': mold_weight,
            'mold_sample_weight_g': specimen_weight,
            'density_g_cm3': density,
            'moisture_pct': spec_moisture,
        })
    
    # Generate humidity verification data based on reference pattern
    humidity_data = []
    n_moisture = len(ref['moisture_data'])
    for i in range(3):
        w_actual = base_moisture + random.uniform(-0.4, 0.4)
        # Use reference container weights as base, with variation (cycle if fewer than 3)
        ref_hum = ref['moisture_data'][i % n_moisture]
        tare = round(ref_hum['container_weight_g'] + random.uniform(-1, 1), 1)
        dry_weight = round(random.uniform(45, 70), 1)
        dry_tare = round(tare + dry_weight, 1)
        wet_tare = round(dry_tare + dry_weight * w_actual / 100, 1)
        humidity_data.append({
            'container_num': 7 + i,
            'container_weight_g': tare,
            'container_wet_g': wet_tare,
            'container_dry_g': dry_tare,
        })
    
    return {
        'specimen_side_cm': specimen_side,
        'specimen_height_cm': specimen_height,
        'ring_calibration': {
            'a': cal_a,
            'b': cal_b,
            'conv': cal_conv,
        },
        'test_speed_mm_min': 0.5,
        'method': 'UU',
        'sample_state': 'Natural',
        'sample_type': 'Inalterada',
        'humidity_verification': humidity_data,
        'specimens': specimens,
    }


# =============================================================================
# 7. PIPELINE COMPLETO
# =============================================================================

def generate_all_lab_data(params):
    """
    Pipeline completo: genera TODOS los datos crudos de laboratorio
    a partir de parámetros estimados.
    
    Args:
        params: {
            'moisture_pct': float,      # Contenido de humedad (%)
            'specific_gravity': float,  # Gs
            'liquid_limit': float,      # LL (%)
            'plastic_limit': float,     # PL (%)
            'sucs': str,                # Clasificación SUCS
            'fines_pct': float,         # % pasante N°200 (opcional)
            'mdd': float,               # Densidad máxima seca (g/cm³)
            'omc': float,               # Humedad óptima (%)
            'friction_angle': float,    # φ (grados)
            'cohesion': float           # c (kg/cm²)
        }
    
    Returns:
        Dict con todos los datos crudos generados, keyed by test name.
    """
    result = {}
    
    # Contenido de humedad
    if 'moisture_pct' in params:
        result['moisture'] = generate_moisture_data(params['moisture_pct'])
    
    # Peso específico
    if 'specific_gravity' in params:
        result['specific_gravity'] = generate_specific_gravity_data(params['specific_gravity'])
    
    # Límites de consistencia
    if 'liquid_limit' in params and 'plastic_limit' in params:
        result['limits'] = generate_limits_data(params['liquid_limit'], params['plastic_limit'])
    
    # Granulometría
    if 'sucs' in params:
        result['granulometry'] = generate_granulometry_data(
            params['sucs'],
            params.get('fines_pct')
        )
    
    # Proctor Modificado
    if 'mdd' in params and 'omc' in params:
        result['proctor'] = generate_proctor_data(params['mdd'], params['omc'])
    
    # Corte Directo
    if 'friction_angle' in params and 'cohesion' in params:
        result['shear'] = generate_shear_data(
            params['friction_angle'], params['cohesion'],
            moisture_pct=params.get('moisture_pct'),
            sucs=params.get('sucs')
        )
    
    return result
