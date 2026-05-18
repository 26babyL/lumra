#!/usr/bin/env python
"""
Simple test runner - makes sure Django is set up before running test
"""
import os
import sys
import django

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_config.settings')
django.setup()

# Now run the test
print("\n" + "="*70)
print(" LUMRA ERP — FULL FLOW TEST DENGAN GEMINI AI")
print("="*70 + "\n")

try:
    # Import at module level after Django setup
    from lumra_config.management.commands.test_setup_with_gemini import run_full_flow_test_with_gemini
    
    # Run the test
    run_full_flow_test_with_gemini()
    
except Exception as e:
    print(f"\n❌ TEST ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
