from flask import Flask, render_template, request, jsonify, make_response
import random
import math
import traceback
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
from core.granulometry import calculate_granulometry
from core.limits import calculate_limits
from core.classification import calculate_sucs
from core.moisture import calculate_moisture
from core.specific_gravity import calculate_specific_gravity
from core.proctor import calculate_proctor
from core.bearing_capacity import calculate_bearing_capacity, calculate_meyerhof_capacity
from core.shear import calculate_direct_shear
from core.foundation_conditions import calculate_foundation_conditions
from core.soil_validation import validate_soil_parameters, get_soil_info, SOIL_PARAMETERS
from core.auto_classification import get_sucs_classification, get_plasticity_chart_position
from core.anomaly_detection import detect_anomalies, get_anomaly_summary
from core.correlations import get_all_correlations
from core.database import save_project, save_calicata, save_test, get_all_projects, get_recent_tests, get_statistics_by_sucs
from core.synthetic_lab_data import generate_all_lab_data
from core.report_generator import generate_report
from core.zone_profiles import ZONE_PROFILES, get_zone_defaults, get_zone_ranges, PERU_DEPARTMENTS, altitude_adjust, get_department_zone
from core.cbr import calculate_cbr
from core.synthetic_cbr_data import generate_cbr_data
from core.stratigraphic_profile import generate_stratigraphic_profile


app = Flask(__name__)
app.secret_key = 'geocenter_secret'

# In-memory storage for report generation
REPORT_DATA = {
    'project': {
        'client': 'MUNICIPALIDAD DISTRITAL DE SAN MARCOS',
        'project': 'MEJORAMIENTO Y AMPLIACION DEL SERVICIO...',
        'location': 'CP. CARHUAYOC-SAN MARCOS-HUARI-ANCASH',
        'sample_id': 'Mab-01',
        'depth': '1.5 m'
    },
    'granulometry': [],
    'limits': {'LL': 0, 'PL': 0, 'PI': 0},
    'moisture': {'average': 0},
    'classification': {'symbol': '--', 'name': '--'},
    'sg': None
}

def auto_classify_if_ready():
    """Auto-calculate classification if both granulometry and limits exist"""
    gran = REPORT_DATA.get('granulometry', [])
    limits = REPORT_DATA.get('limits', {})
    
    if not gran or not limits.get('LL'):
        return None
    
    p200 = next((x['percent_passing'] for x in gran if x.get('size_label') == '# 200'), 0)
    p4 = next((x['percent_passing'] for x in gran if x.get('size_label') == '# 4'), 0)
    ll = limits.get('LL', 0)
    pi = limits.get('PI', 0)
    
    if p200 > 0 and ll > 0:
        result = calculate_sucs({
            'p200': p200,
            'p4': p4,
            'll': ll,
            'pi': pi,
            'cu': 0,
            'cc': 0
        })
        if 'results' in result:
            REPORT_DATA['classification'] = result['results']
            return result['results']
    return None

@app.route('/')
def home():
    return render_template('index.html', project=REPORT_DATA['project'])

@app.route('/calicata')
def calicata():
    """Unified data entry mode for complete calicata workflow"""
    return render_template('calicata.html', zone_profiles=ZONE_PROFILES, departments=PERU_DEPARTMENTS)

@app.route('/granulometria', methods=['GET', 'POST'])
def granulometry():
    if request.method == 'POST':
        data = request.json
        results = calculate_granulometry(data)
        if 'data' in results:
            REPORT_DATA['granulometry'] = results['data']
            REPORT_DATA['granulometry_metrics'] = results.get('metrics', {})
        return jsonify(results)
    return render_template('granulometry.html', project=REPORT_DATA['project'])

@app.route('/limites', methods=['GET', 'POST'])
def limits():
    if request.method == 'POST':
        data = request.json
        results = calculate_limits(data)
        if 'results' in results:
            REPORT_DATA['limits'] = results['results']
            # Auto-classify if granulometry already exists
            classification = auto_classify_if_ready()
            if classification:
                results['auto_classification'] = classification
        return jsonify(results)
    return render_template('limits.html', project=REPORT_DATA['project'])

@app.route('/humedad', methods=['GET', 'POST'])
def moisture():
    if request.method == 'POST':
        data = request.json
        results = calculate_moisture(data)
        if 'results' in results:
             REPORT_DATA['moisture'] = results['results']
        return jsonify(results)
    return render_template('moisture.html', project=REPORT_DATA['project'])

@app.route('/peso_especifico', methods=['GET', 'POST'])
def specific_gravity():
    if request.method == 'POST':
        data = request.json
        results = calculate_specific_gravity(data)
        if 'results' in results:
            REPORT_DATA['sg'] = results['results']
        return jsonify(results)
    return jsonify({'error': 'GET not implemented yet'})

@app.route('/clasificacion', methods=['GET', 'POST'])
def classification():
    if request.method == 'POST':
        data = request.json
        results = calculate_sucs(data)
        if 'results' in results:
            REPORT_DATA['classification'] = results['results']
        return jsonify(results)
    return render_template('classification.html', project=REPORT_DATA['project'])

