"""
GEOCENTER LAB — Generador de Reportes HTML Completo
Genera un reporte multi-página A4 idéntico al formato ENSAYOS.xlsx
con tablas ASTM y gráficos Chart.js.
"""
import json
import math
import os
try:
    from soil_validation import SOIL_PARAMETERS
except ImportError:
    from core.soil_validation import SOIL_PARAMETERS


def generate_report(project, results, output_path=None):
    """
    Genera reporte HTML completo.
    
    Args:
        project: dict con datos del proyecto
        results: dict con resultados procesados de cada ensayo
        output_path: ruta donde guardar el HTML (opcional, si None retorna string)
    """
    sucs = project.get('sucs', project.get('material', 'SM'))
    p = {
        'nombre': project.get('nombre', 'PROYECTO DE INGENIERIA'),
        'ubicacion': project.get('ubicacion', ''),
        'solicitante': project.get('solicitante', ''),
        'calicata': project.get('calicata', 'C-01'),
        'profundidad': project.get('profundidad', '1.5 m'),
        'muestra': project.get('muestra', 'M-01'),
        'fecha': project.get('fecha', ''),
        'tecnico': project.get('tecnico', 'J.L.C.'),
        'coordenadas': project.get('coordenadas', ''),
        'material': project.get('material', ''),
        'solicitud_nro': project.get('solicitud_nro', 'J-001-2025'),
        'descripcion': project.get('descripcion', 'Capacidad Portante'),
        'sucs': sucs,
    }
    
    pages = []
    page_num = 1
    total_pages = _count_pages(results)
    
    # Page 1: Granulometría + Límites
    if 'granulometry' in results:
        pages.append(_page_granulometry(p, results, page_num, total_pages))
        page_num += 1
    
    # Page 2: Humedad
    if 'moisture' in results:
        pages.append(_page_moisture(p, results['moisture'], page_num, total_pages))
        page_num += 1
    
    # Page 3: Límites detalle
    if 'limits' in results:
        pages.append(_page_limits(p, results['limits'], page_num, total_pages))
        page_num += 1
    
    # Page 4: Peso Específico
    if 'specific_gravity' in results:
        pages.append(_page_sg(p, results['specific_gravity'], page_num, total_pages))
        page_num += 1
    
    # Pages 5-6: Corte Directo (data + charts)
    if 'shear' in results:
        pages.append(_page_shear(p, results['shear'], page_num, total_pages))
        page_num += 2  # shear generates 2 pages
    
    # Page 6: Proctor
    if 'proctor' in results:
        pages.append(_page_proctor(p, results['proctor'], page_num, total_pages))
        page_num += 1
    
    # Page 7: Capacidad Portante (Terzaghi)
    if 'bearing_capacity' in results:
        pages.append(_page_bearing(p, results['bearing_capacity'], page_num, total_pages))
        page_num += 1
    
    # Page 8: Capacidad Portante (Meyerhof) + Asentamiento
    if 'meyerhof' in results:
        pages.append(_page_meyerhof(p, results['meyerhof'], results.get('bearing_capacity', {}), page_num, total_pages))
        page_num += 1
    
    # Page: CBR
    if 'cbr' in results:
        pages.append(_page_cbr(p, results['cbr'], page_num, total_pages))
        page_num += 1
    
    html = _wrap_html(pages, results)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path
    
    return html


def _count_pages(results):
    count = 0
    for key in ['granulometry', 'moisture', 'limits', 'specific_gravity', 'shear', 'proctor', 'bearing_capacity', 'meyerhof', 'cbr']:
        if key in results:
            count += 2 if key == 'shear' else 1  # shear generates 2 pages
    return count


def _project_header(p, titulo, norma, page_num, total_pages):
    return f'''
    <div class="text-center font-bold mb-4 relative">
        <div class="absolute top-0 right-0 border border-black px-2 text-xs">Solicitud N° {p['solicitud_nro']}</div>
        <h2 class="text-lg uppercase">{titulo}</h2>
        <div class="text-xs">{norma}</div>
        <div class="text-xs text-right mt-2">Pag. {page_num:02d} de {total_pages:02d}</div>
    </div>
    <table class="mb-4 text-xs">
        <tr class="border-t border-l border-r border-black">
            <td class="font-bold w-24 p-1">Proyecto</td>
            <td colspan="3" class="p-1 uppercase">: {p['nombre']}</td>
        </tr>
        <tr class="border-l border-r border-black">
            <td class="font-bold p-1">Solicita</td>
            <td class="p-1 uppercase">: {p['solicitante']}</td>
            <td class="font-bold w-24 text-right p-1">Fecha :</td>
            <td class="w-32 p-1">{p['fecha']}</td>
        </tr>
        <tr class="border-b border-l border-r border-black">
            <td class="font-bold p-1">Lugar</td>
            <td class="p-1 uppercase">: {p['ubicacion']}</td>
            <td class="font-bold text-right p-1">Tecnico :</td>
            <td class="p-1">{p['tecnico']}</td>
        </tr>
    </table>
    <table class="mb-4 text-xs text-center font-bold">
        <tr class="bg-gray-200">
            <td class="border border-black p-1">Descripción : {p['descripcion']}</td>
            <td class="border border-black p-1">Coordenadas : {p['coordenadas']}</td>
            <td class="border border-black p-1">Material : {p['material']}</td>
        </tr>
        <tr>
            <td class="border border-black p-1">Calicata : {p['calicata']}</td>
            <td class="border border-black p-1">Muestra : {p['muestra']}</td>
            <td class="border border-black p-1">Profundidad : {p['profundidad']}</td>
        </tr>
    </table>'''


def _footer():
    return '''
    <div class="mt-12 flex justify-between px-10 text-center text-xs">
        <div class="w-40 border-t border-black pt-2"><strong>Realizado por:</strong><br>Tec. de Laboratorio</div>
        <div class="w-40 border-t border-black pt-2"><strong>Revisado por:</strong><br>Jefe de Laboratorio</div>
        <div class="w-40 border-t border-black pt-2"><strong>Aprobado por:</strong><br>Ing. Civil</div>
    </div>'''


def _methodology_box(norma, nivel, origen, procedimiento, formula, resultado, sucs, param_checks):
    """
    Genera bloque HTML de fundamentación técnica con trazabilidad.
    
    Args:
        norma: str - "ASTM D3080 / NTP 339.171"
        nivel: str - "Primario", "Derivado", "Calculado"
        origen: str - de dónde provienen los datos
        procedimiento: str - descripción breve del método
        formula: str - ecuación principal (puede incluir HTML)
        resultado: str - "φ = 31.0°, c = 0.30 kg/cm²"
        sucs: str - tipo SUCS ("SM")
        param_checks: list of (label, value, soil_key, unit) tuples
    """
    nivel_icons = {'Primario': '🟢', 'Derivado': '🟡', 'Calculado': '🔴'}
    nivel_icon = nivel_icons.get(nivel, '⚪')
    
    soil = SOIL_PARAMETERS.get(sucs, {})
    soil_name = soil.get('name', sucs)
    
    # Build validation rows
    validation_rows = ''
    all_in_range = True
    for label, value, soil_key, unit in param_checks:
        rng = soil.get(soil_key)
        if rng and value is not None:
            try:
                val = float(value)
                in_range = rng[0] <= val <= rng[1]
                icon = '✅' if in_range else '⚠️'
                if not in_range:
                    all_in_range = False
                validation_rows += f'<div style="margin-left:12px;">{icon} {label} = {val}{unit} — rango esperado: ({rng[0]} – {rng[1]}{unit})</div>'
            except (ValueError, TypeError):
                pass
    
    status_icon = '✅' if all_in_range else '⚠️'
    status_text = 'Valores dentro del rango esperado' if all_in_range else 'Algunos valores fuera del rango esperado'
    status_color = '#065f46' if all_in_range else '#92400e'
    status_bg = '#d1fae5' if all_in_range else '#fef3c7'
    
    return f'''
    <div style="border: 1.5px solid #374151; border-radius: 6px; padding: 8px 12px; margin-top: 8px; font-size: 8px; line-height: 1.4; background: #f9fafb;">
        <div style="font-weight:bold; font-size:9px; margin-bottom:4px; color:#1f2937;">📋 FUNDAMENTACIÓN TÉCNICA</div>
        <div><strong>Norma:</strong> {norma}</div>
        <div><strong>Nivel:</strong> {nivel_icon} {nivel}</div>
        <div style="margin-top:3px;"><strong>🔗 Origen de datos:</strong> {origen}</div>
        <div style="margin-top:3px;"><strong>Procedimiento:</strong> {procedimiento}</div>
        <div style="margin-top:3px;"><strong>Fórmula:</strong> {formula}</div>
        <div style="margin-top:3px;"><strong>Resultado:</strong> {resultado}</div>
        <div style="margin-top:6px; padding:4px 8px; border-radius:4px; background:{status_bg}; color:{status_color}; font-weight:bold;">
            {status_icon} {status_text} para {sucs} ({soil_name})
        </div>
        {validation_rows}
    </div>'''

# ===================== AASHTO CLASSIFICATION =====================

def _estimate_aashto(gravel_pct, sand_pct, fines_pct, ll, pi):
    """Estimate AASHTO classification from granulometry and plasticity data."""
    # Convert to numeric, handle string/None
    try:
        ll_n = float(ll) if ll and ll != '---' else 0
    except (ValueError, TypeError):
        ll_n = 0
    try:
        pi_n = float(pi) if pi and pi != '---' else 0
    except (ValueError, TypeError):
        pi_n = 0
    
    p200 = fines_pct  # % passing #200
    p4 = sand_pct + fines_pct  # approximate % passing #4
    
    # AASHTO M 145 Classification
    if p200 <= 35:
        # Granular materials (A-1, A-2, A-3)
        if p200 <= 15 and pi_n <= 6:
            if p4 <= 50:
                return {'symbol': 'A-1-a', 'description': 'Fragmentos de roca, grava y arena'}
            else:
                return {'symbol': 'A-1-b', 'description': 'Grava y arena arcillosa o limosa'}
        elif p200 <= 10 and pi_n == 0:
            return {'symbol': 'A-3', 'description': 'Arena fina'}
        else:
            # A-2 group
            if pi_n <= 10:
                if ll_n <= 40:
                    return {'symbol': 'A-2-4', 'description': 'Grava y arena limosa o arcillosa'}
                else:
                    return {'symbol': 'A-2-5', 'description': 'Grava y arena limosa o arcillosa'}
            else:
                if ll_n <= 40:
                    return {'symbol': 'A-2-6', 'description': 'Grava y arena arcillosa'}
                else:
                    return {'symbol': 'A-2-7', 'description': 'Grava y arena arcillosa'}
    else:
        # Silt-clay materials (A-4 to A-7)
        if ll_n <= 40:
            if pi_n <= 10:
                return {'symbol': 'A-4', 'description': 'Suelos limosos'}
            else:
                return {'symbol': 'A-6', 'description': 'Suelos arcillosos'}
        else:
            if pi_n <= 10:
                return {'symbol': 'A-5', 'description': 'Suelos limosos'}
            elif pi_n <= (ll_n - 30):
                return {'symbol': 'A-7-5', 'description': 'Suelos arcillosos'}
            else:
                return {'symbol': 'A-7-6', 'description': 'Suelos arcillosos'}

# ===================== PAGE GENERATORS =====================

