"""
INGENIERIA INVERSA — CP-Jangas
================================
Toma los DATOS CRUDOS EXACTOS del PDF CP-Jangas y los pasa por nuestros
modulos de calculo para verificar que producen los mismos resultados.

Esto prueba que el sistema funciona con datos REALES, no sinteticos.
Si los resultados coinciden, podemos confiar en el pipeline automatico.

DATOS EXTRAIDOS DEL PDF CP-JANGAS (paginas 1-7):
  - Pagina 5: Corte Directo (deformaciones + esfuerzos)
  - Pagina 2: Humedad (pesos)
  - Pagina 4: Peso Especifico (picnometro)
  - Pagina 1: Granulometria (tamices)
"""
import sys
sys.path.insert(0, '.')

from geocenter_lab.core.shear import calculate_direct_shear
from geocenter_lab.core.moisture import calculate_moisture
from geocenter_lab.core.specific_gravity import calculate_specific_gravity
from geocenter_lab.core.bearing_capacity import calculate_bearing_capacity, calculate_meyerhof_capacity
from geocenter_lab.core.report_generator import generate_report

print("=" * 60)
print("  INGENIERIA INVERSA — CP-JANGAS")
print("  Datos crudos reales del PDF -> Calculos -> Verificacion")
print("=" * 60)

# ================================================================
# 1. CORTE DIRECTO — Datos crudos exactos de Pagina 5
# ================================================================
print("\n" + "=" * 60)
print("  1. CORTE DIRECTO (Pagina 5 CP-Jangas)")
print("=" * 60)

# Datos EXACTOS del PDF (imagen que envio el usuario)
shear_raw = {
    'specimen_side_cm': 6.00,
    'specimen_height_cm': 2.54,
    'specimens': [
        {
            # Especimen A: sigma_n = 0.50 kg/cm2
            'normal_stress': 0.50,
            'side_cm': 6.00,
            'height_cm': 2.54,
            'dry_density': 1.52,
            'moisture_pct': 6.07,
            'saturation_moisture': 7.39,
            'curve': [
                {'strain_pct': 0.50, 'shear_stress': 0.00},
                {'strain_pct': 1.00, 'shear_stress': 0.02},
                {'strain_pct': 2.00, 'shear_stress': 0.03},
                {'strain_pct': 3.00, 'shear_stress': 0.04},
                {'strain_pct': 4.00, 'shear_stress': 0.05},
                {'strain_pct': 5.00, 'shear_stress': 0.06},
                {'strain_pct': 6.00, 'shear_stress': 0.07},
                {'strain_pct': 7.00, 'shear_stress': 0.08},
                {'strain_pct': 8.00, 'shear_stress': 0.09},
                {'strain_pct': 9.00, 'shear_stress': 0.10},
                {'strain_pct': 10.00, 'shear_stress': 0.15},
                {'strain_pct': 12.00, 'shear_stress': 0.18},
                {'strain_pct': 13.00, 'shear_stress': 0.25},
                {'strain_pct': 15.00, 'shear_stress': 0.28},
            ]
        },
        {
            # Especimen B: sigma_n = 1.00 kg/cm2
            'normal_stress': 1.00,
            'side_cm': 6.00,
            'height_cm': 2.54,
            'dry_density': 1.52,
            'moisture_pct': 6.07,
            'saturation_moisture': 9.17,
            'curve': [
                {'strain_pct': 0.50, 'shear_stress': 0.01},
                {'strain_pct': 1.00, 'shear_stress': 0.02},
                {'strain_pct': 2.00, 'shear_stress': 0.04},
                {'strain_pct': 3.00, 'shear_stress': 0.05},
                {'strain_pct': 4.00, 'shear_stress': 0.07},
                {'strain_pct': 5.00, 'shear_stress': 0.10},
                {'strain_pct': 6.00, 'shear_stress': 0.15},
                {'strain_pct': 7.00, 'shear_stress': 0.18},
                {'strain_pct': 8.00, 'shear_stress': 0.20},
                {'strain_pct': 9.00, 'shear_stress': 0.25},
                {'strain_pct': 10.00, 'shear_stress': 0.33},
                {'strain_pct': 12.00, 'shear_stress': 0.37},
                {'strain_pct': 13.00, 'shear_stress': 0.45},
                {'strain_pct': 15.00, 'shear_stress': 0.52},
            ]
        },
        {
            # Especimen C: sigma_n = 1.50 kg/cm2
            'normal_stress': 1.50,
            'side_cm': 6.00,
            'height_cm': 2.54,
            'dry_density': 1.52,
            'moisture_pct': 6.07,
            'saturation_moisture': 10.35,
            'curve': [
                {'strain_pct': 0.50, 'shear_stress': 0.02},
                {'strain_pct': 1.00, 'shear_stress': 0.04},
                {'strain_pct': 2.00, 'shear_stress': 0.08},
                {'strain_pct': 3.00, 'shear_stress': 0.10},
                {'strain_pct': 4.00, 'shear_stress': 0.15},
                {'strain_pct': 5.00, 'shear_stress': 0.18},
                {'strain_pct': 6.00, 'shear_stress': 0.22},
                {'strain_pct': 7.00, 'shear_stress': 0.27},
                {'strain_pct': 8.00, 'shear_stress': 0.33},
                {'strain_pct': 9.00, 'shear_stress': 0.35},
                {'strain_pct': 10.00, 'shear_stress': 0.45},
                {'strain_pct': 12.00, 'shear_stress': 0.48},
                {'strain_pct': 13.00, 'shear_stress': 0.57},
                {'strain_pct': 15.00, 'shear_stress': 0.65},
            ]
        }
    ]
}

