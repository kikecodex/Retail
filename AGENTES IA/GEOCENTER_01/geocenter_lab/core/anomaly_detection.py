"""
Anomaly Detection Module
Detects unusual or potentially erroneous soil test results

Checks for:
- Inconsistent parameter combinations
- Values outside physical limits
- Lab errors (negative values, etc.)
"""

def detect_anomalies(test_data):
    """
    Detect anomalies in soil test results
    
    Args:
        test_data: dict with keys for various test results:
            - granulometry: {p200, cu, cc}
            - limits: {LL, PL, PI}
            - shear: {phi, cohesion}
            - proctor: {mdd, omc}
            - classification: {sucs}
    
    Returns:
        list of anomaly dicts with 'type', 'severity', 'message', 'recommendation'
    """
    anomalies = []
    
    # Extract data safely
    limits = test_data.get('limits', {})
    shear = test_data.get('shear', {})
    proctor = test_data.get('proctor', {})
    gran = test_data.get('granulometry', {})
    
    ll = limits.get('LL', 0)
    pl = limits.get('PL', 0)
    pi = limits.get('PI', ll - pl if ll and pl else 0)
    
    phi = shear.get('phi', 0)
    cohesion = shear.get('cohesion', 0)
    
    mdd = proctor.get('mdd', 0)
    omc = proctor.get('omc', 0)
    
    p200 = gran.get('p200', 0)
    cu = gran.get('cu', 0)
    
    # ========== PHYSICAL LIMIT CHECKS ==========
    
    # 1. Negative PI
    if pi < 0:
        anomalies.append({
            'type': 'error',
            'severity': 'critical',
            'param': 'PI',
            'value': pi,
            'message': f'IP negativo ({pi:.1f}%) - Esto es físicamente imposible',
            'recommendation': 'Revisar ensayos de LL y LP. Posible error de laboratorio.'
        })
    
    # 2. PL > LL
    if pl > ll and ll > 0:
        anomalies.append({
            'type': 'error',
            'severity': 'critical',
            'param': 'PL>LL',
            'value': f'PL={pl}, LL={ll}',
            'message': f'Límite Plástico ({pl:.1f}%) mayor que Límite Líquido ({ll:.1f}%)',
            'recommendation': 'Verificar que no se intercambiaron los valores. Repetir ensayos.'
        })
    
    # 3. LL fuera de rango típico
    if ll > 150:
        anomalies.append({
            'type': 'warning',
            'severity': 'moderate',
            'param': 'LL',
            'value': ll,
            'message': f'LL muy alto ({ll:.1f}%) - Típico de arcillas muy plásticas o turbas',
            'recommendation': 'Verificar si es suelo orgánico (color, olor). Considerar clasificación PT.'
        })
    
    # 4. φ > 45° (muy raro excepto gravas angulares)
    if phi > 45:
        anomalies.append({
            'type': 'warning',
            'severity': 'moderate',
            'param': 'phi',
            'value': phi,
            'message': f'Ángulo de fricción muy alto (φ={phi:.1f}°)',
            'recommendation': 'Verificar calibración del equipo. Solo gravas angulares limpias alcanzan estos valores.'
        })
    
    # 5. Cohesión alta + φ alto (inusual)
    if cohesion > 0.3 and phi > 30:
        anomalies.append({
            'type': 'warning',
            'severity': 'moderate',
            'param': 'c+phi',
            'value': f'c={cohesion}, φ={phi}',
            'message': f'Cohesión alta ({cohesion:.2f} kg/cm²) con φ alto ({phi:.1f}°)',
            'recommendation': 'Combinación inusual. Revisar si la muestra estaba saturada o parcialmente cementada.'
        })
    
    # 6. Arena con cohesión alta
    if p200 < 12 and cohesion > 0.2:
        anomalies.append({
            'type': 'warning',
            'severity': 'moderate',
            'param': 'cohesion_sand',
            'value': cohesion,
            'message': f'Arena/grava limpia ({p200:.1f}% finos) con cohesión alta ({cohesion:.2f} kg/cm²)',
            'recommendation': 'Las arenas limpias típicamente tienen c≈0. Verificar contenido de finos real.'
        })
    
    # 7. MDD muy bajo (posible suelo orgánico)
    if mdd < 1.2 and mdd > 0:
        anomalies.append({
            'type': 'warning',
            'severity': 'moderate',
            'param': 'mdd',
            'value': mdd,
            'message': f'Densidad máxima muy baja (MDD={mdd:.2f} g/cm³)',
            'recommendation': 'Posible suelo orgánico o muy poroso. Verificar clasificación.'
        })
    
    # 8. OMC muy alto (posible suelo fino o orgánico)
    if omc > 40:
        anomalies.append({
            'type': 'warning',
            'severity': 'low',
            'param': 'omc',
            'value': omc,
            'message': f'Humedad óptima muy alta (OMC={omc:.1f}%)',
            'recommendation': 'Típico de arcillas muy plásticas o suelos orgánicos.'
        })
    
    # 9. Cu < 1 (físicamente imposible para suelos bien graduados)
    if cu > 0 and cu < 1:
        anomalies.append({
            'type': 'error',
            'severity': 'critical',
            'param': 'cu',
            'value': cu,
            'message': f'Coeficiente de uniformidad Cu={cu:.2f} < 1 (imposible)',
            'recommendation': 'Cu siempre debe ser ≥1. Revisar cálculos de D60 y D10.'
        })
    
    return anomalies


def get_anomaly_summary(anomalies):
    """Get a summary of anomaly detection results"""
    if not anomalies:
        return {
            'status': 'ok',
            'message': '✅ No se detectaron anomalías. Datos consistentes.',
            'critical_count': 0,
            'warning_count': 0
        }
    
    critical = [a for a in anomalies if a['severity'] == 'critical']
    warnings = [a for a in anomalies if a['severity'] in ['moderate', 'low']]
    
    if critical:
        return {
            'status': 'error',
            'message': f'❌ Se detectaron {len(critical)} errores críticos. Revisar antes de continuar.',
            'critical_count': len(critical),
            'warning_count': len(warnings)
        }
    else:
        return {
            'status': 'warning',
            'message': f'⚠️ Se detectaron {len(warnings)} advertencias. Revisar si es posible.',
            'critical_count': 0,
            'warning_count': len(warnings)
        }
