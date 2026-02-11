"""
Stratigraphic Profile Generator
Generates visual column profiles for EMS reports.

Produces SVG/HTML representation of soil layers with SUCS patterns,
water table, and sample locations.
"""


# SUCS pattern colors (muted, professional)
SUCS_COLORS = {
    'GW': '#D4A574', 'GP': '#C8956E', 'GM': '#B8A088', 'GC': '#A89078',
    'SW': '#E8D4A0', 'SP': '#DCC890', 'SM': '#D0BC80', 'SC': '#C0A870',
    'ML': '#98B8A0', 'CL': '#88A890', 'OL': '#789878',
    'MH': '#80A898', 'CH': '#709888', 'OH': '#608878',
    'Pt': '#505050',
}

SUCS_PATTERNS = {
    'GW': 'dots-large', 'GP': 'dots-large', 'GM': 'dots-medium', 'GC': 'dots-cross',
    'SW': 'dots-small', 'SP': 'dots-small', 'SM': 'dots-fine', 'SC': 'dots-dash',
    'ML': 'lines-h', 'CL': 'lines-h-thick', 'OL': 'lines-h-dash',
    'MH': 'lines-h-wavy', 'CH': 'lines-h-double', 'OH': 'lines-h-wavy',
}

SUCS_DESCRIPTIONS = {
    'GW': 'Grava bien graduada', 'GP': 'Grava mal graduada',
    'GM': 'Grava limosa', 'GC': 'Grava arcillosa',
    'SW': 'Arena bien graduada', 'SP': 'Arena mal graduada',
    'SM': 'Arena limosa', 'SC': 'Arena arcillosa',
    'ML': 'Limo de baja plasticidad', 'CL': 'Arcilla de baja plasticidad',
    'OL': 'Orgánico de baja plasticidad',
    'MH': 'Limo de alta plasticidad', 'CH': 'Arcilla de alta plasticidad',
    'OH': 'Orgánico de alta plasticidad', 'Pt': 'Turba',
}


def _get_color(sucs):
    """Get fill color for a SUCS type."""
    for key in SUCS_COLORS:
        if sucs.startswith(key) or key in sucs:
            return SUCS_COLORS[key]
    return '#C0C0C0'


def _pattern_defs_svg():
    """Generate SVG pattern definitions for SUCS fill patterns."""
    return '''
    <defs>
        <!-- Gravel patterns (dots) -->
        <pattern id="pat-dots-large" width="12" height="12" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="2.5" fill="#00000020"/>
            <circle cx="9" cy="9" r="2.5" fill="#00000020"/>
        </pattern>
        <pattern id="pat-dots-medium" width="10" height="10" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="1.8" fill="#00000020"/>
            <circle cx="8" cy="8" r="1.8" fill="#00000020"/>
        </pattern>
        <pattern id="pat-dots-small" width="8" height="8" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.2" fill="#00000020"/>
            <circle cx="6" cy="6" r="1.2" fill="#00000020"/>
        </pattern>
        <pattern id="pat-dots-fine" width="6" height="6" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="0.8" fill="#00000020"/>
        </pattern>
        <pattern id="pat-dots-cross" width="10" height="10" patternUnits="userSpaceOnUse">
            <circle cx="3" cy="3" r="1.5" fill="#00000020"/>
            <line x1="7" y1="5" x2="9" y2="5" stroke="#00000020" stroke-width="1"/>
        </pattern>
        <pattern id="pat-dots-dash" width="8" height="8" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="4" r="1" fill="#00000020"/>
            <line x1="5" y1="4" x2="7" y2="4" stroke="#00000020" stroke-width="0.8"/>
        </pattern>
        <!-- Clay/Silt patterns (lines) -->
        <pattern id="pat-lines-h" width="20" height="6" patternUnits="userSpaceOnUse">
            <line x1="0" y1="3" x2="20" y2="3" stroke="#00000020" stroke-width="0.8"/>
        </pattern>
        <pattern id="pat-lines-h-thick" width="20" height="8" patternUnits="userSpaceOnUse">
            <line x1="0" y1="4" x2="20" y2="4" stroke="#00000025" stroke-width="1.2"/>
        </pattern>
        <pattern id="pat-lines-h-dash" width="20" height="6" patternUnits="userSpaceOnUse">
            <line x1="0" y1="3" x2="8" y2="3" stroke="#00000020" stroke-width="0.8"/>
            <line x1="12" y1="3" x2="20" y2="3" stroke="#00000020" stroke-width="0.8"/>
        </pattern>
        <pattern id="pat-lines-h-wavy" width="20" height="8" patternUnits="userSpaceOnUse">
            <path d="M0,4 Q5,2 10,4 Q15,6 20,4" fill="none" stroke="#00000020" stroke-width="0.8"/>
        </pattern>
        <pattern id="pat-lines-h-double" width="20" height="10" patternUnits="userSpaceOnUse">
            <line x1="0" y1="3" x2="20" y2="3" stroke="#00000025" stroke-width="1"/>
            <line x1="0" y1="7" x2="20" y2="7" stroke="#00000025" stroke-width="1"/>
        </pattern>
    </defs>'''