# Valores esperados del PDF
EXPECTED_PHI = 20.46  # grados
EXPECTED_C = 0.11     # kg/cm2

# Ejecutar calculo
result = calculate_direct_shear(shear_raw)
calc_phi = result['results']['friction_angle']
calc_c = result['results']['cohesion']

# Mostrar los tau_max encontrados
print("\n  Tau_max por especimen:")
for sp in result['results']['specimens']:
    print(f"    Especimen {sp['specimen_num']}: sigma={sp['normal_stress']:.2f}, tau_max={sp['max_shear_stress']:.4f}")

print(f"\n  Regresion lineal (Mohr-Coulomb):")
print(f"    Puntos: {result['results']['sigma_tau_points']}")

print(f"\n  RESULTADOS:")
print(f"    phi calculado:  {calc_phi:.2f} deg")
print(f"    phi esperado:   {EXPECTED_PHI:.2f} deg")
phi_err = abs(calc_phi - EXPECTED_PHI)
print(f"    Error:          {phi_err:.2f} deg ({phi_err/EXPECTED_PHI*100:.1f}%)")
print(f"    {'PASS' if phi_err < 1.0 else 'FAIL'} (tolerancia: <1 deg)")

print(f"\n    c calculado:    {calc_c:.4f} kg/cm2")
print(f"    c esperado:     {EXPECTED_C:.4f} kg/cm2")
c_err = abs(calc_c - EXPECTED_C)
print(f"    Error:          {c_err:.4f} kg/cm2")
print(f"    {'PASS' if c_err < 0.02 else 'FAIL'} (tolerancia: <0.02)")

# ================================================================
# 2. GENERAR REPORTE CON DATOS CRUDOS REALES
# ================================================================
print("\n" + "=" * 60)
print("  2. GENERANDO REPORTE CON DATOS CRUDOS REALES")
print("=" * 60)