def _page_granulometry(p, results, pn, tp):
    gran = results.get('granulometry', {})
    data = gran.get('data', gran.get('sieves', []))
    metrics = gran.get('metrics') or {}
    limits = results.get('limits', {})
    classification = results.get('classification', {})
    moisture = results.get('moisture', {})
    
    # Extract values
    w_avg = moisture.get('average', moisture.get('results', {}).get('average', 0))
    ll_val = limits.get('LL', limits.get('results', {}).get('LL', '---'))
    pl_val = limits.get('PL', limits.get('results', {}).get('PL', '---'))
    pi_val = limits.get('PI', limits.get('results', {}).get('PI', '---'))
    
    fractions = metrics.get('fractions', {})
    gravel = fractions.get('gravel', {}) if isinstance(fractions.get('gravel'), dict) else {}
    sand = fractions.get('sand', {}) if isinstance(fractions.get('sand'), dict) else {}
    gravel_pct = gravel.get('total', 0)
    gravel_coarse = gravel.get('coarse', 0)
    gravel_fine = gravel.get('fine', 0)
    sand_pct = sand.get('total', 0)
    sand_coarse = sand.get('coarse', 0)
    sand_medium = sand.get('medium', 0)
    sand_fine = sand.get('fine', 0)
    fines_pct = fractions.get('fines', 0) if not isinstance(fractions.get('fines'), dict) else 0
    
    d10 = metrics.get('d10', '--')
    d30 = metrics.get('d30', '--')
    d60 = metrics.get('d60', '--')
    cu = metrics.get('cu', '--')
    cc = metrics.get('cc', '--')
    
    # Format numeric values
    d10_str = f"{d10:.2f}" if isinstance(d10, (int, float)) else '--'
    d30_str = f"{d30:.2f}" if isinstance(d30, (int, float)) else '--'
    d60_str = f"{d60:.2f}" if isinstance(d60, (int, float)) else '--'
    cu_str = f"{cu:.2f}" if isinstance(cu, (int, float)) else '--'
    cc_str = f"{cc:.2f}" if isinstance(cc, (int, float)) else '--'
    
    # Total weight and washed weight
    total_weight = sum(s.get('weight_retained', s.get('retained_g', 0)) for s in data)
    
    # Sieve categories for reference
    sieve_cats = {
        75.0: ('BOLONES', ''), 37.5: ('GRAVA', 'Gruesa'), 19.0: ('GRAVA', 'Gruesa'),
        9.5: ('GRAVA', 'Gruesa'), 4.75: ('GRAVA', 'Fina'),
        2.36: ('ARENA', 'Gruesa'), 2.0: ('ARENA', 'Gruesa'),
        1.18: ('ARENA', 'Media'), 0.6: ('ARENA', 'Media'), 0.425: ('ARENA', 'Media'),
        0.3: ('ARENA', 'Fina'), 0.15: ('ARENA', 'Fina'), 0.075: ('ARENA', 'Fina')
    }
    
    # Build sieve rows with categories
    rows = ''
    last_cat = ''
    for s in data:
        name = s.get('size_label', s.get('sieve', ''))
        opening = s.get('opening_mm', 0)
        ret = s.get('weight_retained', s.get('retained_g', 0))
        pct_ret = s.get('percent_retained', 0)
        cum_ret = s.get('cumulative_retained', 0)
        pct_pass = s.get('percent_passing', 0)
        
        cat_info = sieve_cats.get(opening, ('', ''))
        cat = cat_info[0]
        subcat = cat_info[1]
        
        # Category header row
        if cat and cat != last_cat:
            cat_colors = {
                'BOLONES': 'bg-gray-600 text-white',
                'GRAVA': 'bg-amber-600 text-white',
                'ARENA': 'bg-yellow-500 text-white',
                'LIMOS Y ARCILLA': 'bg-blue-600 text-white',
            }
            rows += f'''<tr class="{cat_colors.get(cat, 'bg-gray-200')}">
                <td colspan="6" class="p-1 font-bold text-[9px] uppercase text-center">{cat}</td>
            </tr>'''
            last_cat = cat
        
        rows += f'''<tr class="border-b border-gray-300">
            <td class="border-r border-gray-400 p-1 text-center font-bold">{name}</td>
            <td class="border-r border-gray-400 p-1 text-center">{opening:.3f}</td>
            <td class="border-r border-gray-400 p-1 text-center">{ret:.2f}</td>
            <td class="border-r border-gray-400 p-1 text-center">{pct_ret:.2f}</td>
            <td class="border-r border-gray-400 p-1 text-center">{cum_ret:.2f}</td>
            <td class="p-1 text-center font-bold bg-yellow-50">{pct_pass:.2f}</td>
        </tr>'''
    
    # Add LIMOS Y ARCILLA row
    rows += f'''<tr class="bg-blue-600 text-white">
        <td colspan="6" class="p-1 font-bold text-[9px] uppercase text-center">LIMOS Y ARCILLA</td>
    </tr>
    <tr class="border-b border-black bg-blue-50">
        <td class="border-r border-gray-400 p-1 text-center font-bold">&lt; 200</td>
        <td class="border-r border-gray-400 p-1 text-center">0.000</td>
        <td class="border-r border-gray-400 p-1 text-center">--</td>
        <td class="border-r border-gray-400 p-1 text-center">{fines_pct:.2f}</td>
        <td class="border-r border-gray-400 p-1 text-center">100.00</td>
        <td class="p-1 text-center font-bold bg-yellow-50">0.00</td>
    </tr>'''
    
    # SUCS classification
    sucs_symbol = classification.get('sucs', '')
    sucs_desc = classification.get('description', '')
    cls_gran = metrics.get('classification', {})
    if cls_gran:
        sucs_symbol = sucs_symbol or cls_gran.get('symbol', p.get('material', ''))
        sucs_desc = sucs_desc or cls_gran.get('name', '')
    if not sucs_symbol:
        sucs_symbol = p.get('material', '')
    
    # AASHTO classification (estimated from fractions)
    aashto = _estimate_aashto(gravel_pct, sand_pct, fines_pct, ll_val, pi_val)
    
    return f'''
    <div class="a4-page">
        <!-- HEADER -->
        <div class="flex items-center justify-between border-2 border-black p-2 mb-2">
            <div class="w-1/4 text-center border-r-2 border-black p-2">
                <h1 class="text-2xl font-bold text-blue-900 leading-none">GEOCENTER</h1>
                <div class="text-[9px] text-gray-600">INGENIERIA & CONSTRUCCION</div>
            </div>
            <div class="w-3/4 px-4 text-center">
                <h2 class="text-base font-bold">ENSAYO DE MECÁNICA DE SUELOS</h2>
                <div class="text-[10px]">Granulometría, Límites de Consistencia y Clasificación SUCS</div>
            </div>
        </div>
        
        <!-- PROJECT INFO -->
        <table class="text-[10px] w-full mb-2 border border-black">
            <tr><td class="bg-gray-100 p-1 font-bold border-r border-black w-24">PROYECTO:</td><td colspan="3" class="p-1 uppercase">{p['nombre']}</td></tr>
            <tr><td class="bg-gray-100 p-1 font-bold border-r border-black">UBICACIÓN:</td><td colspan="3" class="p-1 uppercase">{p['ubicacion']}</td></tr>
            <tr><td class="bg-gray-100 p-1 font-bold border-r border-black">SOLICITANTE:</td><td colspan="3" class="p-1 uppercase">{p['solicitante']}</td></tr>
            <tr><td class="bg-gray-100 p-1 font-bold border-r border-black">CALICATA:</td><td class="p-1 uppercase">{p['calicata']}</td>
                <td class="bg-gray-100 p-1 font-bold border-r border-black w-24">PROFUNDIDAD:</td><td class="p-1">{p['profundidad']}</td></tr>
        </table>
        
        <!-- DESCRIPCIÓN DE LA MUESTRA -->
        <div class="text-[9px] font-bold text-center bg-gray-200 border border-black p-1 mb-1">DESCRIPCIÓN DE LA MUESTRA</div>
        <table class="text-[9px] w-full mb-2 border border-black">
            <tr>
                <td class="bg-gray-50 p-1 border-r border-black font-bold">Masa Inicial (seco/gr):</td>
                <td class="p-1 text-center border-r border-black">{total_weight:.2f}</td>
                <td class="bg-gray-50 p-1 border-r border-black font-bold">% que pasa N°200:</td>
                <td class="p-1 text-center border-r border-black font-bold text-red-600">{fines_pct:.2f}</td>
            </tr>
            <tr>
                <td class="bg-gray-50 p-1 border-r border-black font-bold">Masa Lavada y Secada:</td>
                <td class="p-1 text-center border-r border-black">{total_weight * (1 - fines_pct/100):.2f}</td>
                <td class="bg-gray-50 p-1 border-r border-black font-bold">Tamaño Máx:</td>
                <td class="p-1 text-center">{data[0].get('size_label', '3"') if data else '3"'}</td>
            </tr>
        </table>

        <!-- SIEVE TABLE -->
        <table class="text-[9px] text-center border-collapse border-2 border-black w-full font-medium mb-2">
            <thead class="bg-gray-200 font-bold">
                <tr>
                    <td class="border border-black p-1" rowspan="2">Tamiz<br>ASTM E11</td>
                    <td class="border border-black p-1" rowspan="2">Abertura<br>mm</td>
                    <td class="border border-black p-1" colspan="2">RETENIDO EN CADA TAMIZ</td>
                    <td class="border border-black p-1" colspan="2">PORCENTAJE ACUMULADO</td>
                </tr>
                <tr>
                    <td class="border border-black p-1">Masa (gr)</td>
                    <td class="border border-black p-1">%</td>
                    <td class="border border-black p-1">Retenido</td>
                    <td class="border border-black p-1 bg-yellow-100">Pasante</td>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>

        <!-- CHART + DESCRIPTION SIDE BY SIDE -->
        <div class="flex gap-2 mb-2">
            <!-- Granulometry Chart -->
            <div class="w-7/12 border-2 border-black relative bg-white" style="height:280px;">
                <div class="text-[9px] font-bold text-center bg-gray-200 border-b border-black p-0.5">Granulometría</div>
                <canvas id="printGranChart"></canvas>
            </div>
            
            <!-- DESCRIPTION + CLASSIFICATION -->
            <div class="w-5/12 flex flex-col gap-1 text-[9px]">
                <!-- DESCRIPCIÓN DE DATOS -->
                <div class="border-2 border-black">
                    <div class="font-bold text-center bg-gray-200 py-1 border-b border-black">DESCRIPCIÓN DE DATOS</div>
                    <table class="w-full">
                        <tr class="border-b border-gray-300"><td class="bg-gray-50 p-1 font-bold">Limite Líquido, LL:</td><td class="p-1 text-right font-bold">{ll_val}</td></tr>
                        <tr class="border-b border-gray-300"><td class="bg-gray-50 p-1 font-bold">Limite Plástico, LP:</td><td class="p-1 text-right font-bold">{pl_val}</td></tr>
                        <tr class="border-b border-gray-300"><td class="bg-gray-50 p-1 font-bold">Ind. de plasticidad IP:</td><td class="p-1 text-right font-bold">{pi_val}</td></tr>
                        <tr class="border-b border-black"><td class="bg-gray-50 p-1 font-bold">Cont. Humedad (%):</td><td class="p-1 text-right font-bold">{w_avg}</td></tr>
                    </table>
                </div>
                
                <!-- CLASIFICACIÓN SUCS -->
                <div class="border-2 border-black">
                    <div class="font-bold text-center bg-gray-200 py-1 border-b border-black">Clasificación SUCS</div>
                    <div class="p-2 text-center">
                        <span class="font-bold text-red-700 text-sm">{sucs_symbol}</span>
                        <div class="text-[8px] mt-1">{sucs_desc}</div>
                    </div>
                </div>
                
                <!-- CLASIFICACIÓN AASHTO -->
                <div class="border-2 border-black">
                    <div class="font-bold text-center bg-gray-200 py-1 border-b border-black">Clasificación AASHTO</div>
                    <div class="p-2 text-center">
                        <span class="font-bold text-blue-700 text-sm">{aashto['symbol']}</span>
                        <div class="text-[8px] mt-1">{aashto['description']}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- CUADRO RESUMEN DE FRACCIONES -->
        <table class="text-[9px] border-2 border-black font-bold w-full text-center">
            <tr class="border-b border-black">
                <td class="bg-amber-100 p-1 border-r border-black w-16" rowspan="2">% GRAVA</td>
                <td class="bg-amber-50 p-1 border-r border-black w-12 text-base" rowspan="2">{gravel_pct:.2f}</td>
                <td class="bg-gray-50 p-1 border-r border-black">% Gruesa</td>
                <td class="p-1 border-r border-black">{gravel_coarse:.2f}</td>
                <td class="bg-gray-100 p-1 border-r border-black">D60 (mm) =</td>
                <td class="p-1 border-r border-black">{d60_str}</td>
            </tr>
            <tr class="border-b border-black">
                <td class="bg-gray-50 p-1 border-r border-black">% Fina</td>
                <td class="p-1 border-r border-black">{gravel_fine:.2f}</td>
                <td class="bg-gray-100 p-1 border-r border-black">D30 (mm) =</td>
                <td class="p-1 border-r border-black">{d30_str}</td>
            </tr>
            <tr class="border-b border-black">
                <td class="bg-yellow-100 p-1 border-r border-black" rowspan="3">% ARENA</td>
                <td class="bg-yellow-50 p-1 border-r border-black text-base" rowspan="3">{sand_pct:.2f}</td>
                <td class="bg-gray-50 p-1 border-r border-black">% Gruesa</td>
                <td class="p-1 border-r border-black">{sand_coarse:.2f}</td>
                <td class="bg-gray-100 p-1 border-r border-black">D10 (mm) =</td>
                <td class="p-1 border-r border-black">{d10_str}</td>
            </tr>
            <tr class="border-b border-black">
                <td class="bg-gray-50 p-1 border-r border-black">% Media</td>
                <td class="p-1 border-r border-black">{sand_medium:.2f}</td>
                <td class="bg-gray-100 p-1 border-r border-black">Coeficiente uniformidad (Cu) =</td>
                <td class="p-1 border-r border-black">{cu_str}</td>
            </tr>
            <tr class="border-b border-black">
                <td class="bg-gray-50 p-1 border-r border-black">% Fina</td>
                <td class="p-1 border-r border-black">{sand_fine:.2f}</td>
                <td class="bg-gray-100 p-1 border-r border-black">Coeficiente curvatura (Cc) =</td>
                <td class="p-1 border-r border-black">{cc_str}</td>
            </tr>
            <tr>
                <td class="bg-blue-100 p-1 border-r border-black">% FINOS</td>
                <td class="bg-blue-50 p-1 border-r border-black text-base">{fines_pct:.2f}</td>
                <td colspan="4"></td>
            </tr>
        </table>
        {_methodology_box(
            norma='NTP 339.128-1999',
            nivel='Primario',
            origen='Ensayo directo de laboratorio — tamizado mecánico por mallas ASTM',
            procedimiento='Se tamió la muestra por mallas estándar y se determinó el porcentaje pasante acumulado para clasificación SUCS',
            formula='% Pasante = (Peso pasante acumulado / Peso total) × 100',
            resultado=f'% Finos = {fines_pct:.1f}%, Gravas = {gravel_pct:.1f}%, Arena = {sand_pct:.1f}%',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('% Finos', fines_pct, 'finos_percent', '%')]
        )}
    </div>'''


