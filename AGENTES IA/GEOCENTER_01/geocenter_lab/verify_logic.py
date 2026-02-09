from core.granulometry import calculate_granulometry
import json

# Test Case from Excel Analysis (Row 24 onwards in Sheet 1)
# Total Weight (D17): Let's assume a standard value or what was in the file if specific
# From previous analysis, specific value wasn't hardcoded but formula refered to D17.
# Let's use a clear example from standard values seen in output dump (R26: 468.3 gr for 3/4")

test_input = {
    'total_dry_weight': 5000.0, # Example total
    'sieves': [
        {'size_label': '3"', 'opening_mm': 75.0, 'weight_retained': 0.0},
        {'size_label': '2"', 'opening_mm': 50.0, 'weight_retained': 0.0},
        {'size_label': '1 1/2"', 'opening_mm': 37.5, 'weight_retained': 0.0},
        {'size_label': '1"', 'opening_mm': 25.0, 'weight_retained': 200.0}, 
        {'size_label': '3/4"', 'opening_mm': 19.0, 'weight_retained': 468.3},
        {'size_label': '3/8"', 'opening_mm': 9.5, 'weight_retained': 342.1},
        {'size_label': '# 4', 'opening_mm': 4.75, 'weight_retained': 245.1}
    ]
}

print("Running Verification Calculation...")
result = calculate_granulometry(test_input)

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print("\n--- RESULTS ---")
    print(f"{'TAMIZ':<10} | {'RET(gr)':<10} | {'% PASA':<10}")
    print("-" * 35)
    for r in result['data']:
        print(f"{r['size_label']:<10} | {r['weight_retained']:<10} | {r['percent_passing']:<10}")
    print("\nVerification Complete.")