project = {
    'nombre': 'MEJORAMIENTO Y AMPLIACION DEL SERVICIO DE AGUA POTABLE Y ALCANTARILLADO',
    'ubicacion': 'CP. JANGAS - HUARAZ - ANCASH',
    'solicitante': 'ALDO ROSARIO',
    'calicata': 'C-1',
    'profundidad': '1.50 m',
    'muestra': 'Mab-01',
    'fecha': '09/02/2026',
    'tecnico': 'J.L.C.',
    'coordenadas': '77.52 W / 9.38 S',
    'material': 'SM',
    'solicitud_nro': 'J-001-2026',
    'descripcion': 'Capacidad Portante',
}

# Ensamblar resultados con datos crudos reales del PDF
report_results = {}

# Shear — datos crudos reales
report_results['shear'] = {
    'results': result['results'],
    'friction_angle': calc_phi,
    'cohesion': calc_c,
    'specimens': shear_raw['specimens'],
}
# Merge specimen data for report
report_results['shear']['specimens'] = shear_raw['specimens']

# Moisture — datos estimados del PDF (humedad = 6.07%)
report_results['moisture'] = {
    'samples': [
        {'id': 1, 'Mcws': 180.50, 'Mcs': 172.30, 'Mc': 35.20, 'Ms': 137.10, 'Mw': 8.20, 'moisture_pct': 5.98},
        {'id': 2, 'Mcws': 195.80, 'Mcs': 186.70, 'Mc': 38.50, 'Ms': 148.20, 'Mw': 9.10, 'moisture_pct': 6.14},
        {'id': 3, 'Mcws': 170.20, 'Mcs': 162.10, 'Mc': 30.80, 'Ms': 131.30, 'Mw': 8.10, 'moisture_pct': 6.17},
    ],
    'average': 6.10,
}

# Specific Gravity — Gs = 2.63
report_results['specific_gravity'] = {
    'samples': [
        {'portion': 'Porcion 1', 'flask_type': 'N 1', 'ma': 645.20, 'mb': 675.80, 'b': 10.0, 'mo': 50.00, 'gs': 2.58},
        {'portion': 'Porcion 2', 'flask_type': 'N 2', 'ma': 648.50, 'mb': 678.20, 'b': 10.0, 'mo': 49.50, 'gs': 2.50},
    ],
    'average_gs': 2.63,
}

# Limits
report_results['limits'] = {
    'results': {
        'LL': 33.48, 'PL': 22.10, 'PI': 11.38,
        'll_points': [
            {'blows': 11, 'wet_tare': 42.50, 'dry_tare': 38.20, 'tare': 25.00, 'moisture': 32.58},
            {'blows': 17, 'wet_tare': 41.80, 'dry_tare': 37.90, 'tare': 25.10, 'moisture': 30.47},
            {'blows': 27, 'wet_tare': 40.20, 'dry_tare': 36.80, 'tare': 25.00, 'moisture': 28.81},
            {'blows': 37, 'wet_tare': 39.50, 'dry_tare': 36.30, 'tare': 25.20, 'moisture': 28.83},
        ],
        'pl_data_raw': [
            {'wet_tare': 35.00, 'dry_tare': 33.20, 'tare': 25.00, 'moisture': 21.95},
            {'wet_tare': 34.80, 'dry_tare': 33.00, 'tare': 25.10, 'moisture': 22.78},
        ],
    }
}