def _page_moisture(p, moisture, pn, tp):
    samples = moisture.get('samples', moisture.get('results', {}).get('samples', []))
    avg = moisture.get('average', moisture.get('results', {}).get('average', 0))

    cols_header = ''
    rows_wt = rows_dt = rows_t = rows_ms = rows_mw = rows_w = ''
    n_samples = min(len(samples), 3)
    for i, s in enumerate(samples[:3]):
        wt = s.get('wet_tare', 0)
        dt = s.get('dry_tare', 0)
        t = s.get('tare', 0)
        ms = round(dt - t, 2)
        mw = round(wt - dt, 2)
        wp = s.get('w_percent', round(mw / ms * 100, 2) if ms > 0 else 0)
        cols_header += f'<td class="p-2 border-r border-black font-bold text-center">M-{i+1:02d}</td>'
        rows_wt += f'<td class="p-1 border-r border-black text-center">{wt:.2f}</td>'
        rows_dt += f'<td class="p-1 border-r border-black text-center">{dt:.2f}</td>'
        rows_t += f'<td class="p-1 border-r border-black text-center">{t:.2f}</td>'
        rows_ms += f'<td class="p-1 border-r border-black text-center bg-blue-50">{ms:.2f}</td>'
        rows_mw += f'<td class="p-1 border-r border-black text-center bg-blue-50">{mw:.2f}</td>'
        rows_w += f'<td class="p-1 border-r border-black text-center bg-blue-50 font-bold">{wp:.2f}</td>'

    col_span = n_samples if n_samples > 0 else 1

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Determinación del Contenido de Humedad del Suelo', '(NTP 339.127-1998)', pn, tp)}
        <table class="text-xs border-collapse border-2 border-black w-full text-center mb-4">
            <thead><tr class="font-bold border-b-2 border-black bg-gray-100">
                <td class="p-2 border-r border-black uppercase text-center" colspan="2">DESCRIPCION</td>{cols_header}
            </tr></thead>
            <tbody>
                <tr class="border-b border-black"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Peso Suelo Húmedo + Contenedor</td><td class="p-1 border-r border-black font-bold w-12">Mcws</td>{rows_wt}</tr>
                <tr class="border-b border-black"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Peso Suelo Seco + Contenedor</td><td class="p-1 border-r border-black font-bold w-12">Mcs</td>{rows_dt}</tr>
                <tr class="border-b border-black"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Peso Contenedor</td><td class="p-1 border-r border-black font-bold w-12">Mc</td>{rows_t}</tr>
                <tr class="border-b border-black bg-blue-50"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Peso Suelo Seco (Ms=Mcs - Mc)</td><td class="p-1 border-r border-black font-bold w-12">Ms</td>{rows_ms}</tr>
                <tr class="border-b border-black bg-blue-50"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Peso del Agua (Mw=Mcws - Mcs)</td><td class="p-1 border-r border-black font-bold w-12">Mw</td>{rows_mw}</tr>
                <tr class="border-b-2 border-black bg-blue-50"><td class="text-left p-1 border-r border-black pl-2" colspan="1">Contenido de Humedad (w=Mw/Ms)</td><td class="p-1 border-r border-black font-bold w-12">w</td>{rows_w}</tr>
            </tbody>
        </table>
        <div class="border-2 border-black">
            <table class="w-full text-sm font-bold text-center">
                <tr><td class="bg-gray-100 p-3 border-r border-black w-2/3 uppercase">Humedad Promedio (%)</td><td class="p-3 text-lg">{avg}</td></tr>
            </table>
        </div>
        {_methodology_box(
            norma='NTP 339.127-1998',
            nivel='Primario',
            origen='Ensayo directo de laboratorio — secado en horno a 110±5°C por 24 horas',
            procedimiento='Se pesaron 3 muestras húmedas, se secaron en horno y se repesaron para determinar el agua evaporada',
            formula='w (%) = (Mw / Ms) × 100, donde Mw = peso del agua, Ms = peso del suelo seco',
            resultado=f'Humedad promedio = {avg}%',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('Humedad', avg, 'humedad', '%')]
        )}
        {_footer()}
    </div>'''


def _page_limits(p, limits, pn, tp):
    r = limits.get('results', limits)
    ll_pts = r.get('ll_data_raw', r.get('ll_points', []))
    pl_pts = r.get('pl_data_raw', [])
    ll = r.get('LL', 0)
    pl = r.get('PL', 0)
    pi = r.get('PI', 0)
    
    # LL table rows
    n_ll = len(ll_pts)
    header_ll = ''.join(f'<td class="p-1 border-l border-black">{i+1}</td>' for i in range(n_ll))
    blows_r = ''.join(f'<td class="p-1 border-l border-black font-bold">{pt.get("blows",0)}</td>' for pt in ll_pts)
    wt_r = ''.join(f'<td class="p-1 border-l border-black">{pt.get("wet_tare",0)}</td>' for pt in ll_pts)
    dt_r = ''.join(f'<td class="p-1 border-l border-black">{pt.get("dry_tare",0)}</td>' for pt in ll_pts)
    t_r = ''.join(f'<td class="p-1 border-l border-black">{pt.get("tare",0)}</td>' for pt in ll_pts)
    water_r = ''.join(f'<td class="p-1 border-l border-black">{round(pt.get("wet_tare",0)-pt.get("dry_tare",0),2)}</td>' for pt in ll_pts)
    solid_r = ''.join(f'<td class="p-1 border-l border-black">{round(pt.get("dry_tare",0)-pt.get("tare",0),2)}</td>' for pt in ll_pts)
    moist_r = ''.join(f'<td class="p-1 border-l border-black">{pt.get("moisture", round((pt.get("wet_tare",0)-pt.get("dry_tare",0))/(pt.get("dry_tare",0)-pt.get("tare",0))*100,2) if pt.get("dry_tare",0)-pt.get("tare",0)>0 else 0)}</td>' for pt in ll_pts)
    
    # PL table rows
    n_pl = len(pl_pts)
    header_pl = ''.join(f'<td class="p-1 border-l border-black">{i+1}</td>' for i in range(n_pl))
    wt_pl = ''.join(f'<td class="p-1 border-l border-black">{pt.get("wet_tare",0)}</td>' for pt in pl_pts)
    dt_pl = ''.join(f'<td class="p-1 border-l border-black">{pt.get("dry_tare",0)}</td>' for pt in pl_pts)
    t_pl = ''.join(f'<td class="p-1 border-l border-black">{pt.get("tare",0)}</td>' for pt in pl_pts)
    water_pl = ''.join(f'<td class="p-1 border-l border-black">{round(pt.get("wet_tare",0)-pt.get("dry_tare",0),2)}</td>' for pt in pl_pts)
    solid_pl = ''.join(f'<td class="p-1 border-l border-black">{round(pt.get("dry_tare",0)-pt.get("tare",0),2)}</td>' for pt in pl_pts)
    moist_pl = ''.join(f'<td class="p-1 border-l border-black">{pt.get("moisture", round((pt.get("wet_tare",0)-pt.get("dry_tare",0))/(pt.get("dry_tare",0)-pt.get("tare",0))*100,2) if pt.get("dry_tare",0)-pt.get("tare",0)>0 else 0)}</td>' for pt in pl_pts)

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Límite Líquido, Límite Plástico e Indice de Plasticidad de Suelos', '(NTP 339.129-1999)', pn, tp)}
        <div class="text-center font-bold text-xs mb-2">DETERMINACIÓN DEL LÍMITE LÍQUIDO</div>
        <div class="flex mb-6">
            <div class="w-1/2 pr-2">
                <table class="text-xs border border-black w-full text-center">
                    <tr class="border-b border-black"><td class="p-1 border-r border-black w-1/3">ENSAYO / DATOS</td><td class="p-1" colspan="{n_ll}">LÍMITE LÍQUIDO</td></tr>
                    <tr class="border-b border-black font-bold bg-gray-100"><td class="p-1 border-r border-black text-left pl-2">N° de frasco</td>{header_ll}</tr>
                    <tr class="border-b border-black"><td class="p-1 border-r border-black text-left pl-2">N° de golpes</td>{blows_r}</tr>
                    <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(1) P. Suelo Húmedo + Rec.</td>{wt_r}</tr>
                    <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(2) P. Suelo Seco + Rec.</td>{dt_r}</tr>
                    <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(3) Peso del Recipiente</td>{t_r}</tr>
                    <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(4) Peso del agua (1)-(2)</td>{water_r}</tr>
                    <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(5) P. Suelo Seco (2)-(3)</td>{solid_r}</tr>
                    <tr class="border-b border-black"><td class="p-1 border-r border-black text-left pl-2">(6) C. Humedad (%) (4)/(5)</td>{moist_r}</tr>
                </table>
            </div>
            <div class="w-1/2 pl-2 border border-black h-64 relative bg-white">
                <div class="text-xs text-center font-bold absolute top-2 w-full">LÍMITE LÍQUIDO</div>
                <canvas id="page3LLChart"></canvas>
            </div>
        </div>
        <div class="text-center font-bold text-xs mb-2">DETERMINACIÓN DEL LÍMITE PLÁSTICO</div>
        <div class="w-3/4 mx-auto mb-6">
            <table class="text-xs border border-black w-full text-center">
                <tr class="border-b border-black"><td class="p-1 border-r border-black w-1/3">ENSAYO / DATOS</td><td class="p-1" colspan="{n_pl}">LIMITE PLÁSTICO</td></tr>
                <tr class="border-b border-black font-bold bg-gray-100"><td class="p-1 border-r border-black text-left pl-2">N° de frasco</td>{header_pl}</tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(1) P. Suelo Húmedo + Rec.</td>{wt_pl}</tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(2) P. Suelo Seco + Rec.</td>{dt_pl}</tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(3) Peso del Recipiente</td>{t_pl}</tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(4) Peso del agua (1)-(2)</td>{water_pl}</tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2">(5) P. Suelo Seco (2)-(3)</td>{solid_pl}</tr>
                <tr class="border-b border-black"><td class="p-1 border-r border-black text-left pl-2">(6) C. Humedad (%) (4)/(5)</td>{moist_pl}</tr>
            </table>
        </div>
        <div class="border border-black flex text-xs font-bold">
            <div class="flex-1 p-2 border-r border-black text-center">Límite Liquido (L.L.) = {ll}</div>
            <div class="flex-1 p-2 border-r border-black text-center">Límite Plástico (L.P.) = {pl}</div>
            <div class="flex-1 p-2 text-center">Indice Plasticidad (I.P.) = {pi}</div>
        </div>
        {_methodology_box(
            norma='NTP 339.129-1999 / NTP 339.130-1999',
            nivel='Derivado',
            origen=f'Cartilla GEOCENTER v2 para {p.get("sucs", "SM")} — valores objetivo de LL y LP generados por ingeniería inversa',
            procedimiento='LL: Copa de Casagrande con 4 puntos a diferentes humedades. LP: Rollitos de 3mm hasta agrietamiento',
            formula='IP = LL - LP (ASTM D4318)',
            resultado=f'LL = {ll}, LP = {pl}, IP = {pi}',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('LL', ll, 'll', ''), ('LP', pl, 'lp', ''), ('IP', pi, 'ip', '')]
        )}
    </div>'''


