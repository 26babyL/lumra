"""
Management command version — lebih mudah dijalankan

Cara pakai:
    python manage.py test_full_flow
    python manage.py test_full_flow --no-rollback
    python manage.py test_full_flow --quiet
"""

from django.core.management.base import BaseCommand
import os
import sys


class Command(BaseCommand):
    help = 'Jalankan test alur lengkap LUMRA ERP dari setup sampai penjualan'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--no-rollback',
            action='store_true',
            help='Jangan rollback data setelah test (simpan permanen)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Kurangi output detail'
        )
    
    def handle(self, *args, **options):
        # Load dan execute main script
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'test_full_flow.py')
        script_path = os.path.abspath(script_path)
        
        if not os.path.exists(script_path):
            self.stderr.write(f"Script tidak ditemukan: {script_path}")
            return
        
        with open(script_path, 'r') as f:
            code = f.read()
        
        # Override settings
        if options['no_rollback']:
            code = code.replace("USE_TRANSACTION = True", "USE_TRANSACTION = False")
        
        if options['quiet']:
            code = code.replace("PRINT_STOCK_AT_EACH_STEP = True", "PRINT_STOCK_AT_EACH_STEP = False")
        
        # Execute
        exec(code)