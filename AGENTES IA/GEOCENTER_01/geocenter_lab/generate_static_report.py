from flask import Flask, render_template
import sys
import os
sys.path.append(os.getcwd())
from app import app, REPORT_DATA
from core.granulometry import calculate_granulometry
from core.limits import calculate_limits
from core.classification import calculate_sucs
from core.moisture import calculate_moisture
from core.specific_gravity import calculate_specific_gravity

# Mimic Populate Server Logic
# 1. Granulometry
total_weight = 3000 # Approx from excel
gran_sieves = [
    {'size_label': '3"', 'opening_mm': 75.0, 'weight_retained': 0},
    {'size_label': '1 1/2"', 'opening_mm': 37.5, 'weight_retained': 0},
    {'size_label': '3/4"', 'opening_mm': 19.0, 'weight_retained': 150},
    {'size_label': '3/8"', 'opening_mm': 9.5, 'weight_retained': 200},
    {'size_label': '# 4', 'opening_mm': 4.75, 'weight_retained': 300},
    {'size_label': '# 8', 'opening_mm': 2.36, 'weight_retained': 250},
    {'size_label': '# 16', 'opening_mm': 1.18, 'weight_retained': 200},
    {'size_label': '# 30', 'opening_mm': 0.60, 'weight_retained': 150},
    {'size_label': '# 50', 'opening_mm': 0.30, 'weight_retained': 100},
    {'size_label': '# 100', 'opening_mm': 0.15, 'weight_retained': 50},
    {'size_label': '# 200', 'opening_mm': 0.075, 'weight_retained': 20}
]
gran_payload = {'total_dry_weight': total_weight, 'sieves': gran_sieves}
gran_res = calculate_granulometry(gran_payload)
REPORT_DATA['granulometry'] = gran_res['data']
REPORT_DATA['granulometry_metrics'] = gran_res.get('metrics', {})

# 2. Limits
ll_data = [
    {'blows': 35, 'wet_tare': 45.0, 'dry_tare': 40.0, 'tare': 20.0},
    {'blows': 25, 'wet_tare': 46.0, 'dry_tare': 40.0, 'tare': 20.0},
    {'blows': 15, 'wet_tare': 48.0, 'dry_tare': 40.0, 'tare': 20.0}
]
pl_data = [
    {'wet_tare': 28.0, 'dry_tare': 27.0, 'tare': 20.0},
    {'wet_tare': 28.1, 'dry_tare': 27.1, 'tare': 20.0}
]
limits_payload = {'ll_data': ll_data, 'pl_data': pl_data}
lim_res = calculate_limits(limits_payload)
REPORT_DATA['limits'] = lim_res['results']

# 3. Moisture
moisture_samples = [{'wet_tare': 195.6, 'dry_tare': 188.2, 'tare': 24.5}]
moist_payload = {'samples': moisture_samples}
moist_res = calculate_moisture(moist_payload)
REPORT_DATA['moisture'] = moist_res['results']

# 4. SG
sg_samples = [{'id': 'M-01', 'ma': 658.90, 'mb': 738.50, 'mo': 130.00, 'tare': 0.0}]
sg_payload = {'samples': sg_samples}
sg_res = calculate_specific_gravity(sg_payload)
REPORT_DATA['sg'] = sg_res['results']

# 5. Classification
if 'fractions' in REPORT_DATA['granulometry_metrics']:
    p200 = REPORT_DATA['granulometry_metrics']['fractions']['fines']
    p4 = 100 - REPORT_DATA['granulometry_metrics']['fractions']['gravel']['total'] # approx
else:
    p200, p4 = 10, 80

sucs_payload = {
    'p200': p200, 'p4': p4,
    'll': REPORT_DATA['limits']['LL'],
    'pi': REPORT_DATA['limits']['PI'],
    'cu': REPORT_DATA['granulometry_metrics'].get('cu', 0),
    'cc': REPORT_DATA['granulometry_metrics'].get('cc', 0)
}
sucs_res = calculate_sucs(sucs_payload)
REPORT_DATA['classification'] = sucs_res['results']


# Render
with app.app_context():
    html = render_template('report_print.html', 
                          project=REPORT_DATA['project'],
                          gran=REPORT_DATA['granulometry'],
                          gran_metrics=REPORT_DATA.get('granulometry_metrics', {}),
                          limits=REPORT_DATA['limits'],
                          moist=REPORT_DATA['moisture'],
                          list_moist=REPORT_DATA['moisture'], 
                          sucs=REPORT_DATA['classification'],
                          sg=REPORT_DATA['sg'])
    
    output_path = r'c:\Users\Hp\Desktop\GEOCENTER_01\reporte_generado.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report generated at: {output_path}")