def _page_sg(p, sg, pn, tp):
    samples = sg.get('samples', sg.get('results', {}).get('samples', []))
    avg_gs = sg.get('average_gs', sg.get('results', {}).get('average_gs', 0))

    cols_h = ''.join(f'<td class="border-r border-black p-2 font-bold text-center">M-{i+1:02d}</td>' for i in range(len(samples)))

    # Build data rows — input fields and calculated fields
    rows_portion = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("portion", "Pasa Malla #4")}</td>' for s in samples)
    rows_flask = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("flask_type", "Picnometro 500 ml")}</td>' for s in samples)
    rows_ma = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("ma",0):.2f}</td>' for s in samples)
    rows_mb = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("mb",0):.2f}</td>' for s in samples)
    rows_a = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("a", s.get("mo",0) + s.get("b",0)):.2f}</td>' for s in samples)
    rows_b = ''.join(f'<td class="border-r border-black p-1 text-center">{s.get("b",0):.2f}</td>' for s in samples)
    rows_mo = ''.join(f'<td class="border-r border-black p-1 text-center bg-blue-50 font-bold">{s.get("mo",0):.2f}</td>' for s in samples)
    rows_gs = ''.join(f'<td class="border-r border-black p-2 text-center bg-blue-50 font-bold">{s.get("gs",0):.2f}</td>' for s in samples)

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Peso Específico Relativo de las Partículas Sólidas de un Suelo', '(NTP 339.131-1998)', pn, tp)}
        <div class="border-2 border-black mb-4">
            <table class="w-full text-xs text-center border-collapse">
                <thead class="font-bold border-b-2 border-black bg-gray-100">
                    <tr><td class="border-r border-black p-2 text-left pl-4">MUESTRA DE ENSAYO</td>{cols_h}</tr>
                </thead>
                <tbody>
                    <tr class="border-b border-gray-300"><td class="border-r border-black p-1 text-left pl-4">Porcion de muestra de ensayo</td>{rows_portion}</tr>
                    <tr class="border-b border-black"><td class="border-r border-black p-1 text-left pl-4">Tipo de frasco Utilizado</td>{rows_flask}</tr>
                    <tr class="border-b border-gray-300"><td class="border-r border-black p-1 text-left pl-4">Masa picnometro + agua</td><td class="border-r border-black p-1 text-left pl-4 text-center" style="display:table-cell">(Ma)</td>{rows_ma}</tr>
                    <tr class="border-b border-gray-300"><td class="border-r border-black p-1 text-left pl-4">Masa picnometro + agua + suelo</td><td class="border-r border-black p-1 text-center">(Mb)</td>{rows_mb}</tr>
                    <tr class="border-b border-gray-300"><td class="border-r border-black p-1 text-left pl-4">Masa muestra seco al horno + recip.</td><td class="border-r border-black p-1 text-center">gr (A)</td>{rows_a}</tr>
                    <tr class="border-b border-gray-300"><td class="border-r border-black p-1 text-left pl-4">Masa recipiente</td><td class="border-r border-black p-1 text-center">gr (B)</td>{rows_b}</tr>
                    <tr class="border-b border-black bg-blue-50"><td class="border-r border-black p-1 text-left pl-4 font-bold">Masa muestra de suelo seco al horno (Mo=A-B)</td><td class="border-r border-black p-1 text-center">gr (Mo)</td>{rows_mo}</tr>
                    <tr class="bg-blue-50"><td class="border-r border-black p-2 text-left pl-4 font-bold">Peso Especifico Relativo de Solidos (Gs=Mo/(Mo+(Ma-Mb)))</td><td class="border-r border-black p-2 text-center"></td>{rows_gs}</tr>
                </tbody>
            </table>
        </div>
        <div class="border-2 border-black">
            <table class="w-full text-sm font-bold text-center">
                <tr><td class="bg-gray-100 p-3 border-r border-black w-2/3 uppercase">Peso Especifico Relativo de Solidos (Gs)</td><td class="p-3 text-lg">{avg_gs}</td></tr>
            </table>
        </div>
        {_methodology_box(
            norma='NTP 339.131-1998',
            nivel='Derivado',
            origen=f'Cartilla GEOCENTER v2 para {p.get("sucs", "SM")} — valor objetivo generado por ingeniería inversa',
            procedimiento='Se determinó el peso específico con picnómetro de 500 ml, comparando masa de suelo seco con volumen desplazado de agua',
            formula='Gs = Mo / (Mo + Ma - Mb), donde Mo = masa suelo seco, Ma = masa picnómetro+agua, Mb = masa picnómetro+agua+suelo',
            resultado=f'Gs promedio = {avg_gs}',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('Gs', avg_gs, 'peso_especifico', '')]
        )}
        {_footer()}
    </div>'''


def _page_shear(p, shear, pn, tp):
    r = shear.get('results', shear)
    phi = r.get('friction_angle', 0)
    c = r.get('cohesion', 0)
    specimens = r.get('specimens', shear.get('specimens', []))
    gamma_d = r.get('dry_density', specimens[0].get('dry_density', 0) if specimens else 0)
    w_pct = r.get('moisture_pct', specimens[0].get('moisture_pct', 0) if specimens else 0)

    n_spec = len(specimens)
    labels = ['A', 'B', 'C', 'D'][:n_spec]

    # --- PAGE 5: DATA TABLE ---
    # Specimen header
    spec_cols = ''.join(f'<td class="p-1 border-r border-black font-bold text-center">{labels[i]}</td>' for i in range(n_spec))

    # Build specimen parameter rows
    def spec_row(label, key, default=0, fmt='.2f'):
        cells = ''.join(f'<td class="p-1 border-r border-black text-center">{sp.get(key, default):{fmt}}</td>' for sp in specimens)
        return f'<tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2 font-bold">{label}</td>{cells}</tr>'

    params_rows = ''
    params_rows += spec_row('Lado (cm)', 'side_cm', 6.00)
    params_rows += spec_row('Altura (cm)', 'height_cm', 2.54)
    params_rows += spec_row('Densidad Seca (gr/cm3)', 'dry_density', gamma_d)
    params_rows += spec_row('humedad Inicial (%)', 'moisture_pct', w_pct)

    # Saturation humidity (calculated)
    sat_cells = ''.join(f'<td class="p-1 border-r border-black text-center bg-blue-50">{sp.get("saturation_moisture", 0):.2f}</td>' for sp in specimens)
    params_rows += f'<tr class="border-b border-gray-300 bg-blue-50"><td class="p-1 border-r border-black text-left pl-2 font-bold">humedad Saturación (%)</td>{sat_cells}</tr>'

    # Normal stress
    sigma_cells = ''.join(f'<td class="p-1 border-r border-black text-center font-bold">{sp.get("normal_stress", 0):.2f}</td>' for sp in specimens)
    params_rows += f'<tr class="border-b border-black"><td class="p-1 border-r border-black text-left pl-2 font-bold">Esfuerzo Normal (Kg/cm2)</td>{sigma_cells}</tr>'

    # Deformation table header
    gn_labels = ''.join(f'<td class="p-1 border-r border-black font-bold text-center bg-gray-100">Gn= {sp.get("normal_stress", 0):.2f}</td>' for sp in specimens)

    # Build deformation rows from curve data
    deform_rows = ''
    # Get all unique strain values across specimens
    all_strains = set()
    for sp in specimens:
        for pt in sp.get('curve', []):
            all_strains.add(round(pt.get('strain_pct', 0), 2))
    all_strains = sorted(all_strains)

    for strain in all_strains:
        cells = ''
        for sp in specimens:
            curve = sp.get('curve', [])
            tau = 0
            for pt in curve:
                if abs(pt.get('strain_pct', 0) - strain) < 0.01:
                    tau = pt.get('shear_stress', 0)
                    break
            cells += f'<td class="p-1 border-r border-black text-center">{tau:.2f}</td>'
        deform_rows += f'<tr class="border-b border-gray-200"><td class="p-1 border-r border-black text-center">{strain:.2f}</td>{cells}</tr>'

    # Final results row
    phi_row = f'<tr class="border-t-2 border-black bg-blue-50 font-bold"><td class="p-1 border-r border-black text-left pl-2">Angulo deFricción Interna del suelo (°)</td><td colspan="{n_spec}" class="p-1 text-center text-lg">{phi}</td></tr>'
    c_row = f'<tr class="border-t border-black bg-blue-50 font-bold"><td class="p-1 border-r border-black text-left pl-2">Cohesión Aparente del Suelo (Kg/cm2)</td><td colspan="{n_spec}" class="p-1 text-center text-lg">{c}</td></tr>'

    page5 = f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Ensayo de Corte Directo', '(ASTM D3080)', pn, tp)}
        <!-- Specimen Parameters -->
        <table class="text-[10px] border-collapse border-2 border-black w-full text-center mb-2">
            <thead><tr class="bg-gray-100 font-bold border-b-2 border-black">
                <td class="p-1 border-r border-black text-left pl-2">Especimen</td>{spec_cols}
            </tr></thead>
            <tbody>{params_rows}</tbody>
        </table>

        <!-- Deformation Table -->
        <table class="text-[9px] border-collapse border-2 border-black w-full text-center mb-2">
            <thead>
                <tr class="bg-gray-100 border-b border-black">
                    <td class="p-1 border-r border-black font-bold" rowspan="2">Deformación Unitaria<br>(ξ - %)</td>
                    {gn_labels}
                </tr>
                <tr class="bg-gray-50 border-b-2 border-black">
                    {''.join(f'<td class="p-1 border-r border-black">Esfuerzo Cortante<br>(kg/cm2)</td>' for _ in specimens)}
                </tr>
            </thead>
            <tbody>{deform_rows}</tbody>
        </table>

        <!-- Results -->
        <table class="text-xs border-collapse border-2 border-black w-full mb-2">
            <tbody>{phi_row}{c_row}</tbody>
        </table>
        {_footer()}
    </div>'''

    # --- PAGE 6: CHARTS ---
    page6 = f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Ensayo de Corte Directo', '(ASTM D3080)', pn+1, tp)}
        <!-- Summary -->
        <table class="text-xs border-collapse border-2 border-black w-full text-center mb-4">
            <tbody>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2 w-2/3 bg-gray-50">Ángulo deFricción Interna del suelo (°)</td><td class="p-1 font-bold text-lg">{phi}</td></tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2 bg-gray-50">Cohesión Aparente del Suelo (Kg/cm2)</td><td class="p-1 font-bold">{c}</td></tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-left pl-2 bg-gray-50">Densidad Seca Promedio (Yd&lt;N°4)</td><td class="p-1 font-bold">{gamma_d}</td></tr>
                <tr><td class="p-1 border-r border-black text-left pl-2 bg-gray-50">Humedad Natural (%)</td><td class="p-1 font-bold">{w_pct}</td></tr>
            </tbody>
        </table>
        <!-- Stress-Strain Chart -->
        <div class="border-2 border-black mb-3 bg-white" style="height:280px;">
            <div class="text-xs text-center font-bold bg-gray-200 py-1 border-b border-black">DIAGRAMA ESFUERZO - DEFORMACION</div>
            <canvas id="shearCurveChart"></canvas>
        </div>
        <!-- Mohr-Coulomb Chart -->
        <div class="border-2 border-black bg-white" style="height:280px;">
            <div class="text-xs text-center font-bold bg-gray-200 py-1 border-b border-black">DIAGRAMA ESF. CORTANTE - ESF. NORMAL</div>
            <canvas id="shearMohrChart"></canvas>
        </div>
        {_methodology_box(
            norma='ASTM D3080 / NTP 339.171',
            nivel='Derivado',
            origen=f'Cartilla GEOCENTER v2 para {p.get("sucs", "SM")} — parámetros objetivo (φ, c) generados por ingeniería inversa a partir de la clasificación SUCS',
            procedimiento=f'Se ensayaron {n_spec} especímenes bajo esfuerzos normales crecientes. Envolvente de falla por regresión lineal de pares (σ, τ)',
            formula='τ = c + σ·tan(φ), donde τ = esfuerzo cortante, σ = esfuerzo normal, c = cohesión, φ = ángulo de fricción',
            resultado=f'φ = {phi}°, c = {c} kg/cm²',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('φ', phi, 'phi', '°'), ('c', c, 'cohesion', ' kg/cm²')]
        )}
        {_footer()}
    </div>'''

    return page5 + page6


def _page_proctor(p, proctor, pn, tp):
    r = proctor.get('results', proctor)
    mdd = r.get('mdd', 0)
    omc = r.get('omc', 0)
    method = r.get('method', 'Proctor Modificado')
    energy = r.get('energy', '56000 lb-ft/ft³')
    mold_volume = r.get('mold_volume_cm3', 944)
    mold_weight = r.get('mold_weight_g', 4180)
    layers = r.get('layers', 5)
    blows = r.get('blows_per_layer', 25)
    gs = r.get('gs', 2.65)
    points = r.get('points', r.get('compaction_points', []))

    # Detailed point rows
    pts_rows = ''
    for i, pt in enumerate(points):
        w = pt.get('moisture_percent', pt.get('w', 0))
        dd = pt.get('dry_density', pt.get('dd', 0))
        wm = pt.get('wet_weight_mold', 0)
        wms = pt.get('wet_weight_soil', round(wm - mold_weight, 1) if wm else 0)
        vol = pt.get('volume_cm3', mold_volume)
        wet_density = round(wms / vol, 3) if vol > 0 and wms > 0 else pt.get('wet_density', 0)
        # Moisture containers
        tare_id = pt.get('tare_id', f'T-{i+1}')
        wet_tare = pt.get('wet_tare', 0)
        dry_tare = pt.get('dry_tare', 0)
        tare = pt.get('tare', 0)
        water = round(wet_tare - dry_tare, 2) if wet_tare and dry_tare else 0
        solids = round(dry_tare - tare, 2) if dry_tare and tare else 0

        pts_rows += f'''<tr class="border-b border-gray-300 text-center">
            <td class="p-1 border-r border-black font-bold">{i+1}</td>
            <td class="p-1 border-r border-black">{wm:.1f}</td>
            <td class="p-1 border-r border-black">{wms:.1f}</td>
            <td class="p-1 border-r border-black">{wet_density:.3f}</td>
            <td class="p-1 border-r border-black">{tare_id}</td>
            <td class="p-1 border-r border-black">{wet_tare:.2f}</td>
            <td class="p-1 border-r border-black">{dry_tare:.2f}</td>
            <td class="p-1 border-r border-black">{tare:.2f}</td>
            <td class="p-1 border-r border-black">{water:.2f}</td>
            <td class="p-1 border-r border-black">{solids:.2f}</td>
            <td class="p-1 border-r border-black bg-blue-50">{w:.2f}</td>
            <td class="p-1 bg-blue-50 font-bold">{dd:.3f}</td>
        </tr>'''

    # Zero air voids line (Gs)
    zav_note = f'Gs = {gs}' if gs else ''

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Ensayo de Compactación Proctor Modificado', '(ASTM D1557 / MTC E-115)', pn, tp)}

        <!-- Method Parameters -->
        <table class="text-[9px] border-collapse border-2 border-black w-full mb-2">
            <tr class="border-b border-gray-300">
                <td class="p-1 border-r border-black text-right w-1/4">Método</td>
                <td class="p-1 font-bold border-r border-black">{method}</td>
                <td class="p-1 border-r border-black text-right w-1/4">Energía de Compact.</td>
                <td class="p-1 font-bold">{energy}</td>
            </tr>
            <tr class="border-b border-gray-300">
                <td class="p-1 border-r border-black text-right">Volumen del molde</td>
                <td class="p-1 border-r border-black">{mold_volume} cm³</td>
                <td class="p-1 border-r border-black text-right">Peso del molde</td>
                <td class="p-1">{mold_weight} g</td>
            </tr>
            <tr class="border-b border-black">
                <td class="p-1 border-r border-black text-right">N° de Capas</td>
                <td class="p-1 border-r border-black">{layers}</td>
                <td class="p-1 border-r border-black text-right">Golpes por capa</td>
                <td class="p-1">{blows}</td>
            </tr>
        </table>

        <!-- Data Table -->
        <div class="section-title text-[10px]">DATOS DE COMPACTACIÓN</div>
        <table class="text-[8px] border-collapse border-2 border-black w-full text-center mb-2">
            <thead>
                <tr class="bg-gray-100 border-b-2 border-black font-bold">
                    <td class="p-1 border-r border-black" rowspan="2">Punto</td>
                    <td class="p-1 border-r border-black" colspan="3">MUESTRA + MOLDE</td>
                    <td class="p-1 border-r border-black" colspan="6">CONTENIDO DE HUMEDAD</td>
                    <td class="p-1 border-r border-black bg-blue-50">w</td>
                    <td class="p-1 bg-blue-50">γd</td>
                </tr>
                <tr class="bg-gray-50 border-b border-black text-[7px]">
                    <td class="p-1 border-r border-black">Wm+m<br>(g)</td>
                    <td class="p-1 border-r border-black">Wms<br>(g)</td>
                    <td class="p-1 border-r border-black">γh<br>(g/cm³)</td>
                    <td class="p-1 border-r border-black">Tarro</td>
                    <td class="p-1 border-r border-black">Wh+t<br>(g)</td>
                    <td class="p-1 border-r border-black">Ws+t<br>(g)</td>
                    <td class="p-1 border-r border-black">Wt<br>(g)</td>
                    <td class="p-1 border-r border-black">Ww<br>(g)</td>
                    <td class="p-1 border-r border-black">Ws<br>(g)</td>
                    <td class="p-1 border-r border-black bg-blue-50">(%)</td>
                    <td class="p-1 bg-blue-50">(g/cm³)</td>
                </tr>
            </thead>
            <tbody>{pts_rows}</tbody>
        </table>

        <!-- Results + Chart -->
        <div class="flex gap-4">
            <div class="w-2/5">
                <div class="border-2 border-black">
                    <table class="w-full text-[10px] font-bold">
                        <tr class="border-b border-black"><td class="bg-gray-100 p-2 border-r border-black">Máxima Densidad Seca (MDD)</td><td class="p-2 text-center bg-blue-50 text-lg">{mdd} g/cm³</td></tr>
                        <tr><td class="bg-gray-100 p-2 border-r border-black">Óptimo Cont. de Humedad (OCH)</td><td class="p-2 text-center bg-blue-50 text-lg">{omc} %</td></tr>
                    </table>
                </div>
                <div class="mt-2 text-[8px] text-gray-500 italic">{zav_note}</div>
            </div>
            <div class="w-3/5 border border-black h-[300px] bg-white relative">
                <div class="text-[9px] text-center font-bold pt-1">CURVA DE COMPACTACIÓN</div>
                <canvas id="proctorChart"></canvas>
            </div>
        </div>
        {_methodology_box(
            norma='ASTM D1557 / MTC E-115',
            nivel='Derivado',
            origen=f'Cartilla GEOCENTER v2 para {p.get("sucs", "SM")} — MDD y OMC objetivo generados por ingeniería inversa',
            procedimiento=f'Compactación en {layers} capas con {blows} golpes por capa. Se determinaron {len(points)} puntos de la curva de compactación',
            formula='γd = γw / (1 + w/100), donde γd = densidad seca, γw = densidad húmeda, w = contenido de humedad',
            resultado=f'MDD = {mdd} g/cm³, OMC = {omc}%',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('MDD', mdd, 'mdd', ' g/cm³'), ('OMC', omc, 'omc', '%')]
        )}
        {_footer()}
    </div>'''


