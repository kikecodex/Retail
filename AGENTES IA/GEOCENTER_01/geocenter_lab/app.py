from flask import Flask, render_template, request, jsonify, make_response
import random
import traceback
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
    return render_template('calicata.html')

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
    return render_template('automatico.html', soil_params=SOIL_PARAMETERS)

@app.route('/api/generar_reporte', methods=['POST'])
def generar_reporte():
    """Full pipeline: params -> synthetic data -> calculations -> HTML report"""
    try:
        data = request.get_json()
        
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
        results['shear']['specimens'] = raw_data['shear']['specimens']
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
            'failure_mode': 'local'
        }
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