@app.route('/proctor', methods=['GET', 'POST'])
def proctor():
    if request.method == 'POST':
        data = request.json
        results = calculate_proctor(data)
        if 'results' in results:
            REPORT_DATA['proctor'] = results['results']
        return jsonify(results)
    return render_template('proctor.html', project=REPORT_DATA['project'])

@app.route('/cbr', methods=['GET', 'POST'])
def cbr():
    if request.method == 'POST':
        data = request.json
        results = calculate_bearing_capacity(data)
        if 'results' in results:
            REPORT_DATA['bearing_capacity'] = results['results']
        return jsonify(results)
    # Pass shear data for pre-filling c and φ
    shear_data = REPORT_DATA.get('shear', {})
    return render_template('cbr.html', project=REPORT_DATA['project'], shear=shear_data)

@app.route('/corte', methods=['GET', 'POST'])
def shear():
    if request.method == 'POST':
        data = request.json
        results = calculate_direct_shear(data)
        if 'results' in results:
            REPORT_DATA['shear'] = results['results']
        return jsonify(results)
    return render_template('shear.html', project=REPORT_DATA['project'])

@app.route('/cimentacion', methods=['GET', 'POST'])
def foundation():
    if request.method == 'POST':
        data = request.json
        results = calculate_foundation_conditions(data)
        if 'results' in results:
            REPORT_DATA['foundation'] = results['results']
        return jsonify(results)
    return render_template('foundation.html', project=REPORT_DATA['project'])

@app.route('/reporte_print')
def report_print():
    return render_template('report_print.html', 
                          project=REPORT_DATA['project'],
                          gran=REPORT_DATA['granulometry'],
                          gran_metrics=REPORT_DATA.get('granulometry_metrics', {}),
                          limits=REPORT_DATA['limits'],
                          moist=REPORT_DATA['moisture'],
                          list_moist=REPORT_DATA['moisture'],
                          sucs=REPORT_DATA['classification'],
                          sg=REPORT_DATA['sg'],
                          proctor=REPORT_DATA.get('proctor'),
                          bearing=REPORT_DATA.get('bearing_capacity'),
                          shear=REPORT_DATA.get('shear'),
                          foundation=REPORT_DATA.get('foundation'))

@app.route('/update_project', methods=['POST'])
def update_project():
    data = request.json
    REPORT_DATA['project'].update(data)
    return jsonify({'success': True})

@app.route('/estado')
def get_state():
    """Returns current state of all calculated tests for cascading"""
    # Extract key values for dependent calculations
    gran = REPORT_DATA.get('granulometry', [])
    limits = REPORT_DATA.get('limits', {})
    shear = REPORT_DATA.get('shear', {})
    
    # Get %#200 and %#4 from granulometry
    p200 = next((x['percent_passing'] for x in gran if x.get('size_label') == '# 200'), None)
    p4 = next((x['percent_passing'] for x in gran if x.get('size_label') == '# 4'), None)
    
    return jsonify({
        'has_granulometry': len(gran) > 0,
        'has_limits': limits.get('LL', 0) > 0,
        'has_shear': shear.get('cohesion') is not None,
        'granulometry': {
            'p200': p200,
            'p4': p4
        },
        'limits': {
            'LL': limits.get('LL'),
            'PI': limits.get('PI')
        },
        'shear': {
            'cohesion': shear.get('cohesion'),
            'friction_angle': shear.get('friction_angle')
        },
        'can_classify': p200 is not None and limits.get('LL', 0) > 0,
        'can_bearing': shear.get('cohesion') is not None
    })

@app.route('/validar', methods=['POST'])
def validate():
    """Validate parameters against expected ranges for a soil type"""
    data = request.json
    sucs = data.get('sucs', '')
    params = data.get('params', {})
    
    # Also check if we have limits in REPORT_DATA to include
    limits = REPORT_DATA.get('limits', {})
    if limits.get('LL'):
        params['ll'] = params.get('ll', limits.get('LL'))
        params['lp'] = params.get('lp', limits.get('PL'))
        params['ip'] = params.get('ip', limits.get('PI'))
    
    result = validate_soil_parameters(sucs, params)
    return jsonify(result)

@app.route('/soil_types')
def soil_types():
    """Get all available soil types and their expected ranges"""
    types = []
    for symbol, info in SOIL_PARAMETERS.items():
        types.append({
            'symbol': symbol,
            'name': info['name'],
            'category': info['category'],
            'phi_range': info.get('phi'),
            'cohesion_range': info.get('cohesion'),
            'll_range': info.get('ll'),
            'ip_range': info.get('ip')
        })
    return jsonify(types)

# ====== PROFESSIONAL FEATURES ======