def _page_cbr(p, cbr, pn, tp):
    """Generate CBR report page with table and chart."""
    r = cbr if isinstance(cbr, dict) else {}
    specimens = r.get('specimens', [])
    cbr_95 = r.get('cbr_95_mdd', '--')
    cbr_100 = r.get('cbr_100_mdd', '--')
    design_cbr = r.get('design_cbr', '--')
    mdd = r.get('proctor_mdd', '--')
    omc = r.get('proctor_omc', '--')
    
    # Build specimen summary rows
    spec_rows = ''
    for i, sp in enumerate(specimens):
        spec_rows += f'''<tr class="border-b border-gray-300">
            <td class="p-1 border-r border-black text-center font-bold">{sp.get('blows', 0)}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('dry_density', 0):.3f}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('moisture_pct', 0):.1f}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('compaction_pct', 0):.1f}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('swell_pct', 0):.2f}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('cbr_01', 0):.1f}</td>
            <td class="p-1 border-r border-black text-center">{sp.get('cbr_02', 0):.1f}</td>
            <td class="p-1 text-center font-bold bg-yellow-50">{sp.get('cbr_selected', 0):.1f}</td>
        </tr>'''
    
    # Build penetration-load rows for each specimen
    pen_header = ''.join(f'<td class="p-1 border-r border-black font-bold text-center">{sp.get("blows",0)} golpes</td>' for sp in specimens)
    pen_rows = ''
    penetrations = [0.64, 1.27, 1.91, 2.54, 3.81, 5.08, 7.62, 10.16, 12.70]
    pen_inches = [0.025, 0.050, 0.075, 0.100, 0.150, 0.200, 0.300, 0.400, 0.500]
    
    for j, (pen_mm, pen_in) in enumerate(zip(penetrations, pen_inches)):
        cells = ''
        for sp in specimens:
            loads = sp.get('corrected_loads', sp.get('loads_lbf', []))
            load = loads[j] if j < len(loads) else 0
            bg = ' bg-yellow-50 font-bold' if pen_mm in [2.54, 5.08] else ''
            cells += f'<td class="p-1 border-r border-black text-center{bg}">{load:.1f}</td>'
        bg_row = ' bg-yellow-50' if pen_mm in [2.54, 5.08] else ''
        pen_rows += f'''<tr class="border-b border-gray-200{bg_row}">
            <td class="p-1 border-r border-black text-center">{pen_mm:.2f}</td>
            <td class="p-1 border-r border-black text-center">{pen_in:.3f}</td>
            {cells}
        </tr>'''
    
    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Ensayo CBR (California Bearing Ratio)', '(NTP 339.145 / ASTM D1883)', pn, tp)}
        
        <!-- SPECIMEN SUMMARY TABLE -->
        <div class="text-[9px] font-bold text-center bg-gray-200 border border-black p-1 mb-1">RESUMEN DE ESPECÍMENES</div>
        <table class="text-[9px] border-collapse border-2 border-black w-full text-center mb-3">
            <thead class="bg-gray-100 font-bold">
                <tr class="border-b-2 border-black">
                    <td class="p-1 border-r border-black">Golpes/capa</td>
                    <td class="p-1 border-r border-black">γd (g/cm³)</td>
                    <td class="p-1 border-r border-black">w (%)</td>
                    <td class="p-1 border-r border-black">Compactación (%)</td>
                    <td class="p-1 border-r border-black">Expansión (%)</td>
                    <td class="p-1 border-r border-black">CBR@0.1"</td>
                    <td class="p-1 border-r border-black">CBR@0.2"</td>
                    <td class="p-1 bg-yellow-100">CBR (%)</td>
                </tr>
            </thead>
            <tbody>{spec_rows}</tbody>
        </table>
        
        <!-- PENETRATION-LOAD TABLE -->
        <div class="text-[9px] font-bold text-center bg-gray-200 border border-black p-1 mb-1">DATOS DE PENETRACIÓN</div>
        <table class="text-[9px] border-collapse border-2 border-black w-full text-center mb-3">
            <thead class="bg-gray-100 font-bold">
                <tr class="border-b-2 border-black">
                    <td class="p-1 border-r border-black">Penetración (mm)</td>
                    <td class="p-1 border-r border-black">Penetración (pulg)</td>
                    {pen_header}
                </tr>
            </thead>
            <tbody>{pen_rows}</tbody>
            <tfoot>
                <tr class="border-t-2 border-black bg-blue-50 font-bold">
                    <td colspan="2" class="p-1 border-r border-black text-right">Carga Patrón @ 0.1" (lbf):</td>
                    <td colspan="{len(specimens)}" class="p-1 text-center">3000</td>
                </tr>
                <tr class="bg-blue-50 font-bold border-b-2 border-black">
                    <td colspan="2" class="p-1 border-r border-black text-right">Carga Patrón @ 0.2" (lbf):</td>
                    <td colspan="{len(specimens)}" class="p-1 text-center">4500</td>
                </tr>
            </tfoot>
        </table>
        
        <!-- CHART -->
        <div class="flex gap-2 mb-2">
            <div class="w-7/12 border-2 border-black relative bg-white" style="height:200px;">
                <div class="text-[9px] font-bold text-center bg-gray-200 border-b border-black p-0.5">Curva Carga vs Penetración</div>
                <canvas id="printCBRChart"></canvas>
            </div>
            <div class="w-5/12">
                <div class="border-2 border-black mb-2">
                    <div class="text-[9px] font-bold text-center bg-gray-200 border-b border-black p-1">RESULTADOS CBR</div>
                    <table class="w-full text-xs">
                        <tr class="border-b border-gray-300"><td class="p-2 font-bold">MDD (Proctor):</td><td class="p-2 text-center">{mdd} g/cm³</td></tr>
                        <tr class="border-b border-gray-300"><td class="p-2 font-bold">OMC (Proctor):</td><td class="p-2 text-center">{omc} %</td></tr>
                        <tr class="border-b border-gray-300 bg-yellow-50"><td class="p-2 font-bold">CBR al 95% MDD:</td><td class="p-2 text-center font-bold text-lg">{cbr_95}%</td></tr>
                        <tr class="bg-yellow-50"><td class="p-2 font-bold">CBR al 100% MDD:</td><td class="p-2 text-center font-bold text-lg">{cbr_100}%</td></tr>
                    </table>
                </div>
                <div class="border-2 border-black bg-green-50">
                    <table class="w-full text-sm font-bold text-center">
                        <tr><td class="p-3">CBR de Diseño = {design_cbr}%</td></tr>
                    </table>
                </div>
            </div>
        </div>
        {_methodology_box(
            norma='NTP 339.145 / ASTM D1883',
            nivel='Derivado',
            origen=f'Correlación SUCS ({p.get("sucs", "SM")}) + Proctor Modificado (MDD={mdd}, OMC={omc}%)',
            procedimiento='3 especímenes compactados a 56, 25 y 10 golpes/capa. Saturación 96h. Penetración a 1.27 mm/min con pistón de 1.954"',
            formula='CBR (%) = (Carga ensayo / Carga patrón) × 100. Patrón: 3000 lbf @0.1", 4500 lbf @0.2"',
            resultado=f'CBR@95%MDD = {cbr_95}%, CBR@100%MDD = {cbr_100}%',
            sucs=p.get('sucs', 'SM'),
            param_checks=[]
        )}
        {_footer()}
    </div>'''


def _page_bearing(p, bc, pn, tp):
    r = bc if isinstance(bc, dict) else {}
    phi = r.get('phi', 0)
    c = r.get('c', 0)
    Nc = r.get('Nc', 0)
    Nq = r.get('Nq', 0)
    Ng = r.get('Ng', 0)
    B = r.get('B', 0)
    L = r.get('L', 1)
    Df = r.get('Df', 0)
    gamma = r.get('gamma', 0)
    FS = r.get('FS', 3)
    qu = r.get('qu_kgcm2', 0)
    qa = r.get('qa_kgcm2', 0)

    # Foundation parameters
    cg = r.get('cg', round(c * 2/3, 2))
    f_val = r.get('friction_angle', phi)
    fr = r.get('fr', round(phi * 2/3, 2) if phi else 0)
    beta = r.get('beta', 0)
    gamma_m = r.get('gamma_m', gamma)
    gamma_i = r.get('gamma_i', gamma)
    shape = r.get('foundation_shape', 'corrido')
    failure = r.get('failure_type', 'Corte General')
    method = r.get('method', 'Terzaghi')
    water_table = r.get('water_table', 'NO')

    # Multiple depth calculations
    depths = r.get('depths', [])
    if not depths:
        # Generate 4 depths from Df if not provided
        base_df = Df if Df > 0 else 1.0
        depths = [
            {'Df': base_df, 'B': B, 'Nc': Nc, 'Nq': Nq, 'Ng': Ng, 'qu': qu, 'qa': qa},
            {'Df': round(base_df + 0.5, 2), 'B': B, 'Nc': Nc, 'Nq': Nq, 'Ng': Ng, 'qu': r.get('qu2', qu), 'qa': r.get('qa2', qa)},
            {'Df': round(base_df + 1.0, 2), 'B': B, 'Nc': Nc, 'Nq': Nq, 'Ng': Ng, 'qu': r.get('qu3', qu), 'qa': r.get('qa3', qa)},
            {'Df': round(base_df + 1.5, 2), 'B': B, 'Nc': Nc, 'Nq': Nq, 'Ng': Ng, 'qu': r.get('qu4', qu), 'qa': r.get('qa4', qa)},
        ]

    # Depth rows for factor table
    depth_rows = ''
    for i, d in enumerate(depths[:4]):
        depth_rows += f'''<tr class="border-b border-gray-300">
            <td class="p-1 border-r border-black font-bold">D<sub>f({i+1})</sub></td>
            <td class="p-1 border-r border-black">{d.get('Nc', Nc):.2f}</td>
            <td class="p-1 border-r border-black">{d.get('Nq', Nq):.2f}</td>
            <td class="p-1 border-r border-black">{d.get('Ng', Ng):.2f}</td>
            <td class="p-1 border-r border-black">{d.get('Df', 0):.2f}</td>
            <td class="p-1 border-r border-black">{d.get('B', B):.2f}</td>
            <td class="p-1 border-r border-black bg-blue-50 font-bold">{d.get('qu', 0):.2f}</td>
            <td class="p-1 border-r border-black bg-blue-50 font-bold">{d.get('qa', 0):.2f}</td>
        </tr>'''

    # Settlement rows
    settle = r.get('settlement_params', {})
    Es = settle.get('Es_kgcm2', settle.get('Es_tm2', 300))
    mu = settle.get('mu', 0.35)
    Si_max = settle.get('Si_max', r.get('settlement_cm', 2.50))

    settle_rows = ''
    for i, d in enumerate(depths[:4]):
        s_qa = d.get('qa', qa)
        s_df = d.get('Df', 0)
        s_if = settle.get('If', round(0.59, 2))
        s_settl = settle.get(f'settle_{i+1}', round(s_qa * B * 100 * (1 - mu**2) / Es * s_if, 2) if Es > 0 else 0)
        s_flex = settle.get(f'flex_{i+1}', 'Flexible')
        s_ok = 'OK!' if s_settl <= Si_max else 'EXCEDE'
        settle_rows += f'''<tr class="border-b border-gray-300">
            <td class="p-1 border-r border-black font-bold">D<sub>f({i+1})</sub></td>
            <td class="p-1 border-r border-black">{s_qa:.2f}</td>
            <td class="p-1 border-r border-black">{mu}</td>
            <td class="p-1 border-r border-black">{Es:.2f}</td>
            <td class="p-1 border-r border-black">{Si_max:.2f}</td>
            <td class="p-1 border-r border-black">{B:.2f}</td>
            <td class="p-1 border-r border-black">{L:.2f}</td>
            <td class="p-1 border-r border-black">{s_if}</td>
            <td class="p-1 border-r border-black bg-blue-50">{s_flex}</td>
            <td class="p-1 border-r border-black bg-blue-50 font-bold">{s_settl:.2f}</td>
            <td class="p-1 border-r border-black">{s_qa:.2f}</td>
            <td class="p-1 bg-green-50 font-bold">{s_ok}</td>
        </tr>'''

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Capacidad de Carga y Asentamientos - Cimentaciones', '(Terzaghi)', pn, tp)}
        <!-- Foundation Params -->
        <table class="text-[9px] border-collapse border-2 border-black w-full mb-2">
            <tbody>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-right w-1/2">Forma de la Cimentación</td><td class="p-1 font-bold" colspan="3">{shape}</td></tr>
                <tr class="border-b border-gray-300"><td class="p-1 border-r border-black text-right">Falla por Corte</td><td class="p-1 font-bold" colspan="3">{failure}</td></tr>
                <tr class="border-b border-black"><td class="p-1 border-r border-black text-right">Cálculo por Método de</td><td class="p-1 font-bold" colspan="3">*{method}</td></tr>
            </tbody>
        </table>

        <!-- POR RESISTENCIA -->
        <div class="section-title text-[10px]">POR RESISTENCIA</div>
        <div class="flex gap-2 mb-2">
            <table class="text-[9px] border-collapse border border-black w-1/2">
                <tr class="border-b"><td class="p-1 border-r text-right">Cohesión</td><td class="p-1 font-bold">C</td><td class="p-1">=</td><td class="p-1">{c}</td><td class="p-1">Kg/cm²</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Cohesión por falla general</td><td class="p-1 font-bold">Cg</td><td class="p-1">=</td><td class="p-1">{cg}</td><td class="p-1">Kg/cm²</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Ángulo de fricción</td><td class="p-1 font-bold">f</td><td class="p-1">=</td><td class="p-1">{phi}</td><td class="p-1">°</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Ángulo de fricción por falla general</td><td class="p-1 font-bold">fr</td><td class="p-1">=</td><td class="p-1">{fr}</td><td class="p-1">°</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Ángulo de inclinación de la carga</td><td class="p-1 font-bold">b</td><td class="p-1">=</td><td class="p-1">{beta}</td><td class="p-1">°</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Peso unitario del suelo sobre el nivel de fundación</td><td class="p-1 font-bold">γm</td><td class="p-1">=</td><td class="p-1">{gamma_m}</td><td class="p-1">g/cm³</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Peso unitario del suelo bajo el nivel de fundación</td><td class="p-1 font-bold">γi</td><td class="p-1">=</td><td class="p-1">{gamma_i}</td><td class="p-1">g/cm³</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Ancho de la cimentación</td><td class="p-1 font-bold">B</td><td class="p-1">=</td><td class="p-1">{B}</td><td class="p-1">m</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Largo de la cimentación</td><td class="p-1 font-bold">L</td><td class="p-1">=</td><td class="p-1">{L}</td><td class="p-1">m</td></tr>
                <tr class="border-b"><td class="p-1 border-r text-right">Factor de seguridad</td><td class="p-1 font-bold">FS</td><td class="p-1">=</td><td class="p-1" colspan="2">{FS}</td></tr>
            </table>
            <div class="w-1/2 text-[8px] text-center text-gray-400 italic flex items-center justify-center border border-gray-300">
                <div>Presencia de nivel freático: <strong>{water_table}</strong></div>
            </div>
        </div>

        <div class="text-[9px] font-bold mb-1">ECUACIÓN PARA LA LARGA ÚLTIMA (qu) = 1·c·Nc + 1·q·Nq + 0.5·γ·B·Nγ</div>
        <!-- Factor Table -->
        <table class="text-[9px] border-collapse border-2 border-black w-full text-center mb-2">
            <thead>
                <tr class="bg-gray-100 border-b border-black font-bold">
                    <td class="p-1 border-r border-black" rowspan="2">FACTOR DE CARGA</td>
                    <td class="p-1 border-r border-black">Nc</td>
                    <td class="p-1 border-r border-black">Nq</td>
                    <td class="p-1 border-r border-black">Ny</td>
                    <td class="p-1 border-r border-black">Profundidad</td>
                    <td class="p-1 border-r border-black">Ancho</td>
                    <td class="p-1 border-r border-black bg-blue-50">q<sub>ult</sub></td>
                    <td class="p-1 bg-blue-50">q<sub>adm</sub></td>
                </tr>
                <tr class="bg-gray-50 border-b-2 border-black text-[8px]">
                    <td class="p-1 border-r border-black"></td><td class="p-1 border-r border-black"></td><td class="p-1 border-r border-black"></td>
                    <td class="p-1 border-r border-black">Df (m)</td><td class="p-1 border-r border-black">(m)</td>
                    <td class="p-1 border-r border-black bg-blue-50">(k/cm²)</td><td class="p-1 bg-blue-50">(k/cm²)</td>
                </tr>
            </thead>
            <tbody>{depth_rows}</tbody>
        </table>

        <!-- POR ASENTAMIENTO -->
        <div class="section-title text-[10px]">POR ASENTAMIENTO</div>
        <table class="text-[8px] border-collapse border-2 border-black w-full text-center mb-2">
            <thead>
                <tr class="bg-gray-100 border-b-2 border-black font-bold">
                    <td class="p-1 border-r border-black" rowspan="2"></td>
                    <td class="p-1 border-r border-black">Capacidad<br>admisible de<br>carga</td>
                    <td class="p-1 border-r border-black">Relación de<br>Poisson</td>
                    <td class="p-1 border-r border-black">Módulo de<br>Elasticidad</td>
                    <td class="p-1 border-r border-black">Asentamiento<br>permisible</td>
                    <td class="p-1 border-r border-black">Ancho ciment.</td>
                    <td class="p-1 border-r border-black">Largo<br>ciment.</td>
                    <td class="p-1 border-r border-black">Factor de<br>profundidad</td>
                    <td class="p-1 border-r border-black">Asentamiento<br>para la<br>cimentación</td>
                    <td class="p-1 border-r border-black">Asentamiento<br>asumida por<br>asentamiento</td>
                    <td class="p-1 border-r border-black">Presión de carga<br>asumida por<br>asentamiento</td>
                    <td class="p-1">Asentamiento<br>para la<br>cimentación</td>
                </tr>
                <tr class="bg-gray-50 border-b-2 border-black text-[7px]">
                    <td class="p-1 border-r border-black">q<sub>adm</sub><br>Kg/cm²</td>
                    <td class="p-1 border-r border-black">m</td>
                    <td class="p-1 border-r border-black">Kg/cm²</td>
                    <td class="p-1 border-r border-black">S<sub>i(max)</sub><br>cm</td>
                    <td class="p-1 border-r border-black">B<br>m</td>
                    <td class="p-1 border-r border-black">L<br>m</td>
                    <td class="p-1 border-r border-black">I<sub>f</sub><br>m/m</td>
                    <td class="p-1 border-r border-black">Flexible</td>
                    <td class="p-1 border-r border-black">cm</td>
                    <td class="p-1 border-r border-black">q<sub>adm</sub><br>Kg/cm²</td>
                    <td class="p-1">Flexible</td>
                </tr>
            </thead>
            <tbody>{settle_rows}</tbody>
        </table>
        {_methodology_box(
            norma='Terzaghi (1943) / NTP CE.050',
            nivel='Calculado',
            origen=f'Calculado a partir de phi={phi} y c={c} kg/cm2 (Corte Directo) + gamma={gamma} g/cm3 (Proctor)',
            procedimiento=f'Aplicacion de teoria de Terzaghi para cimentacion {shape} (B={B}m, Df={Df}m, FS={FS})',
            formula=f'qu = c*Nc + q*Nq + 0.5*gamma*B*Ng, donde Nc={Nc:.1f}, Nq={Nq:.1f}, Ng={Ng:.1f}',
            resultado=f'qu = {qu} kg/cm2, qa = {qa} kg/cm2 (FS={FS})',
            sucs=p.get('sucs', 'SM'),
            param_checks=[('qa', qa, 'qa_range', ' kg/cm2')]
        )}
        {_footer()}
    </div>'''