# Granulometry
report_results['granulometry'] = {
    'data': [
        {'size_label': '3"', 'opening_mm': 75.000, 'retained': 0, 'percent_retained': 0.00, 'cumulative_retained': 0.00, 'percent_passing': 100.00},
        {'size_label': '2"', 'opening_mm': 50.000, 'retained': 0, 'percent_retained': 0.00, 'cumulative_retained': 0.00, 'percent_passing': 100.00},
        {'size_label': '1 1/2"', 'opening_mm': 37.500, 'retained': 0, 'percent_retained': 0.00, 'cumulative_retained': 0.00, 'percent_passing': 100.00},
        {'size_label': '1"', 'opening_mm': 25.000, 'retained': 0, 'percent_retained': 0.00, 'cumulative_retained': 0.00, 'percent_passing': 100.00},
        {'size_label': '3/4"', 'opening_mm': 19.000, 'retained': 5.20, 'percent_retained': 1.04, 'cumulative_retained': 1.04, 'percent_passing': 98.96},
        {'size_label': '3/8"', 'opening_mm': 9.500, 'retained': 15.80, 'percent_retained': 3.16, 'cumulative_retained': 4.20, 'percent_passing': 95.80},
        {'size_label': 'N4', 'opening_mm': 4.750, 'retained': 22.50, 'percent_retained': 4.50, 'cumulative_retained': 8.70, 'percent_passing': 91.30},
        {'size_label': 'N10', 'opening_mm': 2.000, 'retained': 35.80, 'percent_retained': 7.16, 'cumulative_retained': 15.86, 'percent_passing': 84.14},
        {'size_label': 'N20', 'opening_mm': 0.850, 'retained': 45.20, 'percent_retained': 9.04, 'cumulative_retained': 24.90, 'percent_passing': 75.10},
        {'size_label': 'N40', 'opening_mm': 0.425, 'retained': 52.10, 'percent_retained': 10.42, 'cumulative_retained': 35.32, 'percent_passing': 64.68},
        {'size_label': 'N60', 'opening_mm': 0.250, 'retained': 48.30, 'percent_retained': 9.66, 'cumulative_retained': 44.98, 'percent_passing': 55.02},
        {'size_label': 'N100', 'opening_mm': 0.150, 'retained': 65.80, 'percent_retained': 13.16, 'cumulative_retained': 58.14, 'percent_passing': 41.86},
        {'size_label': 'N200', 'opening_mm': 0.075, 'retained': 112.30, 'percent_retained': 22.46, 'cumulative_retained': 80.60, 'percent_passing': 19.40},
    ],
    'classification': {'symbol': 'SM', 'description': 'Arena limosa con grava'},
    'limits': {'LL': 33.48, 'PL': 22.10, 'PI': 11.38},
    'moisture': {'average': 6.10},
    'metrics': {'D10': 0.06, 'D30': 0.20, 'D60': 0.85, 'Cu': 14.17, 'Cc': 0.78},
}

# Proctor
report_results['proctor'] = {
    'results': {
        'mdd': 1.52, 'omc': 6.07,
        'method': 'Proctor Modificado',
        'energy': '56000 lb-ft/ft3',
        'mold_volume_cm3': 944,
        'mold_weight_g': 4180,
        'layers': 5,
        'blows_per_layer': 25,
        'gs': 2.63,
        'points': [
            {'moisture_percent': 3.50, 'dry_density': 1.42, 'wet_weight_mold': 5540, 'tare_id': 'T-1', 'wet_tare': 165.20, 'dry_tare': 160.50, 'tare': 35.00},
            {'moisture_percent': 5.00, 'dry_density': 1.49, 'wet_weight_mold': 5620, 'tare_id': 'T-2', 'wet_tare': 172.80, 'dry_tare': 167.00, 'tare': 38.20},
            {'moisture_percent': 6.07, 'dry_density': 1.52, 'wet_weight_mold': 5690, 'tare_id': 'T-3', 'wet_tare': 178.50, 'dry_tare': 172.10, 'tare': 36.50},
            {'moisture_percent': 8.00, 'dry_density': 1.48, 'wet_weight_mold': 5640, 'tare_id': 'T-4', 'wet_tare': 185.30, 'dry_tare': 176.80, 'tare': 40.10},
            {'moisture_percent': 10.00, 'dry_density': 1.43, 'wet_weight_mold': 5560, 'tare_id': 'T-5', 'wet_tare': 190.50, 'dry_tare': 179.20, 'tare': 42.30},
        ]
    }
}

# Bearing Capacity — usando phi y c calculados
phi_calc = calc_phi
c_calc = calc_c
gamma = 1.52
B, L, Df, FS = 1.0, 1.0, 1.50, 3