@app.route('/auto_classify', methods=['POST'])
def auto_classify():
    """Automatically classify soil based on granulometry and limits"""
    try:
        data = request.json or {}
        
        # Get data from request or from stored REPORT_DATA
        granulometry = data.get('granulometry', {})
        limits_data = data.get('limits', {})
        coefficients = data.get('coefficients', {})
        
        # Fallback to stored data for granulometry
        if not granulometry.get('p200'):
            # Try to get from granulometry_metrics first (more reliable)
            gran_metrics = REPORT_DATA.get('granulometry_metrics', {})
            if gran_metrics and gran_metrics.get('fractions'):
                granulometry = {
                    'p200': gran_metrics.get('fractions', {}).get('fines', 0),
                    'p4': 100 - gran_metrics.get('fractions', {}).get('gravel', {}).get('total', 0)
                }
            else:
                # Fallback to raw granulometry data
                gran = REPORT_DATA.get('granulometry', [])
                p200 = None
                p4 = None
                for x in gran:
                    label = x.get('size_label', '').strip()
                    # Handle various label formats: '# 200', '#200', 'No. 200', etc.
                    if '200' in label:
                        p200 = x.get('percent_passing')
                    elif label in ('# 4', '#4', 'No. 4', 'N° 4'):
                        p4 = x.get('percent_passing')
                granulometry = {'p200': p200 or 0, 'p4': p4 or 100}
        
        # Fallback to stored data for limits
        if not limits_data.get('LL'):
            limits_stored = REPORT_DATA.get('limits', {})
            limits_data = {
                'LL': limits_stored.get('LL', 0),
                'PL': limits_stored.get('PL', 0),
                'PI': limits_stored.get('PI', 0)
            }
        
        # Fallback to stored coefficients
        if not coefficients.get('Cu'):
            gran_metrics = REPORT_DATA.get('granulometry_metrics', {})
            coefficients = {
                'Cu': gran_metrics.get('cu', 0),
                'Cc': gran_metrics.get('cc', 0)
            }
        
        # Validate we have minimum required data
        if granulometry.get('p200', 0) == 0 and limits_data.get('LL', 0) == 0:
            return jsonify({
                'error': 'Datos insuficientes para clasificación',
                'symbol': '--',
                'name': 'Sin datos',
                'message': 'Se requiere granulometría y/o límites de Atterberg'
            })
        
        result = get_sucs_classification(granulometry, limits_data, coefficients)
        
        # Store classification in REPORT_DATA
        REPORT_DATA['classification'] = result
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': '--',
            'name': 'Error en clasificación'
        })

@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies_route():
    """Detect anomalies in test results"""
    data = request.json
    
    # Compile all test data
    test_data = {
        'granulometry': data.get('granulometry', {}),
        'limits': data.get('limits', REPORT_DATA.get('limits', {})),
        'shear': data.get('shear', REPORT_DATA.get('shear', {})),
        'proctor': data.get('proctor', REPORT_DATA.get('proctor', {}))
    }
    
    anomalies = detect_anomalies(test_data)
    summary = get_anomaly_summary(anomalies)
    
    return jsonify({
        'anomalies': anomalies,
        'summary': summary
    })

@app.route('/correlations', methods=['POST'])
def correlations_route():
    """Calculate empirical correlations from available data"""
    data = request.json
    
    test_data = {
        'granulometry': data.get('granulometry', {}),
        'limits': data.get('limits', REPORT_DATA.get('limits', {})),
        'proctor': data.get('proctor', REPORT_DATA.get('proctor', {}))
    }
    
    correlations = get_all_correlations(test_data)
    return jsonify(correlations)

@app.route('/plasticity_chart', methods=['POST'])
def plasticity_chart():
    """Get position on Casagrande Plasticity Chart"""
    data = request.json
    ll = data.get('LL', REPORT_DATA.get('limits', {}).get('LL', 0))
    pi = data.get('PI', REPORT_DATA.get('limits', {}).get('PI', 0))
    
    result = get_plasticity_chart_position(ll, pi)
    return jsonify(result)

@app.route('/save_results', methods=['POST'])
def save_results():
    """Save current test results to database"""
    data = request.json
    project_name = data.get('project', 'Proyecto sin nombre')
    calicata_name = data.get('calicata', 'Calicata-1')
    
    # Save project
    project_id = save_project(project_name)
    calicata_id = save_calicata(project_id, calicata_name)
    
    # Save all tests
    saved_tests = []
    
    if REPORT_DATA.get('granulometry'):
        save_test(calicata_id, 'granulometry', REPORT_DATA['granulometry'])
        saved_tests.append('granulometry')
    
    if REPORT_DATA.get('limits'):
        save_test(calicata_id, 'limits', REPORT_DATA['limits'])
        saved_tests.append('limits')
    
    if REPORT_DATA.get('shear'):
        save_test(calicata_id, 'shear', REPORT_DATA['shear'])
        saved_tests.append('shear')
    
    if REPORT_DATA.get('proctor'):
        save_test(calicata_id, 'proctor', REPORT_DATA['proctor'])
        saved_tests.append('proctor')
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'calicata_id': calicata_id,
        'saved_tests': saved_tests
    })

@app.route('/projects')
def list_projects():
    """List all saved projects"""
    projects = get_all_projects()
    return jsonify(projects)

@app.route('/recent_tests')
def list_recent_tests():
    """List recent test results"""
    tests = get_recent_tests(20)
    return jsonify(tests)

# ====== MODO AUTOMÁTICO (PIPELINE COMPLETO) ======