def _page_meyerhof(p, meyerhof, terzaghi, pn, tp):
    """Meyerhof page kept for backward compatibility but now only shows comparison."""
    r = meyerhof if isinstance(meyerhof, dict) else {}
    t = terzaghi if isinstance(terzaghi, dict) else {}
    qu = r.get('qu_kgcm2', 0)
    qa = r.get('qa_kgcm2', 0)
    phi = r.get('phi', 0)
    c = r.get('c', 0)
    Nc = r.get('Nc', 0)
    Nq = r.get('Nq', 0)
    Ng = r.get('Ng', 0)
    B = r.get('B', 0)
    Df = r.get('Df', 0)
    gamma = r.get('gamma', 0)
    FS = r.get('FS', 3)
    sf = r.get('shape_factors', {})
    df = r.get('depth_factors', {})
    settlement = r.get('settlement_cm', 0)
    sp = r.get('settlement_params', {})
    t_qu = t.get('qu_kgcm2', 0)
    t_qa = t.get('qa_kgcm2', 0)

    return f'''
    <div class="a4-page" style="page-break-before: always;">
        {_project_header(p, 'Capacidad Portante y Asentamiento', '(Meyerhof 1963 / Bowles)', pn, tp)}
        <div class="mb-3">
            <div class="section-title">PARÁMETROS DE ENTRADA</div>
            <table class="text-xs border border-black w-full">
                <tr><td class="bg-gray-100 p-2 border-r border-black w-1/2">Ángulo de Fricción (φ)</td><td class="p-2">{phi}°</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Cohesión (c)</td><td class="p-2 border-t border-black">{c} kg/cm²</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Peso Unitario (γ)</td><td class="p-2 border-t border-black">{gamma} t/m³</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Ancho Cimentación (B)</td><td class="p-2 border-t border-black">{B} m</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Profundidad (Df)</td><td class="p-2 border-t border-black">{Df} m</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Factor de Seguridad (FS)</td><td class="p-2 border-t border-black">{FS}</td></tr>
            </table>
        </div>
        <div class="flex gap-4 mb-3">
            <div class="w-1/2">
                <div class="section-title">FACTORES DE CAPACIDAD DE CARGA (MEYERHOF)</div>
                <table class="text-xs border border-black w-full text-center">
                    <tr class="bg-gray-100 font-bold border-b border-black">
                        <td class="p-2 border-r border-black">Nc</td><td class="p-2 border-r border-black">Nq</td><td class="p-2">Nγ</td>
                    </tr>
                    <tr><td class="p-2 border-r border-black">{Nc:.2f}</td><td class="p-2 border-r border-black">{Nq:.2f}</td><td class="p-2">{Ng:.2f}</td></tr>
                </table>
            </div>
            <div class="w-1/2">
                <div class="section-title">FACTORES DE FORMA Y PROFUNDIDAD</div>
                <table class="text-xs border border-black w-full text-center">
                    <tr class="bg-gray-100 font-bold border-b border-black">
                        <td class="p-1 border-r border-black">sc</td><td class="p-1 border-r border-black">sq</td><td class="p-1 border-r border-black">sγ</td>
                        <td class="p-1 border-r border-black">dc</td><td class="p-1 border-r border-black">dq</td><td class="p-1">dγ</td>
                    </tr>
                    <tr>
                        <td class="p-1 border-r border-black">{sf.get('sc', 0):.3f}</td><td class="p-1 border-r border-black">{sf.get('sq', 0):.3f}</td><td class="p-1 border-r border-black">{sf.get('sg', 0):.3f}</td>
                        <td class="p-1 border-r border-black">{df.get('dc', 0):.3f}</td><td class="p-1 border-r border-black">{df.get('dq', 0):.3f}</td><td class="p-1">{df.get('dg', 0):.3f}</td>
                    </tr>
                </table>
            </div>
        </div>
        <div class="border-2 border-black mb-4">
            <table class="w-full text-sm font-bold text-center">
                <tr><td class="bg-gray-100 p-3 border-r border-black w-1/2 border-b border-black">Capacidad de Carga Última (qu)</td><td class="p-3 border-b border-black">{qu} kg/cm²</td></tr>
                <tr><td class="bg-gray-100 p-3 border-r border-black">Capacidad de Carga Admisible (qa)</td><td class="p-3">{qa} kg/cm²</td></tr>
            </table>
        </div>
        <div class="mb-4">
            <div class="section-title">ASENTAMIENTO ELÁSTICO ESTIMADO (BOWLES)</div>
            <table class="text-xs border border-black w-full">
                <tr><td class="bg-gray-100 p-2 border-r border-black w-1/2">Módulo de Elasticidad (Es)</td><td class="p-2">{sp.get('Es_tm2', 0)} t/m²</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Relación de Poisson (μ)</td><td class="p-2 border-t border-black">{sp.get('mu', 0)}</td></tr>
                <tr><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Factor de Influencia (Is)</td><td class="p-2 border-t border-black">{sp.get('Is', 0)}</td></tr>
                <tr class="font-bold bg-yellow-50"><td class="bg-gray-100 p-2 border-r border-black border-t border-black">Asentamiento Estimado (Si)</td><td class="p-2 border-t border-black text-lg">{settlement} cm</td></tr>
            </table>
        </div>
        <div class="mb-4">
            <div class="section-title">CUADRO COMPARATIVO TERZAGHI vs MEYERHOF</div>
            <table class="text-xs border border-black w-full text-center font-bold">
                <tr class="bg-gray-100 border-b border-black">
                    <td class="p-2 border-r border-black w-1/3">Método</td><td class="p-2 border-r border-black">qu (kg/cm²)</td><td class="p-2">qa (kg/cm²)</td>
                </tr>
                <tr class="border-b border-gray-300"><td class="p-2 border-r border-black">Terzaghi (1943)</td><td class="p-2 border-r border-black">{t_qu}</td><td class="p-2">{t_qa}</td></tr>
                <tr><td class="p-2 border-r border-black">Meyerhof (1963)</td><td class="p-2 border-r border-black">{qu}</td><td class="p-2">{qa}</td></tr>
            </table>
        </div>
        {_footer()}
    </div>'''


