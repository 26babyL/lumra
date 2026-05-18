"""
Django management command for full flow test with Gemini AI
Usage: python manage.py test_with_gemini
"""

from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
import sys
import os

class Command(BaseCommand):
    help = 'Run LUMRA ERP full flow test dengan Gemini AI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--use-gemini',
            action='store_true',
            default=True,
            help='Use Gemini AI for data generation'
        )
        parser.add_argument(
            '--keep-data',
            action='store_true',
            default=True,
            help='Keep generated data (don\'t rollback)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n[OK] Starting LUMRA ERP Full Flow Test with Gemini AI\n'))
        
        try:
            # Import test module
            from lumra_config.management.commands.test_setup_with_gemini import run_full_flow_test_with_gemini
            
            # Run test
            run_full_flow_test_with_gemini()
            
            self.stdout.write(self.style.SUCCESS('\n[OK] Test completed successfully!\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] Test failed: {e}\n'))
            import traceback
            traceback.print_exc()
            sys.exit(1)
