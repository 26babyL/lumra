#!/usr/bin/env python
"""
QUICK TEST RUNNER — Test setup dengan Gemini AI
Bisa dijalankan langsung: python test_runner.py
"""

import os
import sys
import django

# Tambah project root ke path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumra_config.settings')

# Setup Django FIRST
django.setup()

# KONFIGURASI (Edit di sini untuk quick change)
CONFIG = {
    'USE_TRANSACTION': False,      # False = keep data, True = rollback
    'USE_GEMINI': True,            # True = AI data, False = hardcoded
    'PRINT_STOCK_AT_EACH_STEP': True,
    'VERBOSE': True,
}

def main():
    """Main test runner"""
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║   LUMRA ERP — FULL FLOW TEST DENGAN GEMINI AI              ║
    ╚════════════════════════════════════════════════════════════╝
    
    KONFIGURASI SAAT INI:
    ├─ Transaction: {'ON (rollback)' if CONFIG['USE_TRANSACTION'] else 'OFF (keep data)'}
    ├─ Gemini AI: {'ACTIVE' if CONFIG['USE_GEMINI'] else 'INACTIVE (hardcoded)'}
    ├─ Stock Print: {'ON' if CONFIG['PRINT_STOCK_AT_EACH_STEP'] else 'OFF'}
    └─ Verbose: {'ON' if CONFIG['VERBOSE'] else 'OFF'}
    
    """)
    
    # Import dan jalankan test
    try:
        from lumra_config.management.commands.test_setup_with_gemini import (
            run_full_flow_test_with_gemini
        )
        
        # Override global settings
        import lumra_config.management.commands.test_setup_with_gemini as test_module
        test_module.USE_TRANSACTION = CONFIG['USE_TRANSACTION']
        test_module.USE_GEMINI = CONFIG['USE_GEMINI']
        test_module.PRINT_STOCK_AT_EACH_STEP = CONFIG['PRINT_STOCK_AT_EACH_STEP']
        
        # Run test
        run_full_flow_test_with_gemini()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