def _chart_scripts(results):
    """Generate Chart.js scripts for all charts."""
    scripts = []
    
    # Granulometry chart
    gran = results.get('granulometry', {})
    gran_data = gran.get('data', gran.get('sieves', []))
    if gran_data:
        pts = [{'x': s.get('opening_mm', 0), 'y': s.get('percent_passing', 0)} for s in gran_data if s.get('opening_mm', 0) > 0]
        scripts.append(f'''
        const granPts = {json.dumps(pts)};
        const ctxG = document.getElementById('printGranChart');
        if(ctxG) {{ new Chart(ctxG, {{
            type:'scatter', data:{{datasets:[{{data:granPts,showLine:true,borderColor:'black',backgroundColor:'black',borderWidth:2,pointRadius:3,tension:0.4}}]}},
            options:{{animation:false,responsive:true,maintainAspectRatio:false,scales:{{x:{{type:'logarithmic',title:{{display:true,text:'ABERTURA (mm)'}},min:0.01,max:100}},y:{{min:0,max:100,title:{{display:true,text:'% QUE PASA'}}}}}},plugins:{{legend:{{display:false}}}} }} }}); }}''')
    
    # Limits charts
    limits = results.get('limits', {})
    r = limits.get('results', limits)
    ll_pts = r.get('ll_points', r.get('ll_data_raw', []))
    eq = r.get('equation', None)
    ll_val = r.get('LL', 0)
    if ll_pts:
        pts_data = [{'x': pt.get('blows', 0), 'y': pt.get('moisture', 0)} for pt in ll_pts]
        trend = '[]'
        if eq:
            slope, intercept = eq.get('slope', 0), eq.get('intercept', 0)
            y1 = slope * math.log(10) + intercept
            y2 = slope * math.log(100) + intercept
            trend = json.dumps([{'x': 10, 'y': round(y1, 2)}, {'x': 100, 'y': round(y2, 2)}])
        
        chart_code = f'''
        const llPts = {json.dumps(pts_data)};
        const llTrend = {trend};
        const llVal = {ll_val};
        ['printLimitsChart','page3LLChart'].forEach(id => {{
            const ctx = document.getElementById(id);
            if(ctx) {{ new Chart(ctx, {{
                type:'scatter', data:{{datasets:[
                    {{data:llPts,backgroundColor:'blue',borderColor:'blue',pointRadius:4}},
                    {{data:llTrend,showLine:true,borderColor:'black',borderWidth:2,pointRadius:0,borderDash:[5,5]}}
                ]}},
                options:{{animation:false,responsive:true,maintainAspectRatio:false,
                    scales:{{x:{{type:'logarithmic',min:10,max:100,title:{{display:true,text:'N° GOLPES'}}}},y:{{min:llVal-8,max:llVal+8,title:{{display:true,text:'HUMEDAD (%)'}}}}}},
                    plugins:{{legend:{{display:false}},annotation:{{annotations:{{l1:{{type:'line',xMin:25,xMax:25,yMin:0,yMax:llVal,borderColor:'red',borderWidth:1,borderDash:[5,5]}}}}}}}}
                }}
            }}); }}
        }});'''
        scripts.append(chart_code)
    
    # Shear charts
    shear = results.get('shear', {})
    sr = shear.get('results', shear)
    specimens = sr.get('specimens', shear.get('specimens', []))
    if specimens:
        mohr_pts = []
        curve_datasets = []
        colors = ['#e74c3c', '#3498db', '#2ecc71']
        for i, sp in enumerate(specimens):
            sigma = sp.get('normal_stress', 0)
            curve = sp.get('curve', [])
            tau_max = max((pt.get('shear_stress', 0) for pt in curve), default=sp.get('tau_max', 0))
            mohr_pts.append({'x': sigma, 'y': tau_max})
            if curve:
                curve_datasets.append({'label': f'σ={sigma}', 'data': [{'x': pt['strain_pct'], 'y': pt['shear_stress']} for pt in curve], 'color': colors[i % 3]})
        
        phi = sr.get('friction_angle', 0)
        c = sr.get('cohesion', 0)
        
        scripts.append(f'''
        const mohrPts = {json.dumps(mohr_pts)};
        const mohrLine = [{{x:0,y:{c}}},{{x:2,y:{c}+2*Math.tan({phi}*Math.PI/180)}}];
        const ctxM = document.getElementById('shearMohrChart');
        if(ctxM) {{ new Chart(ctxM, {{
            type:'scatter', data:{{datasets:[
                {{data:mohrPts,backgroundColor:'red',borderColor:'red',pointRadius:5,label:'Datos'}},
                {{data:mohrLine,showLine:true,borderColor:'black',borderWidth:2,pointRadius:0,label:'Envolvente'}}
            ]}},
            options:{{animation:false,responsive:true,maintainAspectRatio:false,scales:{{x:{{min:0,max:2,title:{{display:true,text:'σ (kg/cm²)'}}}},y:{{min:0,title:{{display:true,text:'τ (kg/cm²)'}}}}}},plugins:{{legend:{{display:false}}}}}}
        }}); }}''')
        
        if curve_datasets:
            ds_json = ','.join(f'{{data:{json.dumps(d["data"])},showLine:true,borderColor:"{d["color"]}",borderWidth:2,pointRadius:2,label:"{d["label"]}"}}' for d in curve_datasets)
            scripts.append(f'''
        const ctxC = document.getElementById('shearCurveChart');
        if(ctxC) {{ new Chart(ctxC, {{
            type:'scatter', data:{{datasets:[{ds_json}]}},
            options:{{animation:false,responsive:true,maintainAspectRatio:false,scales:{{x:{{title:{{display:true,text:'Deformación (%)'}}}},y:{{min:0,title:{{display:true,text:'τ (kg/cm²)'}}}}}},plugins:{{legend:{{position:'bottom',labels:{{font:{{size:9}}}}}}}}}}
        }}); }}''')
    
    # Proctor chart
    proctor = results.get('proctor', {})
    pr = proctor.get('results', proctor)
    pts = pr.get('points', pr.get('compaction_points', []))
    if pts:
        proctor_pts = [{'x': pt.get('moisture_percent', pt.get('w', 0)), 'y': pt.get('dry_density', pt.get('dd', 0))} for pt in pts]
        mdd = pr.get('mdd', 0)
        omc = pr.get('omc', 0)
        scripts.append(f'''
        const prPts = {json.dumps(proctor_pts)};
        const ctxP = document.getElementById('proctorChart');
        if(ctxP) {{ new Chart(ctxP, {{
            type:'scatter', data:{{datasets:[{{data:prPts,showLine:true,borderColor:'#2c3e50',backgroundColor:'#3498db',borderWidth:2,pointRadius:4,tension:0.4}}]}},
            options:{{animation:false,responsive:true,maintainAspectRatio:false,
                scales:{{x:{{title:{{display:true,text:'Humedad (%)'}}}},y:{{title:{{display:true,text:'Densidad Seca (g/cm³)'}}}}}},
                plugins:{{legend:{{display:false}},annotation:{{annotations:{{
                    vLine:{{type:'line',xMin:{omc},xMax:{omc},borderColor:'red',borderWidth:1,borderDash:[5,5],label:{{content:'OMC={omc}%',display:true}}}},
                    hLine:{{type:'line',yMin:{mdd},yMax:{mdd},borderColor:'blue',borderWidth:1,borderDash:[5,5],label:{{content:'MDD={mdd}',display:true}}}}
                }}}}}}
            }}
        }}); }}''')
    

    # CBR chart
    cbr = results.get('cbr', {})
    cbr_specs = cbr.get('specimens', [])
    if cbr_specs:
        cbr_datasets = []
        cbr_colors = ['#e74c3c', '#3498db', '#2ecc71']
        penetrations_cbr = [0.64, 1.27, 1.91, 2.54, 3.81, 5.08, 7.62, 10.16, 12.70]
        for i, sp in enumerate(cbr_specs):
            loads = sp.get('corrected_loads', sp.get('loads_lbf', []))
            pts_cbr = [{'x': pen, 'y': ld} for pen, ld in zip(penetrations_cbr, loads)]
            cbr_datasets.append({'data': pts_cbr, 'label': str(sp.get('blows', 0)) + ' golpes', 'color': cbr_colors[i % 3]})
        ds_cbr_json = ','.join(f'{{data:{json.dumps(d["data"])},showLine:true,borderColor:"{d["color"]}",borderWidth:2,pointRadius:3,label:"{d["label"]}",tension:0.3}}' for d in cbr_datasets)
        scripts.append(f''''
        const ctxCBR = document.getElementById('printCBRChart');
        if(ctxCBR) {{{{ new Chart(ctxCBR, {{{{
            type:'scatter', data:{{{{datasets:[{ds_cbr_json}]}}}},
            options:{{{{animation:false,responsive:true,maintainAspectRatio:false,
                scales:{{{{x:{{{{min:0,max:14,title:{{{{display:true,text:'Penetracion (mm)'}}}}}}}}}},y:{{{{min:0,title:{{{{display:true,text:'Carga (lbf)'}}}}}}}}}}}}}},
                plugins:{{{{legend:{{{{position:'bottom',labels:{{{{font:{{{{size:8}}}}}}}}}}}}}}}}}}
            }}}}
        }}}}); }}}}''')

    return '\n'.join(scripts)


