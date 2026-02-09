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
# 6. CORTE DIRECTO
# =============================================================================

def generate_shear_data(target_phi, target_c, specimen_side=6, specimen_height=2.544):
    """
    Genera curvas esfuerzo-deformación que producen φ y c objetivo.
    Usa regresión matemáticamente correcta: τ = c + σ·tan(φ)
    
    Args:
        target_phi: Ángulo de fricción objetivo (grados)
        target_c: Cohesión objetivo (kg/cm²)
    
    Returns:
        Dict compatible con calculate_direct_shear()
    """
    normal_stresses = [0.5, 1.0, 1.5]
    tan_phi = math.tan(math.radians(target_phi))
    
    specimens = []
    for sigma in normal_stresses:
        # τ_max objetivo usando la recta de Mohr-Coulomb
        tau_max = target_c + sigma * tan_phi
        
        # Generar curva esfuerzo-deformación sigmoidal realista
        # τ(ε) = τ_max * (1 - exp(-k*ε)) donde k controla la velocidad
        k = random.uniform(0.25, 0.4)  # rapidez de desarrollo del esfuerzo
        
        deformations = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15]
        curve = []
        
        for eps in deformations:
            # Curva sigmoidal con leve ruido
            tau = tau_max * (1 - math.exp(-k * eps))
            # Añadir ruido muy pequeño (±0.005) para realismo
            tau += random.uniform(-0.005, 0.005)
            tau = max(0, round(tau, 2))
            
            curve.append({
                'strain_pct': eps,
                'shear_stress': tau
            })
        
        # Asegurar que el último punto sea cercano al τ_max
        curve[-1]['shear_stress'] = round(tau_max + random.uniform(-0.01, 0.01), 2)
        
        specimens.append({
            'normal_stress': sigma,
            'curve': curve
        })
    
    return {
        'specimen_side_cm': specimen_side,
        'specimen_height_cm': specimen_height,
        'specimens': specimens
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
        result['shear'] = generate_shear_data(params['friction_angle'], params['cohesion'])
    
    return result