def generate_stratigraphic_profile(data):
    """
    Generate an SVG stratigraphic profile.
    
    Args:
        data: dict with:
            'calicata': str — e.g. 'C-01'
            'location': str — project location
            'layers': [
                {
                    'depth_from': 0.0,
                    'depth_to': 0.80,
                    'sucs': 'SM',
                    'description': 'Arena limosa, color marrón claro...',
                    'moisture_pct': 8.5,
                    'sample': 'Mab-01'  # optional
                },
                ...
            ],
            'water_table_depth': 2.50  # optional, None if not found
            'total_depth': 3.00
    
    Returns:
        dict with 'svg' (SVG string) and 'summary' table data
    """
    try:
        calicata = data.get('calicata', 'C-01')
        location = data.get('location', '')
        layers = data.get('layers', [])
        water_table = data.get('water_table_depth')
        total_depth = float(data.get('total_depth', 3.0))
        
        if not layers:
            return {'error': 'No layers provided'}
        
        # SVG dimensions
        margin_left = 60
        margin_right = 320
        margin_top = 60
        margin_bottom = 40
        col_width = 80
        scale = 120  # pixels per meter
        
        svg_height = margin_top + total_depth * scale + margin_bottom
        svg_width = margin_left + col_width + margin_right + 20
        
        parts = []
        parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" '
                     f'viewBox="0 0 {svg_width} {svg_height}" '
                     f'style="font-family: Arial, sans-serif; background: white;">')
        
        parts.append(_pattern_defs_svg())
        
        # Title
        parts.append(f'<text x="{svg_width/2}" y="20" text-anchor="middle" '
                     f'font-size="14" font-weight="bold" fill="#333">'
                     f'PERFIL ESTRATIGRÁFICO — {calicata}</text>')
        if location:
            parts.append(f'<text x="{svg_width/2}" y="38" text-anchor="middle" '
                         f'font-size="10" fill="#666">{location}</text>')
        
        # Depth scale (left axis)
        x_col = margin_left
        y_top = margin_top
        
        # Draw depth markers
        max_depth_int = int(total_depth) + 1
        for d in range(max_depth_int + 1):
            if d > total_depth:
                break
            y = y_top + d * scale
            parts.append(f'<line x1="{x_col-10}" y1="{y}" x2="{x_col}" y2="{y}" '
                         f'stroke="#333" stroke-width="1"/>')
            parts.append(f'<text x="{x_col-15}" y="{y+4}" text-anchor="end" '
                         f'font-size="10" fill="#333">{d:.1f}m</text>')
        
        # Draw 0.5m ticks
        d = 0.5
        while d < total_depth:
            y = y_top + d * scale
            parts.append(f'<line x1="{x_col-5}" y1="{y}" x2="{x_col}" y2="{y}" '
                         f'stroke="#999" stroke-width="0.5"/>')
            d += 1.0
        
        # Draw column border
        y_bottom = y_top + total_depth * scale
        parts.append(f'<rect x="{x_col}" y="{y_top}" width="{col_width}" '
                     f'height="{total_depth * scale}" fill="none" stroke="#333" stroke-width="1.5"/>')
        
        # Draw layers
        for i, layer in enumerate(layers):
            d_from = float(layer.get('depth_from', 0))
            d_to = float(layer.get('depth_to', total_depth))
            sucs = layer.get('sucs', 'ML')
            desc = layer.get('description', SUCS_DESCRIPTIONS.get(sucs, sucs))
            moisture = layer.get('moisture_pct')
            sample = layer.get('sample')
            
            y1 = y_top + d_from * scale
            y2 = y_top + d_to * scale
            h = y2 - y1
            
            color = _get_color(sucs)
            pattern_id = SUCS_PATTERNS.get(sucs, 'dots-fine')
            
            # Fill with color
            parts.append(f'<rect x="{x_col}" y="{y1}" width="{col_width}" height="{h}" '
                         f'fill="{color}" stroke="none"/>')
            
            # Overlay pattern
            parts.append(f'<rect x="{x_col}" y="{y1}" width="{col_width}" height="{h}" '
                         f'fill="url(#pat-{pattern_id})" stroke="none"/>')
            
            # Layer boundary line
            if i > 0:
                parts.append(f'<line x1="{x_col}" y1="{y1}" x2="{x_col + col_width}" y2="{y1}" '
                             f'stroke="#333" stroke-width="1" stroke-dasharray="4,2"/>')
            
            # SUCS label inside column
            y_mid = (y1 + y2) / 2
            parts.append(f'<text x="{x_col + col_width/2}" y="{y_mid + 4}" '
                         f'text-anchor="middle" font-size="11" font-weight="bold" '
                         f'fill="#333">{sucs}</text>')
            
            # Description to the right
            x_desc = x_col + col_width + 15
            # Truncate description for display
            desc_short = desc[:50] + '...' if len(desc) > 50 else desc
            parts.append(f'<text x="{x_desc}" y="{y_mid}" font-size="9" fill="#444">'
                         f'{desc_short}</text>')
            
            # Depth range
            parts.append(f'<text x="{x_desc}" y="{y_mid + 14}" font-size="8" fill="#888">'
                         f'{d_from:.2f} — {d_to:.2f} m</text>')
            
            # Moisture
            if moisture is not None:
                parts.append(f'<text x="{x_desc}" y="{y_mid + 26}" font-size="8" fill="#0077AA">'
                             f'w = {moisture:.1f}%</text>')
            
            # Sample marker
            if sample:
                y_sample = y_mid - 10
                parts.append(f'<line x1="{x_col - 5}" y1="{y_sample}" '
                             f'x2="{x_col + 10}" y2="{y_sample}" '
                             f'stroke="#CC0000" stroke-width="1.5"/>')
                parts.append(f'<circle cx="{x_col - 8}" cy="{y_sample}" r="3" '
                             f'fill="#CC0000"/>')
                parts.append(f'<text x="{x_col - 30}" y="{y_sample + 3}" '
                             f'text-anchor="end" font-size="8" fill="#CC0000" '
                             f'font-weight="bold">{sample}</text>')
        
        # Water table
        if water_table is not None and water_table <= total_depth:
            y_wt = y_top + water_table * scale
            # Dashed blue line
            parts.append(f'<line x1="{x_col - 20}" y1="{y_wt}" '
                         f'x2="{x_col + col_width + 5}" y2="{y_wt}" '
                         f'stroke="#0066CC" stroke-width="2" stroke-dasharray="6,3"/>')
            # Water symbol
            parts.append(f'<text x="{x_col + col_width + 10}" y="{y_wt + 4}" '
                         f'font-size="10" fill="#0066CC" font-weight="bold">'
                         f'▼ NF = {water_table:.2f}m</text>')
        
        # Legend
        y_legend = svg_height - 20
        parts.append(f'<text x="{margin_left}" y="{y_legend}" font-size="8" fill="#999">'
                     f'NTP 339.162 / ASTM D2488 — Clasificación visual-manual</text>')
        
        parts.append('</svg>')
        
        # Summary table
        summary = []
        for layer in layers:
            summary.append({
                'depth_from': layer.get('depth_from'),
                'depth_to': layer.get('depth_to'),
                'sucs': layer.get('sucs'),
                'description': layer.get('description', 
                    SUCS_DESCRIPTIONS.get(layer.get('sucs', ''), '')),
                'moisture_pct': layer.get('moisture_pct'),
                'sample': layer.get('sample'),
            })
        
        return {
            'success': True,
            'svg': '\n'.join(parts),
            'summary': summary,
            'total_depth': total_depth,
            'water_table': water_table,
            'calicata': calicata,
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