def _wrap_html(pages, results):
    charts_js = _chart_scripts(results)
    pages_html = '\n'.join(pages)
    
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Ensayo - GEOCENTER LAB</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.1.0"></script>
    <style>
        body {{ font-family: 'Arial', sans-serif; font-size: 11px; -webkit-print-color-adjust: exact; }}
        @page {{ size: A4; margin: 1cm; }}
        .a4-page {{ width: 21cm; min-height: 29.7cm; margin: 0 auto; background: white; padding: 1cm; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        @media print {{ .no-print {{ display: none; }} .a4-page {{ box-shadow: none; padding: 0; }} body {{ background: white; }} }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid black; padding: 4px; }}
        .header-cell {{ background-color: #e5e7eb; font-weight: bold; text-align: center; }}
        .section-title {{ background-color: #1f2937; color: white; font-weight: bold; padding: 5px; text-transform: uppercase; margin-top: 10px; border: 1px solid black; text-align: center; }}
    </style>
</head>
<body class="bg-gray-100 p-8">
    <div class="fixed top-4 right-4 no-print flex gap-2">
        <button onclick="window.print()" class="bg-blue-600 text-white px-4 py-2 rounded shadow font-bold hover:bg-blue-700">🖨️ Imprimir / PDF</button>
    </div>
    {pages_html}
    <script>{charts_js}</script>
</body>
</html>'''