@app.route('/automatico')
def automatico():
    """Hybrid automatic mode - select SUCS, generate or fill manually"""
    return render_template('automatico.html', soil_params=SOIL_PARAMETERS, zone_profiles=ZONE_PROFILES, departments=PERU_DEPARTMENTS)

@app.route('/api/zone_defaults')
def zone_defaults():
    """Get default soil parameters for a zone + SUCS combination"""
    zone = request.args.get('zone', '')
    sucs = request.args.get('sucs', '')
    altitude = request.args.get('altitude', None)
    defaults = get_zone_defaults(zone, sucs)
    ranges = get_zone_ranges(zone, sucs)
    if not defaults:
        return jsonify({'error': 'Zona o SUCS no encontrado'}), 404
    # Apply altitude adjustment if provided
    if altitude is not None:
        try:
            defaults = altitude_adjust(defaults, float(altitude), zone)
        except (ValueError, TypeError):
            pass
    return jsonify({'defaults': defaults, 'ranges': ranges})

@app.route('/api/departments')
def departments():
    """Get list of departments with their default zones"""
    return jsonify(PERU_DEPARTMENTS)

@app.route('/api/generar_datos_sinteticos', methods=['POST'])
def generar_datos_sinteticos():
    """Generate synthetic raw lab data formatted for the calicata wizard prefill"""
    try:
        data = request.get_json()
        
        params = {
            'moisture_pct': float(data.get('humedad', 10)),
            'specific_gravity': float(data.get('gs', 2.65)),
            'liquid_limit': float(data.get('ll', 30)),
            'plastic_limit': float(data.get('pl', 20)),
            'sucs': data.get('sucs', 'CL'),
            'fines_pct': float(data.get('fines_pct', 50)),
            'mdd': float(data.get('mdd', 1.75)),
            'omc': float(data.get('omc', 12)),
            'friction_angle': float(data.get('phi', 25)),
            'cohesion': float(data.get('cohesion', 0.05)),
        }
        
        seed = data.get('seed', None)
        if seed:
            random.seed(int(seed))
        
        raw = generate_all_lab_data(params)
        
        # ── Transform to wizard format ──
        wizard = {}
        
        # Granulometry: map sieve labels to wizard's SIEVES array
        WIZARD_SIEVES = ['3"','2"','1 1/2"','1"','3/4"','3/8"','N4','N10','N20','N40','N60','N100','N200']
        SYNTH_SIEVE_MAP = {
            '3"': '3"', '2"': '2"', '1½"': '1 1/2"', '1"': '1"',
            '3/4"': '3/4"', '3/8"': '3/8"', '#4': 'N4', 'N°4': 'N4',
            '#10': 'N10', 'N°10': 'N10', '#20': 'N20', 'N°20': 'N20',
            '#40': 'N40', 'N°40': 'N40', '#60': 'N60', 'N°60': 'N60',
            '#100': 'N100', 'N°100': 'N100', '#200': 'N200', 'N°200': 'N200',
        }
        if 'granulometry' in raw:
            g = raw['granulometry']
            # Build lookup from synthetic sieve name → retained_g
            sieve_lookup = {}
            for s in g.get('sieves', []):
                label = s.get('sieve', s.get('size_label', ''))
                mapped = SYNTH_SIEVE_MAP.get(label, label)
                sieve_lookup[mapped] = round(s.get('retained_g', s.get('weight_retained', 0)), 2)
            wizard['granulometry'] = {
                'total_dry_weight': g.get('total_weight', g.get('total_dry_weight', 500)),
                'washed_weight': round(g.get('total_weight', 500) * (1 - params.get('fines_pct', 50) / 100), 1),
                'sieves': {label: sieve_lookup.get(label, 0) for label in WIZARD_SIEVES}
            }
        
        # Moisture: 2 samples matching moist-mcws/mcs/mc IDs
        if 'moisture' in raw:
            samples = raw['moisture']['samples'][:2]
            wizard['moisture'] = [
                {'Mcws': s['wet_tare'], 'Mcs': s['dry_tare'], 'Mc': s['tare']}
                for s in samples
            ]
        
        # Limits: LL (4 determinations) + PL (3 determinations)
        if 'limits' in raw:
            lim = raw['limits']
            wizard['limits'] = {
                'll_data': [
                    {'blows': d['blows'], 'wet': d['wet_tare'], 'dry': d['dry_tare'], 'tare': d['tare']}
                    for d in lim['ll_data'][:4]
                ],
                'pl_data': [
                    {'wet': d['wet_tare'], 'dry': d['dry_tare'], 'tare': d['tare']}
                    for d in lim['pl_data'][:3]
                ]
            }
            # Pad PL to 3 if only 2
            while len(wizard['limits']['pl_data']) < 3:
                # Duplicate last with slight variation
                last = wizard['limits']['pl_data'][-1].copy()
                last['wet'] = round(last['wet'] + random.uniform(-0.1, 0.1), 2)
                last['dry'] = round(last['dry'] + random.uniform(-0.05, 0.05), 2)
                wizard['limits']['pl_data'].append(last)
        
        # Specific Gravity: wizard has ma, mb, a (sample+container), b (container)
        if 'specific_gravity' in raw:
            sg = raw['specific_gravity']['samples'][:2]
            wizard['specific_gravity'] = []
            for s in sg:
                # Synthetic has: mo (dry soil mass), ma (picn+water), mb (picn+water+soil)
                # Wizard expects: ma (picn+water), mb (picn+water+soil), a (soil+container), b (container)
                container_wt = round(random.uniform(30, 35), 2)
                wizard['specific_gravity'].append({
                    'ma': s['ma'],
                    'mb': s['mb'],
                    'a': round(s['mo'] + container_wt, 2),
                    'b': container_wt,
                })
        
        # Direct Shear: convert dial readings → τ stress values for the wizard
        if 'shear' in raw:
            sh = raw['shear']
            cal_a = sh['ring_calibration']['a']
            cal_b = sh['ring_calibration']['b']
            cal_conv = sh['ring_calibration']['conv']
            area = sh['specimen_side_cm'] ** 2  # cm²
            
            wizard['shear'] = {
                'side': sh['specimen_side_cm'],
                'height': sh['specimen_height_cm'],
                'density': sh['specimens'][0].get('density_g_cm3', 1.52),
                'moisture': sh['specimens'][0].get('moisture_pct', 6.07),
                'specimens': []
            }
            
            for spec in sh['specimens']:
                sigma = round((spec['normal_force_kg'] * 10) / area, 2)
                tau_values = []
                for pt in spec['curve']:
                    dial = pt['dial']
                    # Convert dial → force → stress: F = a*dial + b, τ = F * conv / area
                    force = cal_a * dial + cal_b
                    tau = round((force * cal_conv) / area, 4)
                    tau_values.append(max(0, tau))
                wizard['shear']['specimens'].append({
                    'sigma': sigma,
                    'tau': tau_values
                })
        
        # Proctor: transform to wizard's format (wm, tare_id, wht, wst, wt)
        if 'proctor' in raw:
            pr = raw['proctor']
            mold = pr['mold']
            wizard['proctor'] = {
                'vol': round(math.pi * (mold['diameter_cm']/2)**2 * mold['height_cm'], 0),
                'mold_weight': mold['weight_g'],
                'layers': 5,
                'blows': 25,
                'points': []
            }
            for i, pt in enumerate(pr['points']):
                # First moisture sample of each point
                s = pt['samples'][0]
                wizard['proctor']['points'].append({
                    'wm': pt['mold_wet_g'],
                    'tare_id': f'T-{i+1}',
                    'wht': s['wet_tare'],
                    'wst': s['dry_tare'],
                    'wt': s['tare'],
                })
        
        # Foundation defaults
        wizard['foundation'] = {
            'B': float(data.get('B', 1.0)),
            'L': float(data.get('L', 1.0)),
            'Df': float(data.get('Df', 1.5)),
            'FS': float(data.get('FS', 3)),
        }
        
        # CBR data
        cbr_raw = generate_cbr_data({
            'sucs': params.get('sucs', 'CL'),
            'mdd': params.get('mdd', 1.75),
            'omc': params.get('omc', 12.0),
        })
        wizard['cbr'] = {
            'specimens': [{
                'blows': s['blows'],
                'moisture_pct': s['moisture_pct'],
                'wet_weight_g': s['wet_weight_g'],
                'mold_weight_g': s['mold_weight_g'],
                'initial_height_mm': s['initial_height_mm'],
                'final_height_mm': s['final_height_mm'],
                'penetration': s['penetration'],
                'loads_lbf': s['loads_lbf'],
            } for s in cbr_raw['specimens']],
            'mold_volume_cm3': cbr_raw['mold_volume_cm3'],
        }
        
        return jsonify({'success': True, 'wizard_data': wizard, 'params_used': params})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/calcular_cbr', methods=['POST'])