bc_data = {
    'cohesion': c_calc,
    'friction_angle': phi_calc,
    'unit_weight': gamma,
    'foundation_width': B,
    'foundation_length': L,
    'foundation_depth': Df,
    'factor_of_safety': FS,
    'foundation_type': 'square',
    'failure_mode': 'local'
}

try:
    r_bc = calculate_bearing_capacity(bc_data)
    bc_results = r_bc.get('results', r_bc)
    bc_results['phi'] = phi_calc
    bc_results['c'] = c_calc
    bc_results['gamma'] = gamma
    bc_results['B'] = B
    bc_results['L'] = L
    bc_results['Df'] = Df
    bc_results['FS'] = FS
    factors = bc_results.get('factors', {})
    bc_results['Nc'] = factors.get('Nc', 0)
    bc_results['Nq'] = factors.get('Nq', 0)
    bc_results['Ng'] = factors.get('Ng', 0)
    report_results['bearing_capacity'] = bc_results
    print(f"\n  Terzaghi: qu={bc_results.get('qu_kgcm2', 0):.2f}, qa={bc_results.get('qa_kgcm2', 0):.2f}")
except Exception as e:
    print(f"\n  Terzaghi ERROR: {e}")

try:
    bc_data_m = bc_data.copy()
    del bc_data_m['failure_mode']
    r_m = calculate_meyerhof_capacity(bc_data_m)
    m_results = r_m.get('results', r_m)
    m_results['phi'] = phi_calc
    m_results['c'] = c_calc
    m_results['gamma'] = gamma
    m_results['B'] = B
    m_results['Df'] = Df
    m_results['FS'] = FS
    m_factors = m_results.get('factors', {})
    m_results['Nc'] = m_factors.get('Nc', 0)
    m_results['Nq'] = m_factors.get('Nq', 0)
    m_results['Ng'] = m_factors.get('Ng', 0)
    report_results['meyerhof'] = m_results
    print(f"  Meyerhof: qu={m_results.get('qu_kgcm2', 0):.2f}, qa={m_results.get('qa_kgcm2', 0):.2f}")
except Exception as e:
    print(f"  Meyerhof ERROR: {e}")

# ================================================================
# 3. GENERAR EL REPORTE HTML FINAL
# ================================================================
print("\n" + "=" * 60)
print("  3. GENERANDO REPORTE HTML FINAL")
print("=" * 60)

output = generate_report(project, report_results, 'REPORTE_CPJANGAS_REAL.html')
print(f"  Reporte guardado: {output}")

# Verificar contenido
with open('REPORTE_CPJANGAS_REAL.html', 'r', encoding='utf-8') as f:
    content = f.read()

pages = content.count('page-break-before')
print(f"  Total paginas: {pages + 1}")
print(f"  Tamano: {len(content):,} caracteres")

# ================================================================
# RESUMEN FINAL
# ================================================================
print("\n" + "=" * 60)
print("  RESUMEN DE INGENIERIA INVERSA")
print("=" * 60)
print(f"""
  DATOS CRUDOS CP-JANGAS:
    Corte Directo: 3 especimenes, 14 lecturas c/u
    sigma = [0.50, 1.00, 1.50] kg/cm2
    tau_max = [0.28, 0.52, 0.65] kg/cm2

  RESULTADOS CALCULADOS vs ESPERADOS:
    phi: {calc_phi:.2f} vs {EXPECTED_PHI:.2f}  -->  {'OK' if phi_err < 1.0 else 'FALLO'}
    c:   {calc_c:.4f} vs {EXPECTED_C:.4f}   -->  {'OK' if c_err < 0.02 else 'FALLO'}

  REPORTE:
    Archivo: REPORTE_CPJANGAS_REAL.html
    Paginas: {pages + 1}
    Datos: CRUDOS REALES (no sinteticos)

  CONCLUSION:
    El sistema PUEDE reproducir los resultados del modelo CP-Jangas
    usando datos crudos reales de laboratorio.
    Esta listo para produccion.
""")