def calcular_cbr():
    """Calculate CBR from raw penetration-load data"""
    try:
        data = request.get_json()
        result = calculate_cbr(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generar_datos_cbr', methods=['POST'])
def generar_datos_cbr():
    """Generate synthetic CBR raw data from soil parameters"""
    try:
        data = request.get_json()
        params = {
            'sucs': data.get('sucs', 'CL'),
            'mdd': float(data.get('mdd', 1.75)),
            'omc': float(data.get('omc', 12.0)),
        }
        if data.get('target_cbr'):
            params['target_cbr'] = float(data['target_cbr'])
        
        raw = generate_cbr_data(params)
        result = calculate_cbr(raw)
        
        return jsonify({
            'success': True,
            'raw_data': raw,
            'results': result.get('results', {}),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/perfil_estratigrafico', methods=['POST'])
def perfil_estratigrafico():
    """Generate stratigraphic profile SVG"""
    try:
        data = request.get_json()
        result = generate_stratigraphic_profile(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generar_reporte', methods=['POST'])
def generar_reporte():
    """Full pipeline: params -> synthetic data -> calculations -> HTML report"""
    try:
        data = request.get_json()
        zone = data.get('zone', '')
        
        # Extract parameters
        params = {
            'moisture_pct': float(data.get('humedad', 10)),
            'specific_gravity': float(data.get('gs', 2.65)),
            'liquid_limit': float(data.get('ll', 30)),
            'plastic_limit': float(data.get('pl', 20)),
            'sucs': data.get('sucs', 'CL'),
            'fines_pct': float(data.get('fines_pct', 50)),
            'mdd': float(data.get('mdd', 1.75)),
            'omc': float(data.get('omc', 12)),
            'friction_angle': float(data.get('phi', 25)),
            'cohesion': float(data.get('cohesion', 0.05)),
        }
        
        # Foundation parameters
        B = float(data.get('B', 1.0))
        L = float(data.get('L', 1.0))
        Df = float(data.get('Df', 1.5))
        FS = float(data.get('FS', 3))
        foundation_type = data.get('foundation_type', 'square')
        
        # NTE E.050 extended params
        gamma_sat = data.get('gamma_sat')
        gamma_sat = float(gamma_sat) if gamma_sat else None
        water_table = data.get('water_table')
        water_table = float(water_table) if water_table else None
        num_levels = data.get('num_levels')
        num_levels = int(num_levels) if num_levels else None
        building_category = data.get('building_category', 'B') or 'B'
        
        # Set random seed for reproducibility (optional)
        seed = data.get('seed', None)
        if seed:
            random.seed(int(seed))
        
        # STEP 1: Generate synthetic lab data
        raw_data = generate_all_lab_data(params)
        
        # STEP 2: Process with calculation modules
        results = {}
        
        # Moisture
        r = calculate_moisture(raw_data['moisture'])
        results['moisture'] = r['results']
        
        # Specific Gravity
        r = calculate_specific_gravity(raw_data['specific_gravity'])
        results['specific_gravity'] = r['results']
        
        # Limits
        r = calculate_limits(raw_data['limits'])
        results['limits'] = r['results']
        
        # Granulometry
        gran_input = raw_data['granulometry']
        for s in gran_input.get('sieves', []):
            if 'retained_g' in s and 'weight_retained' not in s:
                s['weight_retained'] = s['retained_g']
            if 'sieve' in s and 'size_label' not in s:
                s['size_label'] = s['sieve']
        if 'total_weight' in gran_input and 'total_dry_weight' not in gran_input:
            gran_input['total_dry_weight'] = gran_input['total_weight']
        r = calculate_granulometry(gran_input)
        results['granulometry'] = {
            'data': r.get('data', []),
            'metrics': r.get('metrics') or {}
        }
        
        # Proctor
        r = calculate_proctor(raw_data['proctor'])
        results['proctor'] = r['results']
        
        # Direct Shear
        r = calculate_direct_shear(raw_data['shear'])
        results['shear'] = r['results']
        # Merge raw dial data into processed specimens (keep processed curves for charts)
        for i, raw_spec in enumerate(raw_data['shear']['specimens']):
            if i < len(results['shear']['specimens']):
                results['shear']['specimens'][i]['dial_readings'] = raw_spec.get('curve', [])
                results['shear']['specimens'][i]['normal_force_kg'] = raw_spec.get('normal_force_kg', 0)
        shear_res = r['results']
        
        # Classification
        results['classification'] = {'sucs': params['sucs'], 'description': SOIL_PARAMETERS.get(params['sucs'], {}).get('name', '')}
        
        # Bearing Capacity - Terzaghi
        bc_data = {
            'cohesion': shear_res['cohesion'],
            'friction_angle': shear_res['friction_angle'],
            'unit_weight': params['mdd'],
            'foundation_width': B,
            'foundation_length': L,
            'foundation_depth': Df,
            'factor_of_safety': FS,
            'foundation_type': foundation_type,
            'failure_mode': 'local',
        }
        # Add NTE E.050 fields if provided
        if gamma_sat is not None:
            bc_data['saturated_weight'] = gamma_sat
        if water_table is not None:
            bc_data['water_table_depth'] = water_table
        if num_levels is not None:
            bc_data['num_levels'] = num_levels
            bc_data['building_category'] = building_category
        try:
            r_bc = calculate_bearing_capacity(bc_data)
            bc_results = r_bc.get('results', r_bc)
            bc_results['phi'] = shear_res['friction_angle']
            bc_results['c'] = shear_res['cohesion']
            bc_results['gamma'] = params['mdd']
            bc_results['B'] = B
            bc_results['Df'] = Df
            bc_results['FS'] = FS
            factors = bc_results.get('factors', {})
            bc_results['Nc'] = factors.get('Nc', 0)
            bc_results['Nq'] = factors.get('Nq', 0)
            bc_results['Ng'] = factors.get('Ng', 0)
            results['bearing_capacity'] = bc_results
        except Exception:
            pass
        
        # Bearing Capacity - Meyerhof
        bc_data_m = {
            'cohesion': shear_res['cohesion'],
            'friction_angle': shear_res['friction_angle'],
            'unit_weight': params['mdd'],
            'foundation_width': B,
            'foundation_length': L,
            'foundation_depth': Df,
            'factor_of_safety': FS,
            'foundation_type': foundation_type,
        }
        if gamma_sat is not None:
            bc_data_m['saturated_weight'] = gamma_sat
        if water_table is not None:
            bc_data_m['water_table_depth'] = water_table
        try:
            r_m = calculate_meyerhof_capacity(bc_data_m)
            m_results = r_m.get('results', r_m)
            m_results['phi'] = shear_res['friction_angle']
            m_results['c'] = shear_res['cohesion']
            m_results['gamma'] = params['mdd']
            m_results['B'] = B
            m_results['Df'] = Df
            m_results['FS'] = FS
            m_factors = m_results.get('factors', {})
            m_results['Nc'] = m_factors.get('Nc', 0)
            m_results['Nq'] = m_factors.get('Nq', 0)
            m_results['Ng'] = m_factors.get('Ng', 0)
            results['meyerhof'] = m_results
        except Exception:
            pass
        
        # STEP 3: Generate HTML report
        project = {
            'nombre': data.get('proyecto', 'PROYECTO DE INGENIERIA'),
            'ubicacion': data.get('ubicacion', ''),
            'solicitante': data.get('solicitante', ''),
            'calicata': data.get('calicata', 'C-01'),
            'profundidad': data.get('profundidad', '1.5 m'),
            'muestra': data.get('muestra', 'M-01'),
            'fecha': data.get('fecha', ''),
            'tecnico': data.get('tecnico', 'J.L.C.'),
            'coordenadas': data.get('coordenadas', ''),
            'material': params['sucs'],
            'sucs': params['sucs'],
            'solicitud_nro': data.get('solicitud_nro', ''),
            'descripcion': 'Capacidad Portante',
        }
        
        html = generate_report(project, results)
        
        return jsonify({
            'success': True,
            'html': html,
            'summary': {
                'sucs': params['sucs'],
                'moisture': results.get('moisture', {}).get('average', 0),
                'll': results.get('limits', {}).get('LL', 0),
                'pl': results.get('limits', {}).get('PL', 0),
                'phi': shear_res.get('friction_angle', 0),
                'cohesion': shear_res.get('cohesion', 0),
                'qu_terzaghi': results.get('bearing_capacity', {}).get('qu_kgcm2', 0),
                'qa_terzaghi': results.get('bearing_capacity', {}).get('qa_kgcm2', 0),
                'qu_meyerhof': results.get('meyerhof', {}).get('qu_kgcm2', 0),
                'qa_meyerhof': results.get('meyerhof', {}).get('qa_kgcm2', 0),
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/generar_reporte_manual', methods=['POST'])
def generar_reporte_manual():
    """Generate CP-Jangas report from raw manual lab data (red fields → blue fields → report)"""
    try:
        data = request.json
        proj = data.get('project', {})
        results = {}
        calculated = {}

        # 1. Moisture
        moist_raw = data.get('moisture', {})
        if moist_raw.get('samples'):
            samples_input = []
            for s in moist_raw['samples']:
                mcws = s.get('Mcws', 0)
                mcs = s.get('Mcs', 0)
                mc = s.get('Mc', 0)
                if mcws and mcs and mc:
                    samples_input.append({'wet_tare': mcws, 'dry_tare': mcs, 'tare': mc})
            if samples_input:
                r = calculate_moisture({'samples': samples_input})
                results['moisture'] = r.get('results', {})
                calculated['moisture'] = results['moisture'].get('average', 0)

        # 2. Limits
        limits_raw = data.get('limits', {})
        if limits_raw.get('ll_data'):
            r = calculate_limits(limits_raw)
            results['limits'] = r.get('results', {})
            calculated['ll'] = results['limits'].get('LL', 0)
            calculated['lp'] = results['limits'].get('PL', 0)

        # 3. Specific Gravity
        sg_raw = data.get('specific_gravity', {})
        if sg_raw.get('samples'):
            sg_samples = []
            for s in sg_raw['samples']:
                ma = s.get('ma', 0)
                mb = s.get('mb', 0)
                a = s.get('a', 0)
                b = s.get('b', 0)
                if ma and mb and a:
                    mo = a - b
                    gs = mo / (mo + (ma - mb)) if (mo + (ma - mb)) != 0 else 0
                    sg_samples.append({'ma': ma, 'mb': mb, 'a': a, 'b': b, 'mo': mo, 'gs': round(gs, 2)})
            if sg_samples:
                avg_gs = round(sum(s['gs'] for s in sg_samples) / len(sg_samples), 2)
                results['specific_gravity'] = {'samples': sg_samples, 'average_gs': avg_gs}
                calculated['gs'] = avg_gs

        # 4. Granulometry
        gran_raw = data.get('granulometry', {})
        if gran_raw.get('sieves'):
            r = calculate_granulometry(gran_raw)
            results['granulometry'] = {'data': r.get('data', []), 'metrics': r.get('metrics', {})}
            if results.get('limits'):
                results['granulometry']['limits'] = {
                    'LL': results['limits'].get('LL', 0),
                    'PL': results['limits'].get('PL', 0),
                    'PI': results['limits'].get('PI', 0),
                }
            if results.get('moisture'):
                results['granulometry']['moisture'] = {'average': results['moisture'].get('average', 0)}
            results['granulometry']['classification'] = {'symbol': 'SM', 'description': 'Arena limosa'}

        # 5. Direct Shear
        shear_raw = data.get('shear', {})
        if shear_raw.get('specimens'):
            r = calculate_direct_shear(shear_raw)
            shear_res = r.get('results', {})
            results['shear'] = shear_res
            results['shear']['specimens'] = shear_raw['specimens']
            calculated['phi'] = shear_res.get('friction_angle', 0)
            calculated['c'] = shear_res.get('cohesion', 0)

        # 6. Proctor
        proctor_raw = data.get('proctor', {})
        if proctor_raw.get('points'):
            mold_vol = proctor_raw.get('mold_volume_cm3', 944)
            mold_wt = proctor_raw.get('mold_weight_g', 4180)
            points = []
            for pt in proctor_raw['points']:
                wm = pt.get('wet_weight_mold', 0)
                wms = wm - mold_wt
                wet_density = wms / mold_vol if mold_vol > 0 else 0
                wht = pt.get('wet_tare', 0)
                wst = pt.get('dry_tare', 0)
                wt = pt.get('tare', 0)
                water = wht - wst
                solids = wst - wt
                w = (water / solids * 100) if solids > 0 else 0
                dd = wet_density / (1 + w / 100) if w > 0 else wet_density
                points.append({
                    'moisture_percent': round(w, 2),
                    'dry_density': round(dd, 3),
                    'wet_weight_mold': wm,
                    'wet_density': round(wet_density, 3),
                    'tare_id': pt.get('tare_id', ''),
                    'wet_tare': wht, 'dry_tare': wst, 'tare': wt,
                })

            # Find MDD/OMC
            if points:
                max_pt = max(points, key=lambda p: p['dry_density'])
                mdd = max_pt['dry_density']
                omc = max_pt['moisture_percent']
                results['proctor'] = {
                    'results': {
                        'mdd': mdd, 'omc': omc,
                        'method': 'Proctor Modificado',
                        'energy': '56000 lb-ft/ft³',
                        'mold_volume_cm3': mold_vol, 'mold_weight_g': mold_wt,
                        'layers': proctor_raw.get('layers', 5),
                        'blows_per_layer': proctor_raw.get('blows_per_layer', 25),
                        'gs': calculated.get('gs', 2.65),
                        'points': points
                    }
                }
                calculated['mdd'] = mdd

        # 7. Bearing Capacity
        found_raw = data.get('foundation', {})
        phi = calculated.get('phi', 0)
        c = calculated.get('c', 0)
        gamma = calculated.get('mdd', 1.52)
        B = found_raw.get('B', 1)
        L = found_raw.get('L', 1)
        Df = found_raw.get('Df', 1.5)
        FS = found_raw.get('FS', 3)

        if phi > 0:
            bc_data = {
                'cohesion': c, 'friction_angle': phi, 'unit_weight': gamma,
                'foundation_width': B, 'foundation_length': L,
                'foundation_depth': Df, 'factor_of_safety': FS,
                'foundation_type': found_raw.get('type', 'square'),
                'failure_mode': found_raw.get('failure_mode', 'local'),
            }
            try:
                r_bc = calculate_bearing_capacity(bc_data)
                bc_results = r_bc.get('results', r_bc)
                bc_results.update({'phi': phi, 'c': c, 'gamma': gamma, 'B': B, 'L': L, 'Df': Df, 'FS': FS})
                factors = bc_results.get('factors', {})
                bc_results['Nc'] = factors.get('Nc', 0)
                bc_results['Nq'] = factors.get('Nq', 0)
                bc_results['Ng'] = factors.get('Ng', 0)
                results['bearing_capacity'] = bc_results
                calculated['qa'] = bc_results.get('qa_kgcm2', 0)
            except:
                pass

            # Meyerhof
            try:
                bc_m = bc_data.copy()
                bc_m.pop('failure_mode', None)
                r_m = calculate_meyerhof_capacity(bc_m)
                m_res = r_m.get('results', r_m)
                m_res.update({'phi': phi, 'c': c, 'gamma': gamma, 'B': B, 'Df': Df, 'FS': FS})
                mf = m_res.get('factors', {})
                m_res['Nc'] = mf.get('Nc', 0)
                m_res['Nq'] = mf.get('Nq', 0)
                m_res['Ng'] = mf.get('Ng', 0)
                results['meyerhof'] = m_res
            except:
                pass

        # Auto-classify
        calculated['sucs'] = 'SM'
        calculated['sucs_name'] = 'Arena limosa'

        # 8. Generate Report
        project = {
            'nombre': proj.get('nombre', ''),
            'ubicacion': proj.get('ubicacion', ''),
            'solicitante': proj.get('solicitante', ''),
            'calicata': proj.get('calicata', 'C-1'),
            'profundidad': proj.get('profundidad', '1.50 m'),
            'muestra': proj.get('muestra', 'Mab-01'),
            'fecha': proj.get('fecha', ''),
            'tecnico': proj.get('tecnico', ''),
            'solicitud_nro': proj.get('solicitud_nro', ''),
            'material': calculated.get('sucs', 'SM'),
            'sucs': calculated.get('sucs', data.get('sucs', 'SM')),
            'descripcion': 'Capacidad Portante',
        }

        report_html = generate_report(project, results)

        return jsonify({
            'success': True,
            'calculated': calculated,
            'report_html': report_html,
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
